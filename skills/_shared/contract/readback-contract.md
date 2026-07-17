# Readback contract

A connector-backed write is successful only after the resulting object is read back and its identity, parent, critical properties, and links are verified. Partial or truncated reads are reported as incomplete.

If a selected artifact archive such as Drive is enabled, completion requires exact-file upload and readback. If readback fails, report an incomplete state instead of success.
