---
name: release
description: Generic release assistant — analyzes repo release rules, then guides the release
triggers:
  - "release"
  - "cut release"
---

# Release

Generic release assistant. Analyzes repository release rules and guides the release process.

## Use When

- User wants to create a new release
- User says "release" or "cut release"
- Need to follow repository-specific release procedures

## Steps

1. **Discover rules**: Read `RELEASE.md`, `RELEASING.md`, or similar files
2. **Check version**: Determine current version and proposed new version
3. **Validate**: Check changelog, tests, and build status
4. **Prepare**: Update version strings, changelog, and tags
5. **Execute**: Run release commands (git tag, npm publish, etc.)
6. **Verify**: Confirm release artifacts are correct

## Tool Usage

- Use `ReadFile` for release rule discovery
- Use `Shell` for version commands and release execution
- Use `Glob` to find release-related files

## Final Checklist

- [ ] Version bumped in all relevant files
- [ ] Changelog updated
- [ ] Tests pass
- [ ] Build succeeds
- [ ] Git tag created
- [ ] Release published
