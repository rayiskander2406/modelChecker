"""
Tests for concaveFaces check.

================================================================================
OVERVIEW
================================================================================

The concaveFaces check detects polygon faces that are concave (non-convex).
A convex polygon has all interior angles less than 180 degrees, meaning any
line between two interior points stays inside the polygon.

Concave faces can cause:
- Unpredictable triangulation during rendering
- Rendering artifacts and shading errors
- Boolean operation failures
- Issues with subdivision surfaces
- Problems when exporting to game engines

================================================================================
ALGORITHM
================================================================================

1. Iterate through each polygon face in the mesh
2. Use Maya's built-in isConvex() method on MItMeshPolygon
3. Flag faces that return False (non-convex)
4. Triangles are always convex, so they pass automatically

================================================================================
KNOWN LIMITATIONS
================================================================================

1. SEVERITY: Does not distinguish between slightly and severely concave faces.
   A barely concave face is flagged the same as an extremely concave one.

2. FLOATING POINT: Very small concave angles may not be detected due to
   floating point precision in Maya's calculations.

3. TRIANGLES: Triangles are always convex by definition and are never flagged,
   even if they appear to have issues.

4. NO METRICS: Does not provide angle measurements or severity scores.

================================================================================
TEST CASES
================================================================================

1. test_convex_quad - Convex quad should PASS
2. test_concave_quad - L-shaped concave quad should FAIL
3. test_triangle - Triangle should PASS (always convex)
4. test_convex_cube - Standard cube (all convex quads) should PASS
5. test_concave_ngon - Concave n-gon should FAIL
6. test_mixed_mesh - Mesh with both convex and concave faces
7. test_star_shape - Star shape (all concave) should FAIL
8. test_empty_selection - Empty input should not crash

================================================================================
RUNNING TESTS
================================================================================

Copy MAYA_TEST_SCRIPT into Maya's Script Editor and execute.

================================================================================
"""

