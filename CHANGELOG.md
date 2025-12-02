# Changelog

All notable changes to the mayaLint Academic Extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Phase 1 (High Impact): 5 remaining checks
- Phase 2 (Professional Quality): 5 checks
- Phase 3 (Polish): 4 checks

---

## [0.2.0] - 2025-12-02

### Added

#### New Check: Flipped Normals (#1/15)
- **Function:** `flippedNormals()`
- **Category:** topology
- **Description:** Detects faces with normals pointing inward (reversed) that cause black faces in renders
- **Algorithm:** Compares face normal direction against vector from mesh center to face center
- **Tests:** 5 test cases including limitation documentation

#### Project Infrastructure
- `.claude/release-plan.json` - Comprehensive project state tracking
- `.claude/commands/` - Slash commands for workflow management:
  - `/plan-release` - View implementation roadmap
  - `/dashboard` - Visual progress dashboard
  - `/start <check_id>` - Begin implementing a check
  - `/finish <check_id>` - Complete and commit a check
  - `/update-preview` - Update UI preview
- `tests/` directory for Maya test scripts
- `CHECKS.md` - Comprehensive check documentation
- `CONTRIBUTING.md` - Contribution guidelines
- `CHANGELOG.md` - This file

#### UI Preview
- `ui-preview/index.html` - Interactive mockup of extended mayaLint
- `ui-preview/checks-overview.html` - 1-pager explaining all 15 new checks
- Deployed to Vercel with mobile-responsive design
- Preview URL: https://modelchecker-preview-guhxbb6ow-rayiskander2406s-projects.vercel.app

#### New Categories (Planned)
- `materials` - Texture and material validation (3 checks planned)
- `scene` - Scene-level settings validation (2 checks planned)

### Changed
- Extended `mayaLint_commands.py` with new check function
- Extended `mayaLint_list.py` with new check registration

---

## [0.1.4] - Original Release

### Original Features (27 checks)

#### Naming (4 checks)
- Trailing Numbers
- Duplicated Names
- Shape Names
- Namespaces

#### General (7 checks)
- Layers
- History
- Shaders
- Unfrozen Transforms
- Uncentered Pivots
- Parent Geometry
- Empty Groups

#### Topology (10 checks)
- Triangles
- Ngons
- Open Edges
- Poles
- Hard Edges
- Lamina
- Zero Area Faces
- Zero Length Edges
- Non-Manifold Edges
- Starlike

#### UVs (6 checks)
- Self Penetrating UVs
- Missing UVs
- UV Range
- Cross Border
- On Border

---

## Version History Summary

| Version | Checks | Description |
|---------|--------|-------------|
| 0.1.4 | 27 | Original mayaLint release |
| 0.2.0 | 28 | Academic Extension begins (+1 check) |
| 0.3.0 | 33 | Phase 1 complete (planned) |
| 0.4.0 | 38 | Phase 2 complete (planned) |
| 1.0.0 | 42 | Full Academic Extension (planned) |

---

## Links

- [Original modelChecker](https://github.com/JakobJK/modelChecker)
- [MayaLint Academic Extension](https://github.com/rayiskander2406/modelChecker)
- [UI Preview](https://modelchecker-preview-guhxbb6ow-rayiskander2406s-projects.vercel.app)
- [Checks Overview](https://modelchecker-preview-guhxbb6ow-rayiskander2406s-projects.vercel.app/checks-overview.html)
