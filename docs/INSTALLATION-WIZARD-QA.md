# Installation Wizard QA

## Required prerequisites

- [x] ChatGPT or Codex and Notion are shown first as the two mandatory products.
- [x] The guide states that Notion must be connected to the intended account and workspace before installation.
- [x] Mandatory account steps show a disabled `Not done — continue` control.

## Wizard behavior

- [x] The user chooses ChatGPT or Codex Desktop.
- [x] Instructions branch according to that choice.
- [x] Optional integrations may be selected or skipped.
- [x] Progress is kept in local browser storage only.
- [x] Back, restart, pause, resume and quit paths are present.
- [x] A complete no-JavaScript manual guide remains available.

## Product truthfulness

- [x] Notion is the only mandatory external integration.
- [x] The current stable Markdown creator remains the public download target.
- [x] Planned Phase 1 capabilities are described as upcoming, not released.
- [x] No private Workspace IDs, account identities or personal records are present.
- [x] High-risk optional capabilities are not presented as autonomous defaults.

## Accessibility and responsive behavior

- [x] Native buttons and form controls are keyboard-accessible.
- [x] Disabled mandatory-skip buttons use the actual `disabled` state.
- [x] Progress announcements use an ARIA live region.
- [x] Focus-visible styling is provided.
- [x] Mobile layouts collapse to a single-column flow.
- [x] Reduced-motion preferences are respected.

## Static verification performed

- JavaScript syntax checked with `node --check`.
- HTML parsed with Python's standard HTML parser.
- Required copy, controls, assets and privacy exclusions asserted.
- Homepage and product page checked for the requested large use-case and benefit sections.
