# Feature and Integration Registry contract

Feature records expose a stable feature key, display name, core or optional classification, owner decision and timestamp, required capabilities, dependencies, selected provider, supported surfaces, risk tier, activation policy, health state, read/write scope, output destination, and persistence policy.

Required states are `Enabled`, `Disabled by User`, `Unavailable`, `Pending Setup`, `Paused`, and `Degraded`. No upgrade may silently enable a disabled capability or switch a selected provider.
