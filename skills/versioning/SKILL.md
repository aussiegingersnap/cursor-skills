# Versioning Skill

Semantic versioning automation based on conventional commits. Automatically manages version bumps, changelogs, and git tags using `standard-version`.

## When to Use

- Before releasing a new version
- When preparing a deployment
- To generate/update CHANGELOG.md
- When the user asks about version management
- Setting up versioning for a new project

## Prerequisites

- Conventional commits enforced (recommended: lefthook)
- Node.js project with package.json

## Setup (One-Time)

### 1. Install standard-version

```bash
npm install --save-dev standard-version
```

### 2. Add scripts to package.json

```json
{
  "scripts": {
    "release": "standard-version",
    "release:minor": "standard-version --release-as minor",
    "release:major": "standard-version --release-as major",
    "release:patch": "standard-version --release-as patch",
    "release:first": "standard-version --first-release"
  }
}
```

### 3. Create .versionrc config (optional but recommended)

```json
{
  "types": [
    {"type": "feat", "section": "✨ Features"},
    {"type": "fix", "section": "🐛 Bug Fixes"},
    {"type": "perf", "section": "⚡ Performance"},
    {"type": "refactor", "section": "♻️ Refactoring"},
    {"type": "docs", "section": "📚 Documentation", "hidden": true},
    {"type": "style", "section": "💄 Styling", "hidden": true},
    {"type": "chore", "hidden": true},
    {"type": "test", "hidden": true},
    {"type": "ci", "hidden": true},
    {"type": "build", "hidden": true}
  ],
  "commitUrlFormat": "https://github.com/{{owner}}/{{repository}}/commit/{{hash}}",
  "compareUrlFormat": "https://github.com/{{owner}}/{{repository}}/compare/{{previousTag}}...{{currentTag}}",
  "tagPrefix": "v"
}
```

## How Version Bumps Work

Based on conventional commits since last tag:

| Commit Type | Version Bump | Example |
|-------------|--------------|---------|
| `feat:` | MINOR (0.x.0) | `feat: add user auth` → 0.1.0 → 0.2.0 |
| `fix:` | PATCH (0.0.x) | `fix: null check` → 0.1.0 → 0.1.1 |
| `feat!:` or `BREAKING CHANGE:` | MAJOR (x.0.0) | `feat!: new API` → 0.1.0 → 1.0.0 |
| `docs:`, `style:`, `chore:` | No bump | Hidden from changelog |

## Release Workflow

### Standard Release (auto-detect bump)

```bash
npm run release
```

This will:
1. Analyze commits since last tag
2. Bump version in package.json
3. Update CHANGELOG.md
4. Create git commit with message `chore(release): 0.2.0`
5. Create git tag `v0.2.0`

### Then push with tags

```bash
git push --follow-tags origin main
```

### First Release (from 0.0.0 or 0.1.0)

```bash
npm run release:first
```

Creates initial tag without bumping version.

### Force Specific Bump

```bash
npm run release:patch  # 0.1.0 → 0.1.1
npm run release:minor  # 0.1.0 → 0.2.0
npm run release:major  # 0.1.0 → 1.0.0
```

### Pre-release (alpha/beta/rc)

```bash
npx standard-version --prerelease alpha  # 0.1.0 → 0.2.0-alpha.0
npx standard-version --prerelease beta   # 0.2.0-alpha.0 → 0.2.0-beta.0
npx standard-version --prerelease rc     # 0.2.0-beta.0 → 0.2.0-rc.0
npx standard-version                     # 0.2.0-rc.0 → 0.2.0 (stable)
```

### Dry Run (preview without changes)

```bash
npx standard-version --dry-run
```

## Lefthook Integration

### Enforce Conventional Commits (pre-requisite)

Add to `lefthook.yml`:

```yaml
commit-msg:
  commands:
    conventional-commit:
      run: |
        msg=$(cat "{1}")
        if ! echo "$msg" | grep -qE "^(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)(\(.+\))?: .+"; then
          echo ""
          echo "❌ Invalid commit message format"
          echo ""
          echo "Expected: <type>(<scope>): <subject>"
          echo "Example:  feat(api): add user endpoint"
          echo ""
          echo "Types: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert"
          echo ""
          exit 1
        fi
```

### Validate Tags on Push (optional)

```yaml
pre-push:
  commands:
    version-tag-check:
      run: |
        # Check if HEAD has a version tag (release commit)
        if git describe --exact-match HEAD 2>/dev/null | grep -qE "^v[0-9]"; then
          if ! echo "$*" | grep -q "follow-tags"; then
            echo ""
            echo "⚠️  Release detected but --follow-tags not used"
            echo "   Run: git push --follow-tags origin main"
            echo ""
          fi
        fi
```

## Displaying Version in App

### Static Import (build-time)

```typescript
import packageJson from '../package.json'

export function VersionDisplay() {
  return <span>v{packageJson.version}</span>
}
```

### Dynamic API (runtime, for deployment builds)

Create `/api/version/route.ts`:

```typescript
import { NextResponse } from 'next/server'

const BUILD_VERSION = process.env.RAILWAY_DEPLOYMENT_ID 
  || process.env.VERCEL_GIT_COMMIT_SHA 
  || process.env.BUILD_VERSION
  || Date.now().toString()

export async function GET() {
  return NextResponse.json(
    { version: BUILD_VERSION },
    { headers: { 'Cache-Control': 'no-store' } }
  )
}
```

Then fetch in component:

```typescript
const [version, setVersion] = useState<string>()

useEffect(() => {
  fetch('/api/version')
    .then(r => r.json())
    .then(d => setVersion(d.version?.slice(0, 8)))
}, [])
```

## Monorepo Considerations

For monorepos with multiple packages:

```bash
# Release from specific directory
cd packages/web && npm run release

# Or use workspaces
npx standard-version --path packages/web
```

## Best Practices

1. **Always use conventional commits** - lefthook enforces this
2. **Release from main branch only** - keep releases clean
3. **Use dry-run first** - preview changes before committing
4. **Push with --follow-tags** - ensures tags reach remote
5. **Don't skip CI on release commits** - validate releases too
6. **Tag format**: Use `v` prefix (v1.0.0) for consistency

## Troubleshooting

### "No commits since last release"
Your commits may not follow conventional format. Check with:
```bash
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

### Version not bumping as expected
Check commit types. `docs:` and `chore:` don't trigger bumps by default.

### Tags not appearing on remote
Always use `git push --follow-tags origin main`

### Want to skip version bump on specific commit
Add `[skip ci]` or use `chore:` type for housekeeping commits.
