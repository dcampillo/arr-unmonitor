# PRD — Arr-Unmonitor Modernization & Hardening

**Status:** Draft
**Date:** 2026-06-04
**Owner:** dcampillo
**Current version:** 0.9 (Nov 2021)
**Target version:** 1.0

---

## 1. Background

Arr-Unmonitor is a pair of Python custom-script connectors that automatically
unmonitor a movie (Radarr) or episode (Sonarr) after a download is imported.
They are registered in Radarr/Sonarr under **Settings → Connect → Custom Scripts**
with the "On Import" trigger, and receive their input through environment
variables set by the *arr app.

The scripts were last released in November 2021 (v0.9). Since then Sonarr has
moved to v3/v4 and **removed the unversioned `/api/...` endpoints** the Sonarr
script depends on. As a result the Sonarr script no longer works against current
installs, and several latent bugs and rough edges have accumulated.

## 2. Goals

1. **Make the Sonarr script work on current Sonarr (v3/v4).**
2. **Fix the multi-episode import bug** so multi-episode files unmonitor correctly.
3. **Fix correctness bugs and typos** in both scripts.
4. **Improve robustness** (timeouts, clearer errors, correct exit codes).
5. **Keep the zero-dependency, single-file, env-var-driven design** — it must
   still run as a Custom Script with stock Python 3.

## 3. Non-Goals

- No rewrite into a package, daemon, or service.
- No third-party dependencies (must run with the Python stdlib only).
- No GUI / web interface.
- No change to the *arr-side setup workflow (still a Custom Script on "On Import").

## 4. Current State & Problems

### 4.1 Sonarr script (`sonarr-unmonitor.py`)

| # | Severity | Problem |
|---|----------|---------|
| S1 | **Blocker** | Uses removed v2 endpoint `/api/episode/{id}`. Current Sonarr requires `/api/v3/episode/...`. Script fails (404 / URLError) on modern Sonarr. |
| S2 | **High** | `sonarr_episodefile_episodeids` can be a **comma-separated list** on multi-episode files. The code passes the raw string as a single ID, so multi-episode imports break (and even single IDs hit the wrong endpoint). |
| S3 | Medium | Generic `except Exception` writes `"Unknow Error RRRRRRRRRR"` (typo, unhelpful) and does **not** exit non-zero, so failures look like success to Sonarr. |
| S4 | Low | Config "Test" event validates API key and port but not host. |
| S5 | Low | Unused imports: `logging`, `re`, `path`. Typos in comments ("episde"). |

### 4.2 Radarr script (`radarr-unmonitor.py`)

| # | Severity | Problem |
|---|----------|---------|
| R1 | **Functional** ✅ | Already on v3 (`/api/v3/movie/{id}`) — GET-then-PUT flow is still valid. |
| R2 | Medium | Success message says `EpisodeID:{movieid} - Unmonitored` — copy-paste from Sonarr; should say MovieID. Misleading logs. |
| R3 | Medium | Same swallowed-`Exception` issue as S3 (no non-zero exit, "Unknow Error" typo). |
| R4 | Low | Unused imports: `logging`, `re`, `path`. |

### 4.3 Shared issues

| # | Severity | Problem |
|---|----------|---------|
| C1 | Medium | No request **timeout** on `urlopen`; a hung *arr app can hang the import callback. |
| C2 | Low | SSL bypass is done via global `ssl._create_default_https_context` mutation inside the GET helper; works but is implicit and only set on the GET path. Prefer an explicit `ssl.SSLContext` passed to `urlopen`. |
| C3 | Low | Secrets (`ARR_API_KEY`) are hardcoded in the file. Optionally allow override via environment variable so the key need not live in the script. |
| C4 | Low | Significant duplication between the two scripts. Out of scope to merge, but config/typo fixes should be applied consistently to both. |

## 5. Requirements

### 5.1 Functional

- **FR1 (S1):** The Sonarr script MUST call the versioned endpoint
  `PUT /api/v3/episode/monitor` with body
  `{"episodeIds": [<int>...], "monitored": false}`.
  This single call replaces the GET-then-PUT flow and works on Sonarr v3 and v4.
- **FR2 (S2):** The Sonarr script MUST parse `sonarr_episodefile_episodeids` as a
  comma-separated list, convert each entry to an int, and unmonitor **all** of them
  in one `/episode/monitor` call.
