# Database schema

## InspectionSettings

Stores the active component configuration, expected color sequence, layer
distance, and color tolerance.

## InspectionRecord

Stores component serial number, component name, operator identity, expected
and detected sequences, expected and detected wire counts, result, error
details, image references, and test time.

The result values are `PASS`, `REWORK`, and `INSPECTION_ERROR`. A count mismatch
or inability to detect the configured number of wires must never be silently
converted into rework; it is recorded as `INSPECTION_ERROR`.

The expected wire count is derived from the length of `expected_sequence`, so
operators can configure any sequence containing at least two colors.

`InspectionProcess` stores the station state (`RUNNING`, `PAUSED`, or
`STOPPED`) used to gate inspection submissions.

History is read directly from `InspectionRecord`; CSV export does not create a
second copy of production data.
