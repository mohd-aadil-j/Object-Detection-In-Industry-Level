# Architecture overview

The application is split into three layers:

- `frontend/`: React and JavaScript/JSX operator interface.
- `backend/`: Django REST API, workflow state, and OpenCV processing.
- `database/`: SQLite through Django migrations, with an MSSQL-compatible
  migration path.

The inspection result contract has three outcomes:

1. `PASS`: detected wire count and color sequence match the active settings.
2. `REWORK`: the wire count is valid but the color sequence does not match.
3. `INSPECTION_ERROR`: the detector cannot find the number of wires configured
   by the operator.

All three outcomes are persisted for traceability.

The image-processing boundary returns detected wires with a normalized color
name, RGB value, center position, and layer index. It does not decide the
inspection result; the classifier first validates the detected count and then
compares the sequence.