- **FR3 (R2):** The Radarr success message MUST report `MovieID`, not `EpisodeID`.
- **FR4 (S3/R3):** On any unhandled error the scripts MUST write a clear message
  to stderr **and exit with a non-zero status** so the *arr app surfaces the failure.
- **FR5:** The "Test" event behavior MUST be preserved (validate config, return
  success/failure) so the in-app "Test" button still works. Optionally also
  validate that `ARR_HOST` is set (S4).

### 5.2 Non-Functional

- **NFR1 (C1):** All HTTP calls MUST use an explicit timeout (e.g. 30s).
- **NFR2:** Scripts MUST remain single-file, stdlib-only, Python 3.8+ compatible.
- **NFR3 (C2):** SSL verification bypass MUST be explicit and applied to every
  request (GET and PUT), not just one path.
- **NFR4 (C3, optional):** `ARR_API_KEY`, `ARR_HOST`, `ARR_PORT` MAY be overridable
  via environment variables, falling back to the in-file constants.

### 5.3 Cleanup

- **CR1 (S5/R4):** Remove unused imports (`logging`, `re`, `path`).
- **CR2:** Fix typos in code, messages, and README ("Unmomitor", "episde",
  "Unknow", "EpisodeID" in Radarr).
- **CR3:** Bump version to **1.0** in both script headers and update the README
  (Sonarr now uses `/api/v3`, note Sonarr v4 support).

## 6. Proposed Approach (high level)

**Sonarr script:**
1. Build base URL `http(s)://{host}:{port}/api/v3`.
2. Read `sonarr_episodefile_episodeids`, split on `,`, strip, cast to `int`.
3. `PUT /api/v3/episode/monitor` with `{"episodeIds": [...], "monitored": false}`.
4. Wrap in try/except with explicit stderr message + `sys.exit(1)` on failure.

**Radarr script:**
1. Keep the v3 GET-then-PUT flow (no bulk endpoint needed for a single movie).
2. Fix the success message to say MovieID.
3. Apply the shared error-handling/timeout/SSL/import cleanups.

**Both:** add `timeout=` to `urlopen`, explicit `ssl.SSLContext`, remove unused
imports, fix typos, bump to v1.0.

## 7. Testing & Acceptance

- **A1:** With a real or mocked Sonarr v4, importing a **single-episode** file
  unmonitors that episode; the script exits 0.
- **A2:** Importing a **multi-episode** file (e.g. `"101,102"`) unmonitors **all**
  listed episodes in one request.
- **A3:** A bad host/API key produces a clear stderr message and a **non-zero**
  exit code (verifiable via the in-app "Test" and a forced-failure run).
- **A4:** Radarr import unmonitors the movie and logs `MovieID:<id>`.
- **A5:** Both scripts run under Python 3.8 with no extra packages installed.
- **A6:** The `testing/setenv.py` helper continues to provide sample env vars for
  local runs (extend with a multi-id example like `"101,102"`).

> Note: live testing requires running Radarr/Sonarr instances, which the CI/dev
> environment may not have. Where a live instance is unavailable, validate via a
> local mock/stub of the HTTP endpoint and by asserting the constructed
> request (URL, method, body).

## 8. Risks & Open Questions

- **Q1:** Sonarr API key for the `/api/v3` endpoints is unchanged from v2 — confirm
  against the user's actual install version (v3 vs v4).
- **Q2:** Should env-var overrides (NFR4) be in scope for 1.0, or deferred? Keeps
  secrets out of the script but adds surface area.
- **Q3:** Is merging the two scripts into one shared module desired later, or keep
  them intentionally standalone for drop-in simplicity? (Currently: keep separate.)

---

### Summary of work items

| ID | Item | Priority |
|----|------|----------|
| FR1 | Sonarr → `/api/v3/episode/monitor` | P0 |
| FR2 | Parse multi-episode ID list | P0 |
| FR4 | Non-zero exit + clear errors (both) | P1 |
| FR3 | Radarr MovieID log fix | P1 |
| NFR1 | Request timeouts | P1 |
| NFR3 | Explicit SSL handling | P2 |
| CR1/CR2/CR3 | Imports, typos, version + README | P2 |
| NFR4 | Env-var config override (optional) | P3 |
