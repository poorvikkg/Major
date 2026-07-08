"""
recognizer.py
-------------
Purpose  : ArcFace R100 ONNX inference wrapper.
Inputs   : 112x112 normalized tensors, ONNX model path.
Outputs  : Raw (un-normalized) 512-d embeddings.
Raises   : FileNotFoundError on missing ONNX model.

Single Responsibility: Manage the ONNX session and run forward passes.
Preprocessing, batching, and normalization are delegated.
"""

import logging
import time
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import onnxruntime as ort

logger = logging.getLogger(__name__)

# Expected output geometry
_EMBEDDING_DIM: int = 512


class FaceRecognizer:
    """
    ArcFace R100 ONNX inference wrapper.
    """

    def __init__(
        self,
        model_path: str,
        session: Optional[ort.InferenceSession] = None,
    ) -> None:
        self.model_path = Path(model_path)
        self._session   = session
        self._input_name:  Optional[str] = None
        self._output_name: Optional[str] = None

        if self._session is None:
            self._session = self._build_session()

        self._input_name  = self._session.get_inputs()[0].name
        self._output_name = self._session.get_outputs()[0].name
        self._validate_model_io()

        logger.info(
            "FaceRecognizer ready | model=%s | providers=%s",
            self.model_path.name,
            self._session.get_providers(),
        )

    def run_inference(self, blob: np.ndarray) -> np.ndarray:
        """
        Forward pass through ArcFace.

        Parameters
        ----------
        blob : (N, 3, 112, 112) float32 NCHW tensor.

        Returns
        -------
        (N, 512) float32 raw (un-normalized) embeddings.
        """
        t0 = time.perf_counter()
        outputs = self._session.run([self._output_name], {self._input_name: blob})
        t1 = time.perf_counter()
        logger.debug("ArcFace run_inference (batch_size=%d) completed in %.1f ms", blob.shape[0], (t1 - t0) * 1000)
        return outputs[0]   # (N, 512)

    def _build_session(self) -> ort.InferenceSession:
        if not self.model_path.exists():
            raise FileNotFoundError(f"ArcFace model not found at: {self.model_path}")

        providers = self._resolve_providers()
        logger.info(
            "Loading ArcFace model from %s with providers: %s",
            self.model_path,
            providers,
        )
        opts = ort.SessionOptions()
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        opts.intra_op_num_threads = 4

        try:
            session = ort.InferenceSession(
                str(self.model_path),
                sess_options=opts,
                providers=providers,
            )
        except Exception as exc:
            if "CUDAExecutionProvider" in str(providers):
                logger.warning(
                    "CUDA provider failed (%s) — falling back to CPU.", exc
                )
                session = ort.InferenceSession(
                    str(self.model_path),
                    sess_options=opts,
                    providers=["CPUExecutionProvider"],
                )
            else:
                raise

        return session

    @staticmethod
    def _resolve_providers() -> List[str]:
        available = ort.get_available_providers()
        logger.debug("Available ORT providers: %s", available)
        preferred = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        return [p for p in preferred if p in available] or ["CPUExecutionProvider"]

    def _validate_model_io(self) -> None:
        inputs  = self._session.get_inputs()
        outputs = self._session.get_outputs()

        if len(inputs) < 1:
            raise RuntimeError("ArcFace model has no input nodes.")
        if len(outputs) < 1:
            raise RuntimeError("ArcFace model has no output nodes.")

        in_shape  = inputs[0].shape
        out_shape = outputs[0].shape

        logger.debug("ArcFace input shape: %s  output shape: %s", in_shape, out_shape)

        if len(out_shape) >= 2 and isinstance(out_shape[-1], int):
            if out_shape[-1] != _EMBEDDING_DIM:
                logger.warning(
                    "Expected embedding dim %d, model reports %d.",
                    _EMBEDDING_DIM,
                    out_shape[-1],
                )
