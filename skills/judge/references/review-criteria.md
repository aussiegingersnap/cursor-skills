# Review Criteria by Skill Type

Detailed review criteria for evaluating output from different skill categories.

## Frontend Skills

Skills: `design-system`, `design-principles`, `nextjs-16`, `effector`, `state-management`

### Component Output

| Criterion | Pass Condition |
|-----------|----------------|
| Renders correctly | Component visible in browser, no console errors |
| All states shown | Default, hover, focus, loading, error, disabled states demonstrated |
| Responsive | Works on mobile viewport (< 768px) |
| Accessible | Keyboard navigable, proper ARIA labels |
| Exported | Available from component barrel file |

### State Management Output

| Criterion | Pass Condition |
|-----------|----------------|
| Type-safe | Full TypeScript coverage, no `any` types |
| Reactive | UI updates when state changes |
| No memory leaks | Subscriptions cleaned up on unmount |
| Testable | Can be tested in isolation |

## Backend Skills

Skills: `db-postgres`, `db-sqlite`, `api-rest`, `auth-better-auth`, `auth-lucia`

### Database Changes

| Criterion | Pass Condition |
|-----------|----------------|
| Migration exists | SQL migration file generated |
| Reversible | Down migration works |
| Schema correct | Tables, columns, indexes as specified |
| Types exported | TypeScript types generated from schema |

### API Endpoint Output

| Criterion | Pass Condition |
|-----------|----------------|
| Route exists | Endpoint accessible at specified path |
| Validation | Zod schema validates input |
| Error handling | Proper error responses for invalid input |
| Auth | Protected routes require authentication |
| Response format | Matches documented schema |

### Auth Integration

| Criterion | Pass Condition |
|-----------|----------------|
| Login works | Valid credentials grant access |
| Logout works | Session terminated, tokens invalidated |
| Protected routes | Unauthenticated users redirected |
| Session persists | Refresh maintains session |

## Infrastructure Skills

Skills: `docker-local`, `infra-railway`, `env`, `1password`

### Docker Output

| Criterion | Pass Condition |
|-----------|----------------|
| Builds | `docker compose build` succeeds |
| Runs | `docker compose up` starts services |
| Healthy | Health checks pass |
| Volumes | Data persists across restarts |

### Deployment Output

| Criterion | Pass Condition |
|-----------|----------------|
| Deploys | Deployment completes without error |
| Accessible | Service reachable at expected URL |
| Env vars | All required variables configured |
| Logs | Application logging works |

### Secrets Output

| Criterion | Pass Condition |
|-----------|----------------|
| No plaintext | Secrets not in code or git history |
| Accessible | Application can read secrets at runtime |
| Documented | Required secrets listed in .env.example |

## Document Skills

Skills: `document-skills/docx`, `document-skills/pdf`, `document-skills/pptx`, `document-skills/xlsx`

### Document Output

| Criterion | Pass Condition |
|-----------|----------------|
| Opens | File opens in appropriate application |
| Content correct | All specified content present |
| Formatting | Styles, fonts, layouts as expected |
| No corruption | File saves and reopens cleanly |

## Productivity Skills

Skills: `linear`, `tools-youtube`, `repo-review`, `email-resend`

### Integration Output

| Criterion | Pass Condition |
|-----------|----------------|
| API connected | Can read/write to external service |
| Auth works | Credentials properly configured |
| Data accurate | Information matches source |
| Error handling | Graceful failure on API errors |

## Creative Skills

Skills: `artifacts-builder`, `feature-gating`

### Artifact Output

| Criterion | Pass Condition |
|-----------|----------------|
| Renders | HTML/React renders in browser |
| Interactive | User interactions work |
| Styled | CSS/Tailwind applied correctly |
| Self-contained | All dependencies bundled |

### Feature Flag Output

| Criterion | Pass Condition |
|-----------|----------------|
| Flag created | Flag exists in PostHog |
| Gating works | Feature hidden when flag off |
| Tracking | Usage events captured |
| Fallback | Graceful behavior if flag service unavailable |

## Universal Criteria

These apply to all skill output:

### Code Quality

| Criterion | Pass Condition |
|-----------|----------------|
| No lint errors | Linter passes |
| Type-safe | TypeScript compiles without errors |
| Formatted | Matches project formatting |
| No dead code | Unused imports/variables removed |

### Scope

| Criterion | Pass Condition |
|-----------|----------------|
| Addresses spec | All acceptance criteria met |
| No scope creep | No changes outside specified scope |
| Minimal | Simplest solution that works |

### Documentation

| Criterion | Pass Condition |
|-----------|----------------|
| Updated | Relevant docs reflect changes |
| Comments | Complex logic explained |
| Types | TypeScript provides documentation |