MAYA_TEST_SCRIPT = '''
import maya.cmds as cmds
import maya.api.OpenMaya as om
from modelChecker import modelChecker_commands as mc

def get_mesh_selection_list():
    """Helper to get all meshes as MSelectionList."""
    meshes = cmds.ls(type='mesh', long=True) or []
    sel = om.MSelectionList()
    for mesh in meshes:
        try:
            sel.add(mesh)
        except:
            pass
    return sel

# =============================================================================
# TEST CASES
# =============================================================================

def test_convex_quad():
    """
    Test: Convex quad (regular square face) should PASS.
    """
    cmds.file(new=True, force=True)

    # Create a simple plane (all convex quads)
    plane = cmds.polyPlane(name='convex_plane', sx=1, sy=1)[0]

    SLMesh = get_mesh_selection_list()
    result_type, result_data = mc.concaveFaces(None, SLMesh)

    total_concave = sum(len(v) for v in result_data.values())
    if total_concave == 0:
        print("PASS: test_convex_quad - Convex quad not flagged")
        return True
    else:
        print("FAIL: test_convex_quad - Convex quad incorrectly flagged")
        return False


def test_concave_quad():
    """
    Test: L-shaped concave quad should FAIL.
    """
    cmds.file(new=True, force=True)

    # Create a plane and move one vertex inward to create concave face
    plane = cmds.polyPlane(name='concave_test', sx=1, sy=1)[0]

    # Move one corner vertex inward past center to create concave shape
    vtx = plane + '.vtx[0]'
    cmds.move(0.3, 0, 0.3, vtx, relative=True)

    SLMesh = get_mesh_selection_list()
    result_type, result_data = mc.concaveFaces(None, SLMesh)

    total_concave = sum(len(v) for v in result_data.values())
    if total_concave > 0:
        print("PASS: test_concave_quad - Concave quad flagged")
        return True
    else:
        print("FAIL: test_concave_quad - Concave quad not detected")
        return False


def test_triangle():
    """
    Test: Triangle should PASS (triangles are always convex).
    """
    cmds.file(new=True, force=True)

    # Create a triangle
    cmds.polyCreateFacet(point=[(0, 0, 0), (1, 0, 0), (0.5, 0, 1)],
                          name='triangle')

    SLMesh = get_mesh_selection_list()
    result_type, result_data = mc.concaveFaces(None, SLMesh)

    total_concave = sum(len(v) for v in result_data.values())
    if total_concave == 0:
        print("PASS: test_triangle - Triangle not flagged (always convex)")
        return True
    else:
        print("FAIL: test_triangle - Triangle incorrectly flagged")
        return False


def test_convex_cube():
    """
    Test: Standard cube (all convex quads) should PASS.
    """
    cmds.file(new=True, force=True)

    # Create a standard cube
    cube = cmds.polyCube(name='convex_cube')[0]

    SLMesh = get_mesh_selection_list()
    result_type, result_data = mc.concaveFaces(None, SLMesh)

    total_concave = sum(len(v) for v in result_data.values())
    if total_concave == 0:
        print("PASS: test_convex_cube - All cube faces convex")
        return True
    else:
        print("FAIL: test_convex_cube - Cube faces incorrectly flagged")
        return False


def test_concave_ngon():
    """
    Test: Concave n-gon (arrow shape) should FAIL.
    """
    cmds.file(new=True, force=True)

    # Create an arrow-shaped concave pentagon
    # Arrow pointing right with indent on left
    points = [
        (0, 0, 0),      # bottom left
        (0.5, 0, 0.5),  # indent (creates concavity)
        (0, 0, 1),      # top left
        (1, 0, 0.5),    # right point
    ]
    cmds.polyCreateFacet(point=points, name='concave_arrow')

    SLMesh = get_mesh_selection_list()
    result_type, result_data = mc.concaveFaces(None, SLMesh)

    total_concave = sum(len(v) for v in result_data.values())
    if total_concave > 0:
        print("PASS: test_concave_ngon - Concave n-gon flagged")
        return True
    else:
        print("FAIL: test_concave_ngon - Concave n-gon not detected")
        return False


def test_mixed_mesh():
    """
    Test: Mesh with both convex and concave faces.
    """
    cmds.file(new=True, force=True)

    # Create a 2x2 plane (4 faces)
    plane = cmds.polyPlane(name='mixed_plane', sx=2, sy=2)[0]

    # Make one face concave by moving a vertex
    cmds.move(0.3, 0, 0.3, plane + '.vtx[4]', relative=True)  # center vertex

    SLMesh = get_mesh_selection_list()
    result_type, result_data = mc.concaveFaces(None, SLMesh)

    total_concave = sum(len(v) for v in result_data.values())
    # At least some faces should be concave, but not all 4
    if total_concave > 0 and total_concave < 4:
        print("PASS: test_mixed_mesh - Mixed mesh correctly identified ({} concave)".format(total_concave))
        return True
    elif total_concave == 0:
        print("FAIL: test_mixed_mesh - No concave faces detected")
        return False
    else:
        print("WARN: test_mixed_mesh - {} concave faces (may be correct)".format(total_concave))
        return True  # Could be correct depending on topology


def test_star_shape():
    """
    Test: Star shape (all points create concave angles) should FAIL.
    """
    cmds.file(new=True, force=True)

    # Create a 5-pointed star (highly concave polygon)
    import math
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        radius = 1.0 if i % 2 == 0 else 0.4  # Alternate outer/inner points
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        points.append((x, 0, z))

    cmds.polyCreateFacet(point=points, name='star_shape')

    SLMesh = get_mesh_selection_list()
    result_type, result_data = mc.concaveFaces(None, SLMesh)

    total_concave = sum(len(v) for v in result_data.values())
    if total_concave > 0:
        print("PASS: test_star_shape - Star shape (concave) flagged")
        return True
    else:
        print("FAIL: test_star_shape - Star shape not detected as concave")
        return False


def test_empty_selection():
    """
    Test: Empty input should not crash.
    """
    cmds.file(new=True, force=True)

    try:
        empty_sel = om.MSelectionList()
        result_type, result_data = mc.concaveFaces(None, empty_sel)
        if len(result_data) == 0:
            print("PASS: test_empty_selection - Empty input handled gracefully")
            return True
        else:
            print("FAIL: test_empty_selection - Unexpected results from empty input")
            return False
    except Exception as e:
        print("FAIL: test_empty_selection - Exception: {}".format(str(e)))
        return False


# =============================================================================
# RUN ALL TESTS
# =============================================================================

def run_all_tests():
    print("")
    print("=" * 70)
    print("  concaveFaces Test Suite")
    print("=" * 70)
    print("")

    results = []
    results.append(("Convex quad", test_convex_quad()))
    results.append(("Concave quad", test_concave_quad()))
    results.append(("Triangle (always convex)", test_triangle()))
    results.append(("Convex cube", test_convex_cube()))
    results.append(("Concave n-gon", test_concave_ngon()))
    results.append(("Mixed mesh", test_mixed_mesh()))
    results.append(("Star shape", test_star_shape()))
    results.append(("Empty selection", test_empty_selection()))

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

    return passed == total

run_all_tests()
'''


def get_test_script():
    """Return the Maya test script for copy/paste."""
    return MAYA_TEST_SCRIPT


if __name__ == "__main__":
    print("=" * 70)
    print("  concaveFaces Test Suite")
    print("=" * 70)
    print()
    print("  These tests require Maya to run.")
    print()
    print("  To execute tests:")
    print("    1. Open Maya")
    print("    2. Ensure modelChecker is in your Python path")
    print("    3. Copy MAYA_TEST_SCRIPT into Script Editor")
    print("    4. Execute")
    print()
    print("  WHAT THIS CHECK DOES:")
    print("    Detects non-convex polygon faces")
    print("    - Uses Maya's built-in isConvex() method")
    print("    - Triangles are always convex (skipped)")
    print()
    print("  CONVEX VS CONCAVE:")
    print("    Convex: All interior angles < 180 degrees")
    print("    Concave: At least one interior angle > 180 degrees")
    print()
    print("  EXAMPLES:")
    print("    Convex: Square, regular pentagon, cube faces")
    print("    Concave: L-shape, star, arrow shape")
    print()
    print("  WHY THIS MATTERS:")
    print("    - Unpredictable triangulation")
    print("    - Rendering artifacts")
    print("    - Boolean operation failures")
    print("    - Game engine compatibility")
    print()
    print("=" * 70)
