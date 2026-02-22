# Prusa XL Collector POC

## Purpose
Define a minimal, production-aligned collector proof-of-concept for Prusa XL
diagnostics data (errors, telemetry, job status), with a clear data flow into
PostgreSQL and Grafana.

## Relevant Prusa3D Repos
- https://github.com/prusa3d/Prusa-Firmware-Buddy (XL firmware stack)
- https://github.com/prusa3d/Prusa-Error-Codes (error taxonomy)
- https://github.com/prusa3d/Prusa-Link-Web (PrusaLink API spec)
- https://github.com/prusa3d/PrusaSlicer (job metadata, profiles, G-code context)

## Data Sources And Access Paths
Confirmed: network access over WiFi. The collector supports:
- Network API (HTTP/HTTPS)
- USB/serial (direct device connection)
- On-device log files (exported from device or SD card)
- SD/USB job artifacts (G-code + metadata)

Log path (manual export or mounted USB):
- `PRUSA_XL_LOG_PATH=/path/to/logs`

### PrusaLink (Primary Option)
PrusaLink is the native web interface on the Prusa XL. Use the PrusaLink client for direct API access.

Env vars:
- `PRUSALINK_BASE_URL=http://prusa-xl.local` (or printer IP/hostname)
- `PRUSALINK_USERNAME=<username>` (from PrusaLink Settings)
- `PRUSALINK_PASSWORD=<password>`
- `PRUSALINK_PRINTER_ID=prusa-xl-1` (optional)
- `PRUSALINK_TIMEOUT_SECONDS=10` (optional)

Endpoints used:
- `/api/v1/status` (printer, job, transfer, storage, camera)
- `/api/v1/job` (current job)
- `/api/v1/info` (printer info)

Auth: Digest (required by PrusaLink). See [Prusa-Link-Web OpenAPI](https://github.com/prusa3d/Prusa-Link-Web/blob/master/spec/openapi.yaml).

### Network Collector Configuration
Use one of these patterns:
- Single payload URL (full URL):
  - `PRUSA_XL_PAYLOAD_URL=https://printer/api/diagnostics`
- Base URL + endpoint paths:
  - `PRUSA_XL_BASE_URL=https://printer`
  - `PRUSA_XL_STATUS_ENDPOINT=/api/status`
  - `PRUSA_XL_ERRORS_ENDPOINT=/api/errors`
  - `PRUSA_XL_TELEMETRY_ENDPOINT=/api/telemetry`
  - `PRUSA_XL_INFO_ENDPOINT=/api/info`
  - `PRUSA_XL_STORAGE_ENDPOINT=/api/storage`

Auth options:
- None:
  - `PRUSA_XL_AUTH_TYPE=none`
- Basic:
  - `PRUSA_XL_AUTH_TYPE=basic`
  - `PRUSA_XL_USERNAME=your_username`
  - `PRUSA_XL_PASSWORD=your_password`
- Digest:
  - `PRUSA_XL_AUTH_TYPE=digest`
  - `PRUSA_XL_USERNAME=your_username`
  - `PRUSA_XL_PASSWORD=your_password`
- Bearer:
  - `PRUSA_XL_AUTH_TYPE=bearer`
  - `PRUSA_XL_BEARER_TOKEN=your_token`

## OctoPrint Integration (Option D)
OctoPrint provides a richer API with job/log access. See [octoprint_xl_quirks.md](octoprint_xl_quirks.md) for known Prusa XL behaviors (absorbing heat, size warning, firmware).

Env vars:
- `OCTOPRINT_BASE_URL=http://octoprint:5000`
- `OCTOPRINT_API_KEY=your_octoprint_api_key`
- `OCTOPRINT_TIMEOUT_SECONDS=10`

Endpoints used:
- `/api/printer`
- `/api/job`
- `/api/logs`

## Signals Map (Minimal POC)
Errors:
- error_code, error_message, severity, subsystem, timestamp

Telemetry:
- nozzle_temp_c, bed_temp_c, chamber_temp_c
- fan_speed_pct, print_progress_pct
- print_state, toolhead_id, job_id

Jobs:
- job_name, job_started_at, job_finished_at, result
- slicer_profile_id, material_profile_id (if available)

## Normalized Schema (Event + Telemetry)
Event (prusa_xl_error_events):
- id (uuid)
- printer_id (text)
- error_code (text)
- error_message (text)
- severity (text)
- subsystem (text)
- event_time (timestamptz)
- raw_payload (jsonb)

Telemetry (prusa_xl_telemetry_samples):
- id (uuid)
- printer_id (text)
- sample_time (timestamptz)
- nozzle_temp_c (float)
- bed_temp_c (float)
- chamber_temp_c (float)
- fan_speed_pct (float)
- print_progress_pct (float)
- print_state (text)
- toolhead_id (text)
- job_id (text)
- raw_payload (jsonb)

## Data Flow
1) Collector adapter pulls raw payload (USB/serial, network, logs).
2) Normalizer maps payload to event + telemetry schemas.
3) Storage writes to PostgreSQL.
4) Grafana dashboard reads from PostgreSQL.

## Grafana Dashboard (POC)
Location: `monitoring/grafana/dashboards/prusa-xl-overview.json`
Panels:
- Error count by error_code (last 24h)
- Nozzle/bed temperature time series
- Print progress over time

## Open Questions / Validation
- Confirm XL network endpoints and payload format.
- Confirm firmware exposure for error codes and state.
- Determine polling interval without overloading device.

## Next Steps
- Wire network collector to confirmed endpoints.
- Capture sample payloads for schema hardening.
- Validate ingestion end-to-end with Grafana.
