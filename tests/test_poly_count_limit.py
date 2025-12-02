"""
Tests for polyCountLimit check.

================================================================================
OVERVIEW
================================================================================

The polyCountLimit check detects meshes that exceed a configurable polygon
count limit. This is essential for academic projects where assignments
typically have strict polygon budgets.

Default limit: 10,000 polygons per mesh

================================================================================
ALGORITHM
================================================================================

1. For each mesh in selection, get polygon count using MFnMesh.numPolygons
2. Compare against configured limit (default: 10,000)
3. Flag meshes that exceed the limit

================================================================================
KNOWN LIMITATIONS
================================================================================

1. PER-MESH LIMIT: Checks each mesh individually, not total scene count.
   A scene with 10 meshes of 5,000 polys each (50,000 total) would pass
   if the limit is 10,000.

2. INSTANCES: Each instance is counted separately (Maya behavior).

3. SUBDIVISION: Subdivision preview levels are not included in count.
   The check uses the base mesh polygon count.

4. CONFIGURATION: The limit is set via POLY_COUNT_LIMIT variable in
   modelChecker_commands.py. There's no UI to change it dynamically.

================================================================================
TEST CASES
================================================================================

1. test_low_poly_cube - Simple cube (6 faces) should PASS
2. test_high_poly_sphere - Dense sphere should FAIL
3. test_exactly_at_limit - Mesh with exactly limit polys should PASS
4. test_one_over_limit - Mesh with limit+1 polys should FAIL
5. test_empty_selection - Empty input should not crash
6. test_multiple_meshes - Mix of passing and failing meshes

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

# Store original limit to restore after tests
ORIGINAL_LIMIT = mc.POLY_COUNT_LIMIT

def get_selection_list(shapes):
    """Helper to create MSelectionList from shape names."""
    selList = om.MSelectionList()
    if isinstance(shapes, str):
        shapes = [shapes]
    for shape in shapes:
        selList.add(shape)
    return selList

def count_polys(mesh_name):
    """Helper to count polygons in a mesh."""
    return cmds.polyEvaluate(mesh_name, face=True)

# =============================================================================
# TEST CASES
# =============================================================================

def test_low_poly_cube():
    """
    Test: Simple cube with 6 faces should PASS (under any reasonable limit).
    """
    cmds.file(new=True, force=True)
    mc.POLY_COUNT_LIMIT = 10000  # Reset to default

    cube = cmds.polyCube(name='low_poly_cube')[0]
    shape = cmds.listRelatives(cube, shapes=True)[0]

    poly_count = count_polys(cube)
    result_type, result_data = mc.polyCountLimit(None, get_selection_list(shape))

    if len(result_data) == 0:
        print("PASS: test_low_poly_cube - Cube ({} polys) under limit".format(poly_count))
        return True
    else:
        print("FAIL: test_low_poly_cube - Cube incorrectly flagged")
        return False


def test_high_poly_sphere():
    """
    Test: Dense sphere with many subdivisions should FAIL (exceed limit).
    """
    cmds.file(new=True, force=True)
    mc.POLY_COUNT_LIMIT = 1000  # Set low limit for test

    # Create high-poly sphere (20x20 = ~400 faces, not enough)
    # Need more subdivisions
    sphere = cmds.polySphere(name='high_poly_sphere',
                              subdivisionsX=50,
                              subdivisionsY=50)[0]
    shape = cmds.listRelatives(sphere, shapes=True)[0]

    poly_count = count_polys(sphere)
    result_type, result_data = mc.polyCountLimit(None, get_selection_list(shape))

    if len(result_data) > 0 and poly_count > 1000:
        print("PASS: test_high_poly_sphere - Sphere ({} polys) correctly flagged".format(poly_count))
        return True
    else:
        print("FAIL: test_high_poly_sphere - {} polys, expected to exceed 1000 limit".format(poly_count))
        return False


def test_exactly_at_limit():
    """
    Test: Mesh with exactly the limit should PASS (not exceed).
    The check uses > not >=, so exactly at limit is OK.
    """
    cmds.file(new=True, force=True)

    # Create a plane and set limit to match its poly count
    plane = cmds.polyPlane(name='limit_plane', subdivisionsX=10, subdivisionsY=10)[0]
    shape = cmds.listRelatives(plane, shapes=True)[0]

    poly_count = count_polys(plane)
    mc.POLY_COUNT_LIMIT = poly_count  # Set limit to exactly match

    result_type, result_data = mc.polyCountLimit(None, get_selection_list(shape))

    if len(result_data) == 0:
        print("PASS: test_exactly_at_limit - {} polys at limit {} is OK".format(poly_count, mc.POLY_COUNT_LIMIT))
        return True
    else:
        print("FAIL: test_exactly_at_limit - Mesh at exact limit was incorrectly flagged")
        return False


def test_one_over_limit():
    """
    Test: Mesh with limit+1 polys should FAIL.
    """
    cmds.file(new=True, force=True)

    # Create a plane
    plane = cmds.polyPlane(name='over_limit_plane', subdivisionsX=10, subdivisionsY=10)[0]
    shape = cmds.listRelatives(plane, shapes=True)[0]

    poly_count = count_polys(plane)
    mc.POLY_COUNT_LIMIT = poly_count - 1  # Set limit to one less

    result_type, result_data = mc.polyCountLimit(None, get_selection_list(shape))

    if len(result_data) > 0:
        print("PASS: test_one_over_limit - {} polys exceeds limit {}".format(poly_count, mc.POLY_COUNT_LIMIT))
        return True
    else:
        print("FAIL: test_one_over_limit - Mesh over limit was not flagged")
        return False


def test_empty_selection():
    """
    Test: Empty selection should not crash and return empty results.
    """
    cmds.file(new=True, force=True)
    mc.POLY_COUNT_LIMIT = 10000

    selList = om.MSelectionList()

    try:
        result_type, result_data = mc.polyCountLimit(None, selList)
        if len(result_data) == 0:
            print("PASS: test_empty_selection - Empty selection handled gracefully")
            return True
        else:
            print("FAIL: test_empty_selection - Unexpected results from empty selection")
            return False
    except Exception as e:
        print("FAIL: test_empty_selection - Exception: {}".format(str(e)))
        return False


def test_multiple_meshes():
    """
    Test: Multiple meshes - some pass, some fail.
    """
    cmds.file(new=True, force=True)
    mc.POLY_COUNT_LIMIT = 50  # Low limit

    # Create a low-poly cube (6 faces) - should pass
    cube = cmds.polyCube(name='low_cube')[0]
    cube_shape = cmds.listRelatives(cube, shapes=True)[0]

    # Create a higher-poly plane (100 faces) - should fail
    plane = cmds.polyPlane(name='high_plane', subdivisionsX=10, subdivisionsY=10)[0]
    plane_shape = cmds.listRelatives(plane, shapes=True)[0]

    # Create another low-poly cube - should pass
    cube2 = cmds.polyCube(name='low_cube2')[0]
    cube2_shape = cmds.listRelatives(cube2, shapes=True)[0]

    selList = get_selection_list([cube_shape, plane_shape, cube2_shape])
    result_type, result_data = mc.polyCountLimit(None, selList)

    cube_polys = count_polys(cube)
    plane_polys = count_polys(plane)

    # Only the plane should be flagged
    if len(result_data) == 1:
        print("PASS: test_multiple_meshes - 1/3 meshes flagged (plane with {} polys)".format(plane_polys))
        return True
    else:
        print("FAIL: test_multiple_meshes - Expected 1 flagged, got {}".format(len(result_data)))
        print("      Cube: {} polys, Plane: {} polys, Limit: {}".format(cube_polys, plane_polys, mc.POLY_COUNT_LIMIT))
        return False


def test_configurable_limit():
    """
    Test: Verify the limit can be changed dynamically.
    """
    cmds.file(new=True, force=True)

    # Create a sphere with known poly count
    sphere = cmds.polySphere(name='config_sphere', subdivisionsX=10, subdivisionsY=10)[0]
    shape = cmds.listRelatives(sphere, shapes=True)[0]

    poly_count = count_polys(sphere)

    # Test 1: Set limit above poly count - should pass
    mc.POLY_COUNT_LIMIT = poly_count + 100
    result_type, result_data = mc.polyCountLimit(None, get_selection_list(shape))
    pass_high = len(result_data) == 0

    # Test 2: Set limit below poly count - should fail
    mc.POLY_COUNT_LIMIT = poly_count - 10
    result_type, result_data = mc.polyCountLimit(None, get_selection_list(shape))
    fail_low = len(result_data) > 0

    if pass_high and fail_low:
        print("PASS: test_configurable_limit - Limit correctly affects results")
        return True
    else:
        print("FAIL: test_configurable_limit - Limit changes not working")
        print("      High limit pass: {}, Low limit fail: {}".format(pass_high, fail_low))
        return False


# =============================================================================
# RUN ALL TESTS
# =============================================================================

def run_all_tests():
    print("")
    print("=" * 70)
    print("  polyCountLimit Test Suite")
    print("=" * 70)
    print("")

    results = []
    results.append(("Low poly cube", test_low_poly_cube()))
    results.append(("High poly sphere", test_high_poly_sphere()))
    results.append(("Exactly at limit", test_exactly_at_limit()))
    results.append(("One over limit", test_one_over_limit()))
    results.append(("Empty selection", test_empty_selection()))
    results.append(("Multiple meshes", test_multiple_meshes()))
    results.append(("Configurable limit", test_configurable_limit()))

    # Restore original limit
    mc.POLY_COUNT_LIMIT = ORIGINAL_LIMIT

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
    print("  Default limit restored to: {}".format(mc.POLY_COUNT_LIMIT))
    print("=" * 70)

    return passed == total

run_all_tests()
'''


def get_test_script():
    """Return the Maya test script for copy/paste."""
    return MAYA_TEST_SCRIPT


if __name__ == "__main__":
    print("=" * 70)
    print("  polyCountLimit Test Suite")
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
    print("  DEFAULT LIMIT: 10,000 polygons per mesh")
    print()
    print("  To customize the limit, edit POLY_COUNT_LIMIT in")
    print("  modelChecker/modelChecker_commands.py")
    print()
    print("=" * 70)
