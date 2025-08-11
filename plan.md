# Plan

## Goal
Support multiple FetLife accounts with per-subscription selection and session isolation.

## Constraints
- Preserve existing command structure; add `/fl account` subcommands and optional account selection for `/fl subscribe`.
- Avoid storing plaintext credentials; persist only SHA-256 hashes.
- Maintain backward compatibility for adapter requests without an explicit account ID.

## Risks
- Incorrect session handling in the adapter could mix account cookies.
- Added account_id parameter may break existing tests if not patched.
- Hashing approach may not satisfy future security expectations.

## Test Plan
- `make check`

## Semver
Minor: new backwards-compatible feature set.
