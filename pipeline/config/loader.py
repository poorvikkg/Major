"""
loader.py
---------
Purpose : Load pipeline_config.json and expose typed, immutable dataclasses.
          All pipeline components import from here instead of hardcoding values.
Inputs  : pipeline_config.json (relative to this file's directory).
Outputs : Singleton PipelineConfig via get_config().
Raises  : FileNotFoundError if config file is missing.
"""

import json
import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG_PATH = Path(__file__).parent / "pipeline_config.json"


# ---------------------------------------------------------------------------
# Typed sub-config dataclasses (all frozen = immutable after load)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DetectorConfig:
    model_path:           str
    conf_threshold:       float
    nms_threshold:        float
    input_size:           Tuple[int, int]
    intra_op_num_threads: int


@dataclass(frozen=True)
class RecognizerConfig:
    model_path:           str
    embedding_dim:        int
    batch_size:           int
    intra_op_num_threads: int


@dataclass(frozen=True)
class TrackerConfig:
    max_age:          int
    min_hits:         int
    iou_threshold:    float
    high_conf_thresh: float
    low_conf_thresh:  float


@dataclass(frozen=True)
class InferenceConfig:
    recognition_threshold: float
    faiss_top_k:           int


@dataclass(frozen=True)
class StreamConfig:
    frame_skip:           int
    reconnect_delay_sec:  float
    max_reconnect_tries:  int
    frame_buffer_size:    int
    fps_cap:              int


@dataclass(frozen=True)
class VideoConfig:
    frame_interval:       int
    dedup_window_frames:  int
    supported_extensions: List[str]


@dataclass(frozen=True)
class NotificationConfig:
    cooldown_seconds:   int
    save_frames:        bool
    include_frame_b64:  bool
    frame_quality_jpeg: int


@dataclass(frozen=True)
class FAISSConfig:
    index_dir:        str
    embedding_dim:    int
    search_threshold: float


@dataclass(frozen=True)
class EmbeddingConfig:
    store_dir:        str
    embedding_dim:    int
    min_valid_images: int


@dataclass(frozen=True)
class PathsConfig:
    registered_faces_dir: str
    uploads_images_dir:   str
    uploads_videos_dir:   str
    uploads_temp_dir:     str


@dataclass(frozen=True)
class BackendConfig:
    url:         str
    socket_url:  str
    api_key:     str
    timeout_sec: int
    max_retries: int


@dataclass(frozen=True)
class PipelineConfig:
    detector:     DetectorConfig
    recognizer:   RecognizerConfig
    tracker:      TrackerConfig
    inference:    InferenceConfig
    stream:       StreamConfig
    video:        VideoConfig
    notification: NotificationConfig
    faiss:        FAISSConfig
    embeddings:   EmbeddingConfig
    paths:        PathsConfig
    backend:      BackendConfig


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_config(config_path: Optional[str] = None) -> PipelineConfig:
    """
    Return the singleton PipelineConfig (cached after first call).

    Purpose : Parse pipeline_config.json into typed dataclasses.
    Inputs  : config_path — optional override; defaults to pipeline_config.json
              next to this file.
    Outputs : Immutable PipelineConfig.
    Raises  : FileNotFoundError — config file not found.
              KeyError          — required key missing in JSON.
    """
    path = Path(config_path) if config_path else _DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Pipeline config not found: {path}. "
            "Ensure pipeline_config.json is present in pipeline/config/."
        )
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    cfg = _build(raw)
    logger.info("PipelineConfig loaded from %s.", path)
    return cfg


def reload_config(config_path: Optional[str] = None) -> PipelineConfig:
    """
    Force a config reload by clearing the LRU cache.

    Purpose : Hot-reload support for long-running processes.
    Inputs  : config_path — optional override path.
    Outputs : Fresh PipelineConfig.
    """
    get_config.cache_clear()
    return get_config(config_path)


# ---------------------------------------------------------------------------
# Private deserialization
# ---------------------------------------------------------------------------

def _build(raw: dict) -> PipelineConfig:
    """
    Deserialize raw JSON dict into PipelineConfig.

    Purpose : Map JSON keys to dataclass instances with type coercion.
    Inputs  : raw — dict loaded from JSON.
    Outputs : PipelineConfig.
    Raises  : KeyError if any required section or key is absent.
    """
    d, r, t  = raw["detector"], raw["recognizer"], raw["tracker"]
    i, s, v  = raw["inference"], raw["stream"],    raw["video"]
    n, fa    = raw["notification"], raw["faiss"]
    em, p, b = raw["embeddings"],   raw["paths"],  raw["backend"]

    return PipelineConfig(
        detector=DetectorConfig(
            model_path=d["model_path"],
            conf_threshold=float(d["conf_threshold"]),
            nms_threshold=float(d["nms_threshold"]),
            input_size=(int(d["input_size"][0]), int(d["input_size"][1])),
            intra_op_num_threads=int(d["intra_op_num_threads"]),
        ),
        recognizer=RecognizerConfig(
            model_path=r["model_path"],
            embedding_dim=int(r["embedding_dim"]),
            batch_size=int(r["batch_size"]),
            intra_op_num_threads=int(r["intra_op_num_threads"]),
        ),
        tracker=TrackerConfig(
            max_age=int(t["max_age"]),
            min_hits=int(t["min_hits"]),
            iou_threshold=float(t["iou_threshold"]),
            high_conf_thresh=float(t["high_conf_thresh"]),
            low_conf_thresh=float(t["low_conf_thresh"]),
        ),
        inference=InferenceConfig(
            recognition_threshold=float(i["recognition_threshold"]),
            faiss_top_k=int(i["faiss_top_k"]),
        ),
        stream=StreamConfig(
            frame_skip=int(s["frame_skip"]),
            reconnect_delay_sec=float(s["reconnect_delay_sec"]),
            max_reconnect_tries=int(s["max_reconnect_tries"]),
            frame_buffer_size=int(s["frame_buffer_size"]),
            fps_cap=int(s["fps_cap"]),
        ),
        video=VideoConfig(
            frame_interval=int(v["frame_interval"]),
            dedup_window_frames=int(v["dedup_window_frames"]),
            supported_extensions=list(v["supported_extensions"]),
        ),
        notification=NotificationConfig(
            cooldown_seconds=int(n["cooldown_seconds"]),
            save_frames=bool(n["save_frames"]),
            include_frame_b64=bool(n["include_frame_b64"]),
            frame_quality_jpeg=int(n["frame_quality_jpeg"]),
        ),
        faiss=FAISSConfig(
            index_dir=fa["index_dir"],
            embedding_dim=int(fa["embedding_dim"]),
            search_threshold=float(fa["search_threshold"]),
        ),
        embeddings=EmbeddingConfig(
            store_dir=em["store_dir"],
            embedding_dim=int(em["embedding_dim"]),
            min_valid_images=int(em["min_valid_images"]),
        ),
        paths=PathsConfig(
            registered_faces_dir=p["registered_faces_dir"],
            uploads_images_dir=p["uploads_images_dir"],
            uploads_videos_dir=p["uploads_videos_dir"],
            uploads_temp_dir=p["uploads_temp_dir"],
        ),
        backend=BackendConfig(
            url=b["url"],
            socket_url=b["socket_url"],
            api_key=b.get("api_key", ""),
            timeout_sec=int(b["timeout_sec"]),
            max_retries=int(b["max_retries"]),
        ),
    )
