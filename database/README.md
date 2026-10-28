# Database layer

SQLite is the initial database for a local production station. Django migrations
own the schema so the database can be exported or replaced with MSSQL without
changing the frontend contract.

The initial schema contains:

- `InspectionSettings`: active expected sequence, layer distance, and color tolerance.
- `InspectionRecord`: every inspection result, including `PASS`, `REWORK`, and
  `INSPECTION_ERROR`.

`INSPECTION_ERROR` is used when the detector cannot identify the configured
number of wires. Such records are retained with the detected count and error
details for traceability.
