# Publishing to PyPI

## Publish New Version

1. Update version in `blocklink/__init__.py`
2. Commit and push changes
3. Create and push tag:
```bash
git tag -a v0.1.1 -m "Release description"
git push origin v0.1.1
```

GitHub Actions automatically builds and publishes to PyPI.

Monitor: https://github.com/derek44554/BlockLink/actions

## Version Format

- `v0.1.1` - Patch
- `v0.2.0` - Minor
- `v1.0.0` - Major
