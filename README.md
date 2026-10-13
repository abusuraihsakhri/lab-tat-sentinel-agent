# Lab TAT Sentinel Agent

A Python command-line tool, FastAPI service, and browser-local demonstration for applying **illustrative, rule-based alerts** to synthetic laboratory operations tasks. The present implementation does **not** calculate specimen turnaround time from LIS event timestamps, predict delays, or provide validated clinical decision support.

## Browser demonstration

The standalone interface in [`web/`](web/) evaluates synthetic task inputs using JavaScript rules corresponding to the three workers in `agents/workers.py`. It works without a Python runtime or backend and displays its execution mode and threshold values. Results can be exported as JSON.

To run locally:

```bash
python -m http.server 8001 --directory web
```

Open `http://localhost:8001`. Do not use actual patient identifiers. The browser demo holds inputs/results only in page memory and makes no application API requests. It does not produce an HMAC signature or persist an audit log.

A GitHub Pages deployment workflow is included in `.github/workflows/pages.yml`; a live Pages URL should only be cited after GitHub Pages is enabled and deployment is verified.

## Python installation

Requires Python 3.10 or newer:

```bash
python -m pip install -e ".[api]"
```

Run the primary CLI:

```bash
lab-tat-sentinel-engine audit --task-id TASK-001 --target SPECIMEN-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
lab-tat-sentinel-engine batch -i sample.csv -o results.csv
lab-tat-sentinel-engine chat "What is the system status?"
lab-tat-sentinel-engine verify-audit
```

`python cli.py` offers the same commands. The batch reader accepts either `primary_metric` / `secondary_metric` or the sample file's legacy `metric_primary` / `metric_secondary` names; it also accepts `is_critical_flag` or `is_stat`. Malformed rows are skipped with a warning; the output reports processed counts.

## API and Docker

Run the API bound to localhost:

```bash
lab-tat-sentinel-engine serve --host 127.0.0.1 --port 8000
```

Implemented endpoints: `GET /health`, `GET /metrics` (Prometheus text), `POST /api/audit`, `POST /api/chat` (deterministic mock), and `GET /api/audit/logs`. The API is **unauthenticated** and must not be exposed to untrusted networks without appropriate access controls. Neither the mock chat response nor the alert thresholds constitute clinical verification.

For container use, configure an independent secret before starting Docker Compose, for example:

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
docker compose up --build
```

If an existing deployment used the formerly committed demonstration signing key, replace it. The HMAC audit chain resides **only in process memory**; setting a secret does not persist logs across restarts. HMACs are verified for each entry, but there is no external append-only storage or independent anchoring.

## Rules and limitations

The primary `agents/` implementation contains three deterministic workers:

| Rule | Trigger | Result |
| --- | --- | --- |
| Primary metric threshold | `primary_metric > 25` | Elevated alert |
| Secondary metric / priority | `secondary_metric > 12` or `is_critical_flag` | Elevated alert, or critical when explicitly flagged |
| Descriptor keyword | Includes `DISCORDANT`, `ANOMALY`, `MUTANT`, `VIOLATION`, `FAIL`, or `REJECT` | Elevated alert |

The thresholds and keywords are demonstration constants, **not** validated CAP/CLSI limits or institutional turnaround-time service-level agreements. The repository also retains historical `lab_tat_sentinel.py`, `lab_tat_sentinel_agent/`, and `enrichment.py` implementations for compatibility; these use different rule schemas and some enrichment classes are placeholders rather than implemented forecasting features.

## Privacy and security

Use synthetic data exclusively. A regex-based sensitive-identifier screen rejects some common patterns; it is **not comprehensive PHI detection, HIPAA Safe Harbor de-identification, or a replacement for a privacy review**. API requests, audit state, and dossiers are processed in server memory; the service does not implement authentication, persistence, access control, or a secured external LIS integration.

## Tests

```bash
python -m pip install -e ".[api,test]"
python -m pytest -q
node --test tests/browser.test.mjs
python cli.py batch -i sample.csv -o results.csv
```

GitHub Actions runs the Python suite on 3.10–3.12 and the Node 22 rule tests. The static browser client uses native ES modules and modern browser APIs supported by current Chromium, Firefox, and Safari versions; cross-browser end-to-end testing is not part of the automated suite.

## License

[MIT](LICENSE).
