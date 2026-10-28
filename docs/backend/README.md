# Backend layer

The backend is a Django application under `backend/`. It currently provides:

- SQLite-backed Django configuration.
- An inspection app with the initial settings and record models.
- A health endpoint at `GET /api/health/`.
- A settings endpoint at `GET/POST /api/settings/` for the active sequence,
  layer distance, and color tolerance.
- Sequence classification that returns `PASS`, `REWORK`, or
  `INSPECTION_ERROR` when the detected wire count differs from the configured
  count.
- Initial OpenCV processing that removes the white background, detects wire
  regions, extracts RGB values, groups detections into layer bands, and
  generates an ordered color sequence.
- Process controls at `/api/process/{start|pause|resume|stop}/`.
- Multipart inspection processing at `POST /api/inspection/process/`, which
  stores every classification and rejects uploads while paused or stopped.
- Inspection history at `GET /api/inspection/history/` and CSV export with
  `?export=csv`.

Image acquisition, wire/layer detection, result classification, and process
control endpoints will be added in later implementation stages.
