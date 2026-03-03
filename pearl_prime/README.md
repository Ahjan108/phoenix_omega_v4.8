# Pearl Prime

`pearl_prime` is the modular template/output layer for Omega V4.x.

Scope:

- Owns modular output-format freeze policy and allowed output format catalog.
- Can call existing V4 systems (arc loader, variation selector, compiler, gates) outside `pearl_prime/`.
- Blocks legacy output format selection when freeze is enabled, while preserving V4 variation controls.

Current integration point:

- `scripts/run_pipeline.py` imports `pearl_prime.modular_format_freeze`.

Config:

- `pearl_prime/config/v4_freeze_modular_formats.yaml`

