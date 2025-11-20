# Pull Request Merge Workflow

**Purpose**: Systematic checklist for merging PRs into GenesisGraph with proper review, testing, documentation updates, and branch cleanup.

---

## Pre-Merge Checklist

### 1. PR Review
- [ ] **Read PR description** - Understand what's being changed and why
- [ ] **Review all changed files** - Check code quality, style, security
- [ ] **Verify issue linkage** - PR should reference related GitHub issue(s)
- [ ] **Check commit messages** - Follow conventional commits format
- [ ] **Review test coverage** - New code should have tests
- [ ] **Security review** - Check for vulnerabilities (XSS, injection, etc.)

### 2. CI/CD Validation
- [ ] **All tests passing** - GitHub Actions CI must be green
- [ ] **Test coverage maintained** - Should be ≥90% (check coverage report)
- [ ] **Linting passes** - No mypy/flake8/black issues
- [ ] **Security scans clean** - Bandit, Safety checks pass
- [ ] **No merge conflicts** - Branch is up to date with main

### 3. Local Testing
```bash
# Fetch and checkout PR branch
gh pr checkout <PR_NUMBER>

# Run full test suite
pytest -v --cov=genesisgraph --cov-report=term-missing

# Run linting
mypy genesisgraph/
flake8 genesisgraph/
black --check genesisgraph/

# Test examples
python -m genesisgraph.cli validate examples/level-a-full-disclosure.gg.yaml
python -m genesisgraph.cli validate examples/level-c-sealed-subgraph.gg.yaml

# Check documentation builds
cd docs && make html  # if Sphinx docs exist
```

### 4. Conflict Resolution (if needed)
```bash
# Update PR branch with latest main
git checkout <pr-branch>
git fetch origin main
git merge origin/main

# Resolve conflicts carefully
# - Preserve PR changes when they're improvements
# - Keep main changes when they're newer/better
# - Test thoroughly after resolution

# Run tests after merge
pytest -v

# Push resolved changes
git push origin <pr-branch>
```

---

## Documentation Updates

### 5. CHANGELOG.md
- [ ] **Add entry to [Unreleased]** section
- [ ] **Use correct category**: Added, Changed, Deprecated, Removed, Fixed, Security
- [ ] **Write clear description** - What changed and why it matters
- [ ] **Include issue/PR references** - e.g., "feat: Add SDK builders (#14)"

**Format:**
```markdown
## [Unreleased]

### Added
- **Feature Name** (#PR_NUMBER, #ISSUE_NUMBER)
  - Detailed description of what was added
  - Why it matters / use case
  - Any breaking changes or migration notes

### Fixed
- Description of bug fix (#PR_NUMBER, #ISSUE_NUMBER)
```

### 6. README.md (if needed)
- [ ] **Update version references** - If version changed
- [ ] **Add new features to overview** - If major feature added
- [ ] **Update examples** - If API changed
- [ ] **Update installation instructions** - If dependencies changed

