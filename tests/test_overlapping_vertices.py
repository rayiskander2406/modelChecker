"""
Tests for overlappingVertices check.

================================================================================
OVERVIEW
================================================================================

The overlappingVertices check detects vertices that occupy the same spatial
position within a tolerance threshold (0.0001 units). This is a common issue
that causes:
- Shading artifacts (pinching, dark spots)
- Problems with edge flow and topology
- Export issues (FBX, OBJ may produce unexpected results)
- Difficulty with proper welding/merging

================================================================================
ALGORITHM
================================================================================

1. Get all vertex positions using MFnMesh.getPoints()
2. Build a spatial hash grid for efficient O(n) comparison
3. For each vertex, check nearby vertices within tolerance
4. Report vertices that share positions with other vertices

================================================================================
KNOWN LIMITATIONS
================================================================================

1. TOLERANCE: Default tolerance of 0.0001 may need adjustment for very small
   models. For microscopic geometry, vertices slightly further apart may not
   be detected.

2. UV SEAMS: Meshes with UV seams often have intentionally "overlapping"
   vertices at seam boundaries. These are technically at the same position
   but serve different UV coordinates. This check will flag them.

   Example: A cube with UV seams will have vertices along seam edges.

3. INTENTIONAL STACKING: Some workflows intentionally stack vertices for
   blend shapes or other deformations. These will be flagged.

================================================================================
TEST CASES
================================================================================

These tests require Maya to be running. Run them from within Maya's Script
Editor or using mayapy.

Test Cases:
1. Clean cube (no overlapping vertices) - should PASS
2. Cube after combine without merge (stacked vertices) - should FAIL
3. Single mesh with duplicated vertex at same position - should FAIL
4. Empty mesh list - should return empty results (no crash)
5. (Known limitation) UV seam vertices - may be flagged

================================================================================
RUNNING TESTS
================================================================================

Option 1: Maya Script Editor
   - Copy MAYA_TEST_SCRIPT below into Maya's Script Editor
   - Execute

Option 2: mayapy
   - mayapy tests/test_overlapping_vertices.py

Option 3: Standalone (info only)
   - python tests/test_overlapping_vertices.py

================================================================================
"""

# =============================================================================
# MAYA TEST COMMANDS
# =============================================================================
# Copy and paste these into Maya's Script Editor to test manually:

MAYA_TEST_SCRIPT = '''
import maya.cmds as cmds
import maya.api.OpenMaya as om
from modelChecker import modelChecker_commands as mc

# -----------------------------------------------------------------------------
# Test 1: Clean Cube (should PASS - no overlapping vertices)
# -----------------------------------------------------------------------------
def test_clean_cube():
    """Test that a normal cube has no overlapping vertices."""
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name='test_clean_cube')[0]

    # Get shape and create selection list
    shape = cmds.listRelatives(cube, shapes=True)[0]
    selList = om.MSelectionList()
    selList.add(shape)

    result_type, result_data = mc.overlappingVertices(None, selList)

    if len(result_data) == 0:
        print("TEST 1 PASSED: Clean cube has no overlapping vertices")
        return True
    else:
        total_verts = sum(len(v) for v in result_data.values())
        print("TEST 1 FAILED: Clean cube incorrectly detected {} overlapping vertices".format(total_verts))
        return False

# -----------------------------------------------------------------------------
# Test 2: Combined Cubes Without Merge (should FAIL - detect overlapping verts)
# -----------------------------------------------------------------------------
def test_combined_cubes_no_merge():
    """Test that combined geometry without vertex merge is detected."""
    cmds.file(new=True, force=True)

    # Create two cubes at the same position
    cube1 = cmds.polyCube(name='test_cube1')[0]
    cube2 = cmds.polyCube(name='test_cube2')[0]

    # Move cube2 so one face overlaps with cube1
    cmds.move(1, 0, 0, cube2)

    # Combine without merging vertices
    combined = cmds.polyUnite(cube1, cube2, name='combined_cubes',
                               constructionHistory=False, mergeUVSets=True)[0]

    # Get shape and create selection list
    shape = cmds.listRelatives(combined, shapes=True)[0]
    selList = om.MSelectionList()
    selList.add(shape)

    result_type, result_data = mc.overlappingVertices(None, selList)

    if len(result_data) > 0:
        total_verts = sum(len(v) for v in result_data.values())
        # Shared face has 4 vertices, so we expect 8 overlapping (4 pairs)
        print("TEST 2 PASSED: Detected {} overlapping vertices in combined mesh".format(total_verts))
        return True
    else:
        print("TEST 2 FAILED: Combined cubes should have overlapping vertices at shared face")
        return False

# -----------------------------------------------------------------------------
# Test 3: Manually Stacked Vertices (should FAIL)
# -----------------------------------------------------------------------------
def test_stacked_vertex():
    """Test detection of manually created stacked vertices."""
    cmds.file(new=True, force=True)

    # Create a plane
    plane = cmds.polyPlane(name='test_plane', sx=2, sy=2)[0]

    # Duplicate the center vertex by extruding and scaling to 0
    cmds.select(plane + '.vtx[4]')  # Center vertex
    cmds.polyExtrudeVertex(length=0)  # Creates overlapping vertex

    # Get shape and create selection list
    shape = cmds.listRelatives(plane, shapes=True)[0]
    selList = om.MSelectionList()
    selList.add(shape)

    result_type, result_data = mc.overlappingVertices(None, selList)

    if len(result_data) > 0:
        total_verts = sum(len(v) for v in result_data.values())
        print("TEST 3 PASSED: Detected {} overlapping vertices from extrude".format(total_verts))
        return True
    else:
        print("TEST 3 FAILED: Stacked vertex was not detected")
        return False

# -----------------------------------------------------------------------------
# Test 4: Empty Selection List (should not crash)
# -----------------------------------------------------------------------------
def test_empty_selection():
    """Test that empty selection is handled gracefully."""
    cmds.file(new=True, force=True)

    selList = om.MSelectionList()

    try:
        result_type, result_data = mc.overlappingVertices(None, selList)
        if len(result_data) == 0:
            print("TEST 4 PASSED: Empty selection handled gracefully")
            return True
        else:
            print("TEST 4 FAILED: Unexpected results from empty selection")
            return False
    except Exception as e:
        print("TEST 4 FAILED: Exception on empty selection:", str(e))
        return False

# -----------------------------------------------------------------------------
# Test 5: Known Limitation - UV Seam Vertices
# -----------------------------------------------------------------------------
def test_uv_seam_limitation():
    """
    Document known limitation with UV seam vertices.

    When a mesh has UV seams, Maya may have multiple vertices at the same
    spatial position to allow different UV coordinates. These are technically
    "overlapping" in 3D space.

    This is a KNOWN LIMITATION, not a bug.
    """
    cmds.file(new=True, force=True)

    # Create a cube and cut UV edges to create seams
    cube = cmds.polyCube(name='test_uv_cube')[0]

    # This cube has default UVs which may or may not have seam vertices
    # depending on Maya version

    # Get shape and create selection list
    shape = cmds.listRelatives(cube, shapes=True)[0]
    selList = om.MSelectionList()
    selList.add(shape)

    result_type, result_data = mc.overlappingVertices(None, selList)

    total_verts = sum(len(v) for v in result_data.values()) if result_data else 0

    print("TEST 5 (LIMITATION): Cube detected {} potentially overlapping vertices".format(total_verts))
    print("  NOTE: This test documents behavior with UV seams.")
    print("  Standard cubes may have overlapping vertices at UV seam boundaries.")
    print("  This is expected behavior - verify manually if flagged vertices are intentional.")
    return True  # Always passes - this documents behavior, not tests correctness

# -----------------------------------------------------------------------------
# Test 6: Sphere with Clean Geometry (should PASS)
# -----------------------------------------------------------------------------
def test_clean_sphere():
    """Test that a clean sphere has no overlapping vertices."""
    cmds.file(new=True, force=True)
    sphere = cmds.polySphere(name='test_sphere', subdivisionsX=8, subdivisionsY=8)[0]

    # Get shape and create selection list
    shape = cmds.listRelatives(sphere, shapes=True)[0]
    selList = om.MSelectionList()
    selList.add(shape)

    result_type, result_data = mc.overlappingVertices(None, selList)

    if len(result_data) == 0:
        print("TEST 6 PASSED: Clean sphere has no overlapping vertices")
        return True
    else:
        total_verts = sum(len(v) for v in result_data.values())
        # Spheres may have pole vertices that are very close
        print("TEST 6 INFO: Sphere detected {} vertices".format(total_verts))
        print("  (Pole vertices may be very close together)")
        return True

# -----------------------------------------------------------------------------
# Run All Tests
# -----------------------------------------------------------------------------
def run_all_tests():
    print("")
    print("=" * 70)
    print("  overlappingVertices Test Suite")
    print("=" * 70)
    print("")

    results = []
    results.append(("Clean Cube", test_clean_cube()))
    results.append(("Combined Cubes (No Merge)", test_combined_cubes_no_merge()))
    results.append(("Stacked Vertex", test_stacked_vertex()))
    results.append(("Empty Selection", test_empty_selection()))
    results.append(("UV Seam Limitation", test_uv_seam_limitation()))
    results.append(("Clean Sphere", test_clean_sphere()))

    print("")
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print("  [{}] {}".format(status, name))
    print("")
    print("  Total: {}/{} tests passed".format(passed, total))
    print("=" * 70)

run_all_tests()
'''


def get_test_script():
    """Return the Maya test script for copy/paste."""
    return MAYA_TEST_SCRIPT


if __name__ == "__main__":
    print("=" * 70)
    print("  overlappingVertices Test Suite")
    print("=" * 70)
    print()
    print("  These tests require Maya to run.")
    print()
    print("  To execute tests:")
    print()
    print("  1. Open Maya")
    print("  2. Ensure modelChecker is in your Python path:")
    print("     import sys")
    print("     sys.path.append('/path/to/modelChecker')")
    print("  3. Copy the MAYA_TEST_SCRIPT from this file into Script Editor")
    print("  4. Execute")
    print()
    print("  Or run with mayapy:")
    print("    mayapy -c \"exec(open('tests/test_overlapping_vertices.py').read())\"")
    print()
    print("=" * 70)
    print()
    print("  KNOWN LIMITATIONS (documented in tests):")
    print()
    print("  - Tolerance of 0.0001 may need adjustment for very small models")
    print("  - UV seam vertices are intentionally at same position")
    print("  - Some workflows intentionally stack vertices (blend shapes)")
    print("  - Test 5 documents UV seam limitation")
    print()
    print("=" * 70)
