"""
kalman_filter.py
----------------
Purpose  : Constant-velocity Kalman filter for a 4D bounding box.
Inputs   : Initial bounding box [x1, y1, x2, y2] at construction.
           Subsequent measurements via update().
Outputs  : Predicted bounding box from predict().
Raises   : N/A — pure numerical computation.

Single Responsibility: Kalman math ONLY.
No tracking lifecycle, no IoU, no detection logic lives here.

State vector: [x1, y1, x2, y2, vx, vy, vw, vh]  (8 dimensions)
Avoids external filterpy / scipy dependencies.
"""

import numpy as np


class KalmanBoxTracker:
    """
    Minimal constant-velocity Kalman filter for bounding box state.

    Parameters
    ----------
    box : (4,) float32 initial bounding box [x1, y1, x2, y2].
    """

    _STATE_DIM = 8   # [pos(4) | vel(4)]
    _MEAS_DIM  = 4   # [x1, y1, x2, y2]
    _DT        = 1.0 # time step (frames)

    def __init__(self, box: np.ndarray) -> None:
        n, m = self._STATE_DIM, self._MEAS_DIM

        # State vector
        self._x = np.zeros((n, 1), dtype=np.float64)
        self._x[:m, 0] = box.astype(np.float64)

        # State transition matrix  F: x_{t+1} = F @ x_t
        self._F = np.eye(n, dtype=np.float64)
        for k in range(m):
            self._F[k, k + m] = self._DT

        # Measurement matrix  H: z = H @ x
        self._H = np.zeros((m, n), dtype=np.float64)
        self._H[:m, :m] = np.eye(m)

        # Covariance matrices
        self._P = np.eye(n, dtype=np.float64) * 10.0
        self._P[m:, m:] *= 1_000.0          # high initial velocity uncertainty

        self._Q = np.eye(n, dtype=np.float64)
        self._Q[m:, m:] *= 0.01             # smooth velocity noise

        self._R = np.eye(m, dtype=np.float64) * 1.0  # measurement noise

    def predict(self) -> np.ndarray:
        """
        Advance state one time step (no measurement).

        Purpose  : Extrapolate position from current velocity.
        Inputs   : None.
        Outputs  : (4,) float64 predicted box [x1, y1, x2, y2].
        """
        self._x = self._F @ self._x
        self._P = self._F @ self._P @ self._F.T + self._Q
        return self._x[:self._MEAS_DIM, 0].copy()

    def update(self, box: np.ndarray) -> None:
        """
        Correct state with an observed measurement.

        Purpose  : Fuse prediction and observation to refine state.
        Inputs   : box — (4,) observed bounding box [x1, y1, x2, y2].
        Outputs  : Mutates internal state in-place.
        """
        z    = box.reshape(-1, 1).astype(np.float64)
        y    = z - self._H @ self._x
        S    = self._H @ self._P @ self._H.T + self._R
        K    = self._P @ self._H.T @ np.linalg.inv(S)
        n    = self._x.shape[0]
        self._x = self._x + K @ y
        self._P = (np.eye(n) - K @ self._H) @ self._P
