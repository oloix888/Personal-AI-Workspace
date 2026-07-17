# Capability model

Skills audit semantic capabilities instead of assuming connector function names. Required states are `AVAILABLE_READ_WRITE`, `AVAILABLE_READ_ONLY`, `UNAVAILABLE`, `UNAUTHORIZED`, `ACCOUNT_MISMATCH`, `DEGRADED`, and `UNKNOWN`. Missing capabilities are reported and never invented.

Runtime capability checks map the current surface and account to semantic capabilities such as `notion.content.read`, `notion.content.write`, `drive.file.upload`, `drive.file.readback`, `github.issue.read`, and `github.issue.write`. A skill may continue with reduced scope only when the resulting operation remains truthful and safe.