### 7. Documentation Files
- [ ] **Check docs/** - Update guides if needed
- [ ] **API documentation** - Update if public API changed
- [ ] **Examples** - Add/update examples if needed
- [ ] **Migration guides** - If breaking changes

---

## Merge Process

### 8. Final Review
- [ ] **Re-read PR description** - Confirm all requirements met
- [ ] **Check all checkboxes above** - Everything validated
- [ ] **Verify documentation updated** - CHANGELOG, README, docs
- [ ] **Confirm tests pass** - Both CI and local

### 9. Merge Strategy

**For Feature PRs (recommended):**
```bash
# Squash and merge for clean history
gh pr merge <PR_NUMBER> --squash --delete-branch

# Or via GitHub UI:
# - Click "Squash and merge"
# - Edit commit message to be clear and complete
# - Include "Co-authored-by" lines if multiple contributors
# - Check "Delete branch" option
```

**For Multi-commit PRs with important history:**
```bash
# Create a merge commit to preserve history
gh pr merge <PR_NUMBER> --merge --delete-branch
```

**For Small fixes:**
```bash
# Rebase for linear history (use sparingly)
gh pr merge <PR_NUMBER> --rebase --delete-branch
```

### 10. Post-Merge Actions

**Immediate:**
- [ ] **Verify branch deleted** - PR branch should auto-delete
- [ ] **Check main CI** - Ensure main branch CI passes
- [ ] **Close related issues** - Link and close fixed issues
- [ ] **Update project boards** - Move cards to "Done"

**Documentation:**
- [ ] **Verify CHANGELOG updated** - Should be in main now
- [ ] **Check docs deployed** - If auto-deploy is set up
- [ ] **Verify examples work** - Test against merged changes

**Cleanup:**
```bash
# Delete local PR branch
git branch -d <pr-branch>

# Prune remote tracking branches
git fetch --prune

# Clean up stale remote branches (if you have permissions)
git push origin --delete <merged-branch-name>
```

---

## Branch Cleanup

### 11. Periodic Cleanup (run monthly)

**Identify stale branches:**
```bash
# List merged branches
git branch -r --merged origin/main

# List branches not updated in 30+ days
git for-each-ref --sort=-committerdate --format='%(committerdate:short) %(refname:short)' refs/remotes/
```

**Safe deletion:**
```bash
# Only delete branches that are:
# 1. Fully merged to main
# 2. Have associated PR that was merged
# 3. No ongoing work

# Delete remote branch
git push origin --delete <branch-name>

# Delete local tracking branch
git branch -d <branch-name>
```

---

## Version Release Process

### When releasing a new version (e.g., v0.3.0):

1. **Update CHANGELOG.md**
   ```markdown
   ## [0.3.0] - YYYY-MM-DD

   ### Added
   [Move items from [Unreleased]]

   ## [Unreleased]
   [Empty for now]
   ```

2. **Update version files**
   - `pyproject.toml`: version = "0.3.0"
   - `genesisgraph/__init__.py`: __version__ = "0.3.0"
   - `README.md`: Update version references

3. **Create release commit**
   ```bash
   git add CHANGELOG.md pyproject.toml genesisgraph/__init__.py README.md
   git commit -m "release: Bump to v0.3.0"
   git push origin main
   ```

4. **Create GitHub release**
   ```bash
   gh release create v0.3.0 --title "v0.3.0: SDK Libraries & Profile Validators" --notes-file RELEASE_NOTES.md
   ```

5. **Tag and publish**
   ```bash
   git tag -a v0.3.0 -m "GenesisGraph v0.3.0"
   git push origin v0.3.0
   ```

---

## Special Cases

### Large PRs (>500 lines)
- Request PR be split into smaller, logical chunks
- Review in multiple sessions
- Extra scrutiny on tests and documentation

### Breaking Changes
- **Must** include migration guide
- **Must** update CHANGELOG with "BREAKING" label
- Consider deprecation warnings before removal
- Bump major version (if v1.0+) or minor version (if v0.x)

### Security Fixes
- Expedite review and merge
- Update SECURITY.md if needed
- Consider security advisory if vulnerability was public
- Backport to supported versions if needed

### Documentation-Only PRs
- Can merge faster (less risk)
- Still check for accuracy
- Verify links work
- Check spelling/grammar

---

## Quick Reference

**Merge a PR:**
```bash
gh pr checkout <number>  # Review locally
pytest -v                 # Test
gh pr merge <number> --squash --delete-branch  # Merge
```

**Clean up branches:**
```bash
git fetch --prune
git branch -d <local-branch>
git push origin --delete <remote-branch>
```

**Update CHANGELOG:**
```markdown
## [Unreleased]

### Added
- Your feature here (#PR, #ISSUE)
```

---

## Contact

Questions about this workflow? See:
- CONTRIBUTING.md
- GitHub Discussions
- Open an issue

---

**Last Updated**: 2025-11-19
**Maintained by**: GenesisGraph Core Team
