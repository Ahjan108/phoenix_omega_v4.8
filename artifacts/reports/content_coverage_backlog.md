# Content Coverage Backlog (STORY Band Coverage)

- Source: `/Users/ahjan/phoenix_omega/config/source_of_truth/master_arcs` + `/Users/ahjan/phoenix_omega/atoms`
- Rule used: target `>= 2` STORY atoms per required band (per persona/topic/engine)
- Arc tuples analyzed: `4`
- Generated files: `/Users/ahjan/phoenix_omega/artifacts/reports/content_coverage_backlog.md` and `/Users/ahjan/phoenix_omega/artifacts/reports/content_coverage_backlog.csv`

## Snapshot
- MISSING (required band absent): `0`
- LOW (present but below target): `0`
- OK: `4`

## Persona/Topic Priority (by total deficit)
| Persona | Topic | Engines | Missing Engines | Total Deficit | Required Bands |
|---|---:|---:|---:|---:|---|
| educators | anxiety | 1 | 0 | 0 | 2,3,4 |
| gen_z_professionals | anxiety | 1 | 0 | 0 | 1,2,3,4 |
| nyc_executives | boundaries | 1 | 0 | 0 | 2,3,4,5 |
| nyc_executives | self_worth | 1 | 0 | 0 | 2,3,4,5 |

## Engine-Level Backlog (highest deficit first)
| Status | Persona | Topic | Engine | Required Bands | Counts (B1/B2/B3/B4/B5) | Deficits (B1/B2/B3/B4/B5) | Deficit Total |
|---|---|---|---|---|---|---|---:|
| OK | educators | anxiety | overwhelm | 2,3,4 | 5/5/5/5/0 | 0/0/0/0/0 | 0 |
| OK | gen_z_professionals | anxiety | overwhelm | 1,2,3,4 | 2/5/9/4/0 | 0/0/0/0/0 | 0 |
| OK | nyc_executives | boundaries | shame | 2,3,4,5 | 5/5/5/5/5 | 0/0/0/0/0 | 0 |
| OK | nyc_executives | self_worth | shame | 2,3,4,5 | 5/5/5/3/2 | 0/0/0/0/0 | 0 |
## Arc Coverage Gaps (cannot band-validate yet)
- Active personas: `4`
- Active topics: `8`
- Missing persona/topic/engine arc tuples: `101`
- Detail CSV: `/Users/ahjan/phoenix_omega/artifacts/reports/content_coverage_arc_gaps.csv`
