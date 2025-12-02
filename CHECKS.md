# modelChecker - Checks Reference

This document describes all available checks in modelChecker, including the academic extension checks.

---

## Table of Contents

- [Original Checks](#original-checks)
  - [Naming](#naming)
  - [General](#general)
  - [Topology](#topology)
  - [UVs](#uvs)
- [Academic Extension Checks](#academic-extension-checks)
  - [Flipped Normals](#flipped-normals)
  - [Overlapping Vertices](#overlapping-vertices)
  - [Poly Count Limit](#poly-count-limit)

---

## Original Checks

### Naming

| Check | Description |
|-------|-------------|
| **Trailing Numbers** | Detects nodes with numeric suffixes (e.g., `pCube1`) |
| **Duplicated Names** | Finds multiple nodes sharing the same short name |
| **Shape Names** | Validates shape node naming convention (`<transform>Shape`) |
| **Namespaces** | Identifies nodes within namespaces |

### General

| Check | Description |
|-------|-------------|
| **Layers** | Detects nodes assigned to display layers |
| **History** | Finds meshes with construction history |
| **Shaders** | Identifies nodes with non-default shaders |
| **Unfrozen Transforms** | Detects transforms not at identity (T≠0, R≠0, S≠1) |
| **Uncentered Pivots** | Finds pivots not at world origin |
| **Parent Geometry** | Detects transform nodes with mesh children |
| **Empty Groups** | Identifies groups with no descendants |

### Topology

| Check | Description |
|-------|-------------|
| **Triangles** | Detects 3-sided polygons |
| **Ngons** | Finds polygons with more than 4 sides |
| **Open Edges** | Identifies boundary edges (less than 2 connected faces) |
| **Poles** | Detects vertices with more than 5 connected edges |
| **Hard Edges** | Finds non-smooth interior edges |
| **Lamina** | Identifies coplanar overlapping faces |
| **Zero Area Faces** | Detects degenerate faces with no area |
| **Zero Length Edges** | Finds edges with no length |
| **Non-Manifold Edges** | Identifies edges with more than 2 connected faces |
| **Starlike** | Detects non-star-shaped (self-intersecting) faces |

### UVs

| Check | Description |
|-------|-------------|
| **Self Penetrating UVs** | Detects overlapping UV islands |
| **Missing UVs** | Finds polygons without UV coordinates |
| **UV Range** | Identifies UVs outside standard range (0-10) |
| **Cross Border** | Detects UVs crossing integer boundaries (tiling issues) |
| **On Border** | Finds UVs aligned exactly to integer borders |

---

## Academic Extension Checks

These checks were added to support academic evaluation criteria for digital design courses.

---

### Flipped Normals

**Category:** Topology
**Function:** `flippedNormals`
**Returns:** Polygon faces

#### Description

Detects faces with normals pointing inward (reversed/flipped normals). Flipped normals typically cause:
- Black faces in renders
- Incorrect lighting calculations
- Issues with backface culling
- Problems when exporting to game engines

#### How It Works

1. Calculates mesh bounding box center as reference point (object space)
2. For each face, gets its center and normal in object space
3. Calculates vector from mesh center to face center
4. If dot product of normal and this vector is negative, the normal points inward

All calculations are performed in object space, ensuring correct results regardless of the mesh's transform (translation, rotation, scale).

#### Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Uses bounding box center | May give false positives on highly concave meshes | Review flagged faces manually |
| Designed for convex/mostly-convex geometry | Complex concave shapes may have legitimate inward-facing areas | Use Maya's Mesh Display > Face Normals for verification |

#### When This Check Helps

- **Student projects**: Catches accidental normal reversals from boolean operations or incorrect extrusions
- **Game assets**: Ensures proper backface culling behavior
- **Rendering**: Prevents black face artifacts in final renders

#### When to Ignore Results

- Intentionally concave geometry (e.g., interior of a room)
- Double-sided materials where normal direction doesn't matter
- Stylized models with intentional inverted sections

#### How to Fix

In Maya:
1. Select the flagged faces
2. Go to **Mesh Display > Reverse** or press the reverse normals button
3. Re-run the check to verify

#### Test Cases

| Test | Expected Result |
|------|-----------------|
| Clean cube at origin | PASS (0 flipped faces) |
| Cube with all normals reversed | FAIL (6 flipped faces) |
| Sphere with some reversed faces | FAIL (reports specific faces) |
| Empty selection | PASS (graceful handling) |
| Translated cube (clean normals) | PASS (0 flipped faces) |
| Rotated cube (clean normals) | PASS (0 flipped faces) |
| Scaled cube (clean normals) | PASS (0 flipped faces) |
| Combined transforms (clean normals) | PASS (0 flipped faces) |

---

### Overlapping Vertices

**Category:** Topology
**Function:** `overlappingVertices`
**Returns:** Vertex indices

#### Description

Detects vertices that occupy the same spatial position within a tolerance threshold (0.0001 units). Overlapping vertices are a common issue that causes:
- Shading artifacts (pinching, dark spots)
- Problems with edge flow and topology
- Export issues (FBX, OBJ may produce unexpected results)
- Difficulty with proper welding/merging

#### How It Works

1. Gets all vertex positions using MFnMesh.getPoints()
2. Builds a spatial hash grid for efficient O(n) comparison
3. For each vertex, checks nearby vertices within tolerance
4. Reports all vertices that share positions with other vertices

The spatial hash approach ensures the check runs efficiently even on high-poly meshes by avoiding O(n^2) comparisons.

#### Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Fixed tolerance (0.0001) | Very small models may not detect close vertices | Scale up model temporarily for checking |
| UV seam vertices | Intentional overlaps at UV seams will be flagged | Review flagged vertices - seam overlaps are expected |
| Blend shape vertices | Intentionally stacked vertices for morphing | Verify if overlaps are part of deformation setup |

#### When This Check Helps

- **After combining meshes**: Catches vertices that weren't merged after polyUnite
- **Boolean operations**: Booleans often leave stacked vertices at intersection edges
- **Imported geometry**: Some file formats create duplicate vertices
- **Cleanup before export**: Ensures clean geometry for game engines

#### When to Ignore Results

- UV seam boundaries (vertices at same position with different UVs)
- Blend shape base meshes with intentional stacking
- Geometry intended for specific deformation rigs

#### How to Fix

In Maya:
1. Select the mesh
2. Go to **Edit Mesh > Merge > Merge Vertices**
3. Set threshold to match check tolerance (0.0001)
4. Or use **Mesh > Cleanup** with "Merge vertices" option
5. Re-run the check to verify

#### Test Cases

| Test | Expected Result |
|------|-----------------|
| Clean cube | PASS (0 overlapping vertices) |
| Combined cubes without merge | FAIL (8 overlapping vertices at shared face) |
| Vertex extruded with length 0 | FAIL (2 stacked vertices) |
| Empty selection | PASS (graceful handling) |
| Clean sphere | PASS (0 overlapping vertices) |

---

### Poly Count Limit

**Category:** General
**Function:** `polyCountLimit`
**Returns:** Nodes (entire meshes that exceed limit)

#### Description

Detects meshes that exceed a configurable polygon count limit. This is essential for academic projects where assignments typically have strict polygon budgets. Exceeding the limit usually results in point deductions.

Default limit: **10,000 polygons per mesh**

#### How It Works

1. For each mesh in the selection, get the polygon count using MFnMesh.numPolygons
2. Compare against the configured limit (default: 10,000)
3. Flag entire meshes that exceed the limit

#### Configuration

To change the polygon limit, edit `modelChecker_commands.py`:

```python
# Find this line near the polyCountLimit function:
POLY_COUNT_LIMIT = 10000  # Change this value

# Common academic limits:
# Game character: 5000 - 15000
# Game prop: 500 - 5000
# Environment asset: 10000 - 50000
```

#### Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| Per-mesh limit only | Doesn't check total scene polygon count | Manually sum poly counts if needed |
| No UI configuration | Must edit code to change limit | Edit POLY_COUNT_LIMIT in commands file |
| Instances counted separately | Each instance counts toward limit | Expected Maya behavior |
| Subdivision not included | Preview subdivision levels not counted | Check at base mesh level |

#### When This Check Helps

- **Academic submissions**: Most 3D assignments have polygon budgets
- **Game assets**: Real-time rendering requires optimized meshes
- **Mobile/VR projects**: Strict performance requirements
- **Before final submission**: Catch over-detailed models early

#### How to Fix

If a mesh exceeds the polygon limit:

1. **Reduce edge loops**: Delete unnecessary edge loops with Edit Mesh > Delete Edge
2. **Retopologize**: Use Mesh > Retopologize or manual cleanup
3. **Simplify details**: Remove geometric details that could be normal maps
4. **Use LODs**: Create lower-poly versions for distance rendering
5. **Polygon reduction**: Mesh > Reduce (use with caution)

To check polygon count manually:
- Select mesh → Display > Heads Up Display > Poly Count

#### Test Cases

| Test | Expected Result |
|------|-----------------|
| Low-poly cube (6 faces) | PASS |
| High-poly sphere (2500+ faces) | FAIL (with limit 1000) |
| Mesh exactly at limit | PASS (uses > not >=) |
| Mesh one over limit | FAIL |
| Empty selection | PASS (graceful handling) |
| Multiple meshes (mixed) | Only over-limit meshes flagged |

---

## Adding New Checks

To add a new check to modelChecker:

1. Add the check function to `modelChecker_commands.py`:
   ```python
   def myCheck(nodes, SLMesh):
       """Docstring with description and limitations."""
       errors = defaultdict(list)
       # ... check logic ...
       return ("polygon", errors)  # or "nodes", "vertex", "edge", "uv"
   ```

2. Register in `modelChecker_list.py`:
   ```python
   "myCheck": {
       'label': 'My Check',
       'category': 'topology',  # or 'naming', 'general', 'UVs'
   }
   ```

3. Document in this file with known limitations

4. Add tests in `tests/test_<check_name>.py`

---

## Version History

| Version | Changes |
|---------|---------|
| 0.1.4 | Original release with 27 checks |
| 0.2.0 | Academic extension: Added flippedNormals check |
| 0.2.1 | Academic extension: Added overlappingVertices check |
| 0.2.2 | Academic extension: Added polyCountLimit check |
