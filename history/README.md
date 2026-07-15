# Release reconstruction

The current creator source is stored in `dist/`. Historical public releases are deterministically reconstructed by applying the patches in this directory in reverse order.

Run:

```bash
bash scripts/build_releases.sh
```

The generated files are written to `build/releases/` and verified against `release-index.json`.
