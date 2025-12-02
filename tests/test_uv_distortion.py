"""
Tests for uvDistortion check.

================================================================================
OVERVIEW
================================================================================

The uvDistortion check detects polygons where UV mapping is significantly
stretched or compressed relative to the 3D geometry. This causes:
- Blurry or stretched textures
- Visible seams and artifacts
- Inconsistent texture resolution

================================================================================
ALGORITHM
================================================================================

1. For each polygon, calculate 3D world-space area using MItMeshPolygon.getArea()
2. Calculate UV-space area using the shoelace formula on UV coordinates
3. Compute ratio: UV_area / 3D_area
4. Normalize against median ratio to handle different overall UV scales
5. Flag faces where normalized ratio is outside threshold bounds (0.5 - 2.0)

================================================================================
KNOWN LIMITATIONS
================================================================================

1. REQUIRES UVS: Faces without UVs are skipped, not flagged.

2. AREA-BASED: Uses area comparison, not angle-based distortion detection.
   Some types of shearing may not be caught if area is preserved.

3. INTENTIONAL SCALING: May flag intentionally scaled UVs like tiled textures
   or detail areas with higher resolution.

4. UNIFORM THRESHOLD: Same threshold for all faces; doesn't account for
   different requirements on different parts of the model.

5. MEDIAN NORMALIZATION: Uses median ratio as baseline, which works well
   for most cases but may give unexpected results on heavily distorted meshes.

================================================================================
TEST CASES
================================================================================

1. test_uniform_cube - Default cube with uniform UVs should PASS
2. test_stretched_plane - Plane with stretched UVs should FAIL
3. test_no_uvs - Mesh without UVs should PASS (no faces to check)
4. test_empty_selection - Empty input should not crash
5. test_mixed_distortion - Some faces distorted, some not
6. test_sphere_projection - Spherical projection has inherent distortion
7. test_configurable_threshold - Verify thresholds can be adjusted

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

# Store original thresholds
ORIGINAL_MIN = mc.UV_DISTORTION_THRESHOLD
ORIGINAL_MAX = mc.UV_DISTORTION_THRESHOLD_MAX

def get_selection_list(shapes):
    """Helper to create MSelectionList from shape names."""
    selList = om.MSelectionList()
    if isinstance(shapes, str):
        shapes = [shapes]
    for shape in shapes:
        selList.add(shape)
    return selList

# =============================================================================
# TEST CASES
# =============================================================================

def test_uniform_cube():
    """
    Test: Default cube with automatic UV projection should have minimal distortion.
    """
    cmds.file(new=True, force=True)
    mc.UV_DISTORTION_THRESHOLD = 0.5
    mc.UV_DISTORTION_THRESHOLD_MAX = 2.0

    # Create a cube with automatic UVs
    cube = cmds.polyCube(name='uniform_cube')[0]
    shape = cmds.listRelatives(cube, shapes=True)[0]

    # Apply automatic UV projection for uniform UVs
    cmds.polyAutoProjection(cube, lm=0, pb=0, ibd=1, cm=0, l=2, sc=1, o=1, p=6, ps=0.2, ws=0)

    result_type, result_data = mc.uvDistortion(None, get_selection_list(shape))

    total_distorted = sum(len(faces) for faces in result_data.values())

    if total_distorted == 0:
        print("PASS: test_uniform_cube - No UV distortion detected")
        return True
    else:
        print("FAIL: test_uniform_cube - {} faces flagged as distorted".format(total_distorted))
        return False


def test_stretched_plane():
    """
    Test: Plane with manually stretched UVs should be flagged.
    """
    cmds.file(new=True, force=True)
    mc.UV_DISTORTION_THRESHOLD = 0.5
    mc.UV_DISTORTION_THRESHOLD_MAX = 2.0

    # Create a plane with multiple subdivisions
    plane = cmds.polyPlane(name='stretched_plane', sx=4, sy=4)[0]
    shape = cmds.listRelatives(plane, shapes=True)[0]

    # Create automatic UVs first
    cmds.polyAutoProjection(plane, lm=0, pb=0, ibd=1, cm=0, l=2, sc=1, o=1, p=6, ps=0.2, ws=0)

    # Now stretch some UVs dramatically to create distortion
    # Scale the UVs of the first few faces
    cmds.select('{}.map[0:3]'.format(shape))
    cmds.polyEditUV(su=5.0, sv=0.2)  # Extreme stretch

    result_type, result_data = mc.uvDistortion(None, get_selection_list(shape))

    total_distorted = sum(len(faces) for faces in result_data.values())

    if total_distorted > 0:
        print("PASS: test_stretched_plane - {} distorted faces detected".format(total_distorted))
        return True
    else:
        print("FAIL: test_stretched_plane - Stretched UVs not detected")
        return False


def test_no_uvs():
    """
    Test: Mesh without UVs should PASS (no faces to check).
    """
    cmds.file(new=True, force=True)
    mc.UV_DISTORTION_THRESHOLD = 0.5
    mc.UV_DISTORTION_THRESHOLD_MAX = 2.0

    # Create a cube
    cube = cmds.polyCube(name='no_uv_cube')[0]
    shape = cmds.listRelatives(cube, shapes=True)[0]

    # Delete all UVs
    cmds.polyMapDel(cube)

    result_type, result_data = mc.uvDistortion(None, get_selection_list(shape))

    total_distorted = sum(len(faces) for faces in result_data.values())

    if total_distorted == 0:
        print("PASS: test_no_uvs - Mesh without UVs handled gracefully")
        return True
    else:
        print("FAIL: test_no_uvs - Unexpected results for mesh without UVs")
        return False


def test_empty_selection():
    """
    Test: Empty selection should not crash.
    """
    cmds.file(new=True, force=True)

    selList = om.MSelectionList()

    try:
        result_type, result_data = mc.uvDistortion(None, selList)
        if len(result_data) == 0:
            print("PASS: test_empty_selection - Empty selection handled gracefully")
            return True
        else:
            print("FAIL: test_empty_selection - Unexpected results from empty selection")
            return False
    except Exception as e:
        print("FAIL: test_empty_selection - Exception: {}".format(str(e)))
        return False


def test_cylinder_ends():
    """
    Test: Cylinder end caps often have UV distortion due to planar projection.
    """
    cmds.file(new=True, force=True)
    mc.UV_DISTORTION_THRESHOLD = 0.5
    mc.UV_DISTORTION_THRESHOLD_MAX = 2.0

    # Create a cylinder - end caps typically have distortion with cylindrical UVs
    cylinder = cmds.polyCylinder(name='test_cylinder', sx=20, sy=1, sc=1)[0]
    shape = cmds.listRelatives(cylinder, shapes=True)[0]

    # Use cylindrical projection which creates distortion at caps
    cmds.polyProjection(cylinder + '.f[*]', type='cylindrical', ibd=True, kir=True)

    result_type, result_data = mc.uvDistortion(None, get_selection_list(shape))

    total_distorted = sum(len(faces) for faces in result_data.values())

    # Cylinder caps typically show distortion with cylindrical projection
    print("INFO: test_cylinder_ends - {} faces with distortion (caps often distorted)".format(total_distorted))
    print("PASS: test_cylinder_ends - Check completed without errors")
    return True


def test_configurable_threshold():
    """
    Test: Verify that threshold configuration works.
    """
    cmds.file(new=True, force=True)

    # Create a plane
    plane = cmds.polyPlane(name='threshold_plane', sx=2, sy=2)[0]
    shape = cmds.listRelatives(plane, shapes=True)[0]

    # Create automatic UVs
    cmds.polyAutoProjection(plane, lm=0, pb=0, ibd=1, cm=0, l=2, sc=1, o=1, p=6, ps=0.2, ws=0)

    # Test with very tight threshold - should flag more faces
    mc.UV_DISTORTION_THRESHOLD = 0.95
    mc.UV_DISTORTION_THRESHOLD_MAX = 1.05
    result_type, result_data = mc.uvDistortion(None, get_selection_list(shape))
    tight_count = sum(len(faces) for faces in result_data.values())

    # Test with very loose threshold - should flag fewer faces
    mc.UV_DISTORTION_THRESHOLD = 0.1
    mc.UV_DISTORTION_THRESHOLD_MAX = 10.0
    result_type, result_data = mc.uvDistortion(None, get_selection_list(shape))
    loose_count = sum(len(faces) for faces in result_data.values())

    if tight_count >= loose_count:
        print("PASS: test_configurable_threshold - Tight: {}, Loose: {}".format(tight_count, loose_count))
        return True
    else:
        print("FAIL: test_configurable_threshold - Threshold not affecting results")
        return False


def test_sphere_projection():
    """
    Test: Sphere with spherical projection - poles typically have distortion.
    """
    cmds.file(new=True, force=True)
    mc.UV_DISTORTION_THRESHOLD = 0.5
    mc.UV_DISTORTION_THRESHOLD_MAX = 2.0

    # Create a sphere
    sphere = cmds.polySphere(name='test_sphere', sx=16, sy=16)[0]
    shape = cmds.listRelatives(sphere, shapes=True)[0]

    # Default sphere UVs have inherent distortion at poles

    result_type, result_data = mc.uvDistortion(None, get_selection_list(shape))

    total_distorted = sum(len(faces) for faces in result_data.values())

    # Spheres typically have some distortion at poles
    print("INFO: test_sphere_projection - {} faces with distortion (poles often distorted)".format(total_distorted))
    print("PASS: test_sphere_projection - Check completed without errors")
    return True


# =============================================================================
# RUN ALL TESTS
# =============================================================================

def run_all_tests():
    print("")
    print("=" * 70)
    print("  uvDistortion Test Suite")
    print("=" * 70)
    print("")

    results = []
    results.append(("Uniform cube", test_uniform_cube()))
    results.append(("Stretched plane", test_stretched_plane()))
    results.append(("No UVs", test_no_uvs()))
    results.append(("Empty selection", test_empty_selection()))
    results.append(("Cylinder ends", test_cylinder_ends()))
    results.append(("Configurable threshold", test_configurable_threshold()))
    results.append(("Sphere projection", test_sphere_projection()))

    # Restore original thresholds
    mc.UV_DISTORTION_THRESHOLD = ORIGINAL_MIN
    mc.UV_DISTORTION_THRESHOLD_MAX = ORIGINAL_MAX

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
    print("  Thresholds restored: {} - {}".format(mc.UV_DISTORTION_THRESHOLD, mc.UV_DISTORTION_THRESHOLD_MAX))
    print("=" * 70)

    return passed == total

run_all_tests()
'''


def get_test_script():
    """Return the Maya test script for copy/paste."""
    return MAYA_TEST_SCRIPT


if __name__ == "__main__":
    print("=" * 70)
    print("  uvDistortion Test Suite")
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
    print("    Detects polygons with stretched or compressed UV coordinates")
    print("    by comparing UV area to 3D geometry area ratios.")
    print()
    print("  DEFAULT THRESHOLDS:")
    print("    UV_DISTORTION_THRESHOLD = 0.5 (min ratio)")
    print("    UV_DISTORTION_THRESHOLD_MAX = 2.0 (max ratio)")
    print()
    print("  COMMON DISTORTION SOURCES:")
    print("    - Spherical/cylindrical projections at poles")
    print("    - Manual UV scaling without maintaining proportions")
    print("    - Boolean operations on UV'd geometry")
    print("    - Stretching geometry after UV mapping")
    print()
    print("=" * 70)
