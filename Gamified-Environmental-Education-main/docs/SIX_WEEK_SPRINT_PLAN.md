# EcoQuest: Six-Week Sprint Plan

**Sprint cadence:** one week, Wednesday to Tuesday  
**Plan dates:** October 7–November 17, 2026  
**Sprint reviews:** every Tuesday; update the progress board below after each review  
**Priority:** security work begins today and is the focus of Sprint 1.

## Sprint progress board

Use this as the team's running record. Update the status, completion estimate, shipped outcomes, blockers, and evidence at the end of every sprint. A sprint is complete only when its acceptance checks pass; do not mark it complete just because the calendar week ended.

| Sprint | Dates | Focus | Status | Progress | Shipped outcomes / evidence | Blockers |
|---|---|---|---|---:|---|---|
| 1 | Oct 7–13 | Security baseline and hardening | In progress | 80% | Added production secret/CORS requirements, teacher invite-code gate, API security headers, safer upstream errors, short-lived JWTs, rotating HttpOnly refresh cookies, CSRF checks, and 20 backend security tests; frontend production build passed. | Finish broader security review and deployment configuration verification. |
| 2 | Oct 14–20 | Mission submission and teacher review | Not started | 0% | — | — |
| 3 | Oct 21–27 | Reliable points, streaks, and badges | Not started | 0% | — | — |
| 4 | Oct 28–Nov 3 | Teacher analytics and reporting | Not started | 0% | — | — |
| 5 | Nov 4–10 | Student experience and engagement | Not started | 0% | — | — |
| 6 | Nov 11–17 | Quality, release readiness, and demo | Not started | 0% | — | — |

**Overall progress:** completed sprints ÷ 6. Record this alongside the board at each review; use acceptance checks below to decide when a sprint counts as completed.

Record security test runs and manual/browser verification in the [security test tracker](./SECURITY_TEST_TRACKER.md); update the sprint evidence with a link to the relevant run.

### Review routine

At each Tuesday review:

1. Demo the sprint's working outcomes.
2. Run the stated acceptance checks and link or record the results.
3. Set the sprint to **Completed** only if all checks pass; otherwise keep it **In progress** or mark it **Blocked** with a clear reason.
4. Update progress, shipped outcomes, blockers, and the next sprint's carry-over items.

## Sprint 1 — Security baseline and hardening

**Dates:** October 7–13  
**Goal:** identify and close the highest-risk gaps before expanding product features.

**Starting today (October 7):**

- Review authentication, authorization, token/session handling, data access, CORS, and secrets configuration in the Flask API and React client.
- Confirm protected APIs enforce identity and role checks server-side; client-side route guards are not authorization.
- Verify production uses a stable, externally configured `SECRET_KEY`; fail clearly rather than silently using an ephemeral key in production.
- Restrict CORS to configured trusted origins instead of allowing arbitrary origins.
- Check that credentials and tokens are not logged or committed, and document safe local configuration.
- Add or update tests for unauthenticated access, role boundaries, invalid inputs, and user-to-user data isolation.

**Remaining Sprint 1 work:**

- Fix issues confirmed by the review, prioritizing access-control and session/signing risks.
- Add consistent, useful API error responses without exposing internal exception details.
- Document the threat model, configuration requirements, and security checks for future changes.

**Acceptance checks:**

- Production configuration refuses to start without a stable secret and trusted-origin configuration.
- Automated tests demonstrate protected routes reject missing/invalid credentials and enforce role and ownership rules.
- CORS behavior is verified for allowed and disallowed origins.
- No secrets are added to source control; local setup instructions explain required environment variables.
- Security fixes and remaining risks are reviewed and recorded.

## Sprint 2 — Mission submission and teacher review

**Dates:** October 14–20  
**Goal:** make a mission completion traceable from student submission through teacher decision.

**Planned work:**

- Verify and complete the existing mission flow before adding duplicate screens or APIs.
- Ensure submissions persist with a clear state such as pending, approved, or rejected, plus reflection and timestamps.
- Let teachers review only submissions for their own class and approve or reject with feedback.
- Prevent duplicate approvals from granting points more than once.
- Show submission status and teacher feedback to students.

**Acceptance checks:**

- Student submissions persist and appear to the correct teacher.
- A teacher cannot review or change another class's submissions.
- Approval/rejection persists and is visible to the student.
- Repeated requests cannot award duplicate points.

## Sprint 3 — Reliable points, streaks, and badges

**Dates:** October 21–27  
**Goal:** make gamification rewards consistent, auditable, and tied to verified activity.

**Planned work:**

- Define reward rules for approved missions and completed learning activities.
- Centralize reward updates so retries do not double-count points or badges.
- Calculate streaks consistently across timezone and day-boundary cases.
- Display points, streaks, and earned badges from persisted backend data.

**Acceptance checks:**

- Tests cover first-time rewards, retries, rejected submissions, and date-boundary streak behavior.
- Student totals agree across profile, dashboard, and leaderboard.
- Rewards are derived from verified events rather than client-submitted totals.

## Sprint 4 — Teacher analytics and reporting

**Dates:** October 28–November 3  
**Goal:** give teachers useful, class-scoped visibility into student engagement and learning.

**Planned work:**

- Add class summaries for mission completion, participation, and learning activity.
- Show trends over a useful date range and identify students who may need support.
- Add a CSV export for the teacher's authorized class data.
- Keep analytics queries and exports scoped to the signed-in teacher's class.

**Acceptance checks:**

- Dashboard totals match the underlying records for representative test data.
- Teachers cannot retrieve another class's analytics or exported records.
- Empty and error states are understandable; export output opens as valid CSV.

## Sprint 5 — Student experience and engagement

**Dates:** November 4–10  
**Goal:** help students understand what to do next and their progress without adding distracting complexity.

**Planned work:**

- Improve mission discovery, due-date/status visibility, and guidance after submission.
- Add a clear progress summary with the next recommended action.
- Review responsive layouts, keyboard navigation, labels, and contrast on key student flows.
- Add in-app reminders for outstanding or reviewed missions if the existing data model supports them.

**Acceptance checks:**

- A student can find a mission, understand its requirements, submit it, and see its review status on mobile and desktop.
- Core flows are keyboard usable and form controls have accessible labels.
- Any reminders are based on persisted state and do not expose another student's information.

## Sprint 6 — Quality, release readiness, and demo

**Dates:** November 11–17  
**Goal:** stabilize the end-to-end product and prepare a reliable demonstration/release.

**Planned work:**

- Run backend and frontend test suites; fix regressions from the six-week work.
- Verify the sign-up → mission → review → rewards → progress/report flow end to end.
- Check setup, environment configuration, database initialization, and deployment instructions.
- Conduct a final security pass and resolve release-blocking findings.
- Prepare a short demo and record known limitations and follow-up work.

**Acceptance checks:**

- Critical user journeys pass in a clean local setup.
- Tests and production build pass, or any known failures are documented and explicitly accepted.
- No release-blocking security issue remains open.
- A teammate can follow the setup guide and reproduce the demo.
- Sprint board reflects delivered outcomes, evidence, and deferred work.

## Scope and working agreements

- Keep work small enough to demo and test within each week; carry unfinished work forward explicitly rather than hiding it in a completion percentage.
- Security is not limited to Sprint 1: each sprint must apply authorization, validation, privacy, and testing to its changes.
- Prefer backend-verified state for points, roles, ownership, and completion status.
- Reassess scope at each review if dependencies or implementation findings change the plan; record changes in the progress board.
