# Publishing to PyPI

## Publish New Version

Just tell Kiro: "发布 0.1.x 版本" and it will:
1. Update version in `blocklink/__init__.py`
2. Commit and push changes
3. Create and push tag

GitHub Actions automatically builds and publishes to PyPI.

Monitor: https://github.com/derek44554/BlockLink/actions

## Version Format

- `v0.1.x` - Patch
- `v0.x.0` - Minor
- `vx.0.0` - Major
