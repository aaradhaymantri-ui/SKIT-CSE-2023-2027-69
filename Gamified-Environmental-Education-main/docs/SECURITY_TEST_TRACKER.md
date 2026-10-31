# EcoQuest Security Test Tracker

Use this checklist to record what has actually been verified. Mark a case **Pass** or **Fail** only after running it; use **Not run** when it still needs verification. For each future run, append a row to the run history with the date, tester, commit, results, and evidence. Never paste tokens, passwords, invitation codes, or other secrets into this document.

## Automated test run

**Latest recorded run:** 2026-10-09  
**Command (run from `backend`):** `python -m unittest discover -s tests -v`  
**Result:** 20 passed, 0 failed  
**Evidence:** `backend/tests/test_security.py`

| Automated coverage | Result |
|---|---|
| Production requires a strong secret and explicit CORS origins | Pass |
| Production validates the CORS allowlist and disables debug | Pass |
| CORS allows configured origins and rejects unknown origins | Pass |
| Standard security headers are added | Pass |
| Protected profile rejects missing or malformed JWTs | Pass |
| Protected profile rejects expired JWTs | Pass |
| Sign-in issues a short-lived JWT and HttpOnly refresh cookie | Pass |
| Production auth cookies set Secure, HttpOnly, and SameSite=Lax correctly | Pass |
| Sign-in rejects an untrusted origin | Pass |
| Refresh requires CSRF and rotates refresh/access tokens | Pass |
| Refresh rejects an untrusted origin | Pass |
| Logout revokes the refresh session | Pass |
| Student is blocked from teacher-only dashboard API | Pass |
| Student cannot complete a mission from another class | Pass |
| Teacher signup requires an invitation code | Pass |
| Valid configured invitation permits teacher signup | Pass |
| Signup rejects short passwords | Pass |
| Signup rejects non-object JSON | Pass |
| Dashboard upstream errors do not leak details | Pass |
| Chat upstream errors do not leak details | Pass |

## Manual/browser checks

These complement automated tests; they are **not** considered covered by the automated pass above. Re-run them after auth/UI changes.

| ID | Check | Status | Run date | Evidence / notes |
|---|---|---|---|---|
| M1 | Sign in through the UI; confirm dashboard opens and no access or refresh token appears in localStorage | Pass | 2026-10-09 | Browser sign-in reached student dashboard; localStorage contained only `currentUser` and `userName`; only CSRF cookie was JavaScript-visible. |
| M2 | Reload the signed-in page; confirm session restores through the refresh cookie | Pass | 2026-10-09 | Reload restored the student dashboard through refresh-cookie session recovery. |
| M3 | Simulate an expired access response; confirm a protected request refreshes and retries successfully | Pass | 2026-10-09 | Browser intercepted the first profile request as 401; auth client refreshed and retried; second request returned 200. |
| M4 | Sign out; confirm the UI returns to guest state and refresh cannot restore the session | Pass | 2026-10-09 | Logout returned browser to `/signin`, cleared localStorage/cookies; `/auth/csrf` returned 401. |
| M5 | Inspect cookie attributes: refresh is HttpOnly and SameSite=Lax; production uses Secure | Pass | 2026-10-09 | Backend Set-Cookie headers verified; production-mode test confirms Secure; browser can see only CSRF cookie, not HttpOnly refresh cookie. |
| M6 | Try a teacher-only page as a student and a student-only page as a teacher | Pass | 2026-10-09 | Student redirected from `/teacherdashboard`; teacher redirected from `/studentdashboard`. |
| M7 | Attempt sign-in from an untrusted origin and check API/browser rejection | Pass | 2026-10-09 | Live API returned no CORS allow-origin header for untrusted preflight; automated sign-in/refresh origin tests also pass. |

## Run history

| Date | Tester | Commit / branch | Automated result | Manual cases completed | Evidence / follow-up |
|---|---|---|---|---|---|
| 2026-10-07 | Development run | Working tree | 18 passed, 0 failed | None recorded | Automated run only; manual/browser checks remain. |
| 2026-10-09 | Development run | Working tree | 20 passed, 0 failed | M1–M7 passed | UI login/restore/refresh retry/role redirects/logout and cookie/CORS checks verified; browser retry was verified by intercepting a 401; expired JWT rejection is covered by an automated test. |

## Updating this tracker

1. Run the automated command and record the actual pass/fail totals and date.
2. Perform manual checks in a test environment; never record credentials or token values.
3. Change each manual status only after observing the expected result; include a short note or link to non-sensitive evidence.
4. Append a run-history row. Keep previous rows so regressions and verification history remain visible.
5. Link failures to an issue or follow-up task and leave them marked **Fail** until fixed and retested.
