"""
Tests for texelDensity check.

================================================================================
OVERVIEW
================================================================================

The texelDensity check detects faces with inconsistent pixel density across the
model. Texel density measures how many texture pixels cover each unit of 3D
surface area. Consistent texel density ensures:
- Uniform texture quality across the entire model
- No areas appear blurrier or sharper than others
- Professional-quality UV mapping

================================================================================
ALGORITHM
================================================================================

1. For each polygon, calculate its 3D world-space area using MItMeshPolygon
2. Calculate the corresponding UV-space area using the shoelace formula
3. Convert UV area to pixel area: UV_area * texture_size^2
4. Compute texel density: pixel_area / 3D_area (pixels per unit)
5. Calculate median density across all faces
6. Flag faces where density deviates more than threshold from median

================================================================================
KNOWN LIMITATIONS
================================================================================

1. REQUIRES UVS: Faces without UVs are skipped, not flagged.

2. UNIFORM TEXTURE SIZE: Assumes all textures are the same resolution
   (default 1024x1024). Multi-resolution textures not considered.

3. NO TEXTURE LOOKUP: Uses assumed texture size, not actual connected textures.
   The check measures UV consistency, not actual pixel coverage.

4. SMALL FACES: Very small faces may have unstable density calculations
   due to floating-point precision issues.

5. INTENTIONAL VARIATION: May flag intentionally varied density, such as
   higher resolution for hero areas or lower for hidden areas.

6. MEDIAN-BASED: Uses median as baseline, which works well for most cases
   but may give unexpected results on meshes with bimodal density distribution.

================================================================================
TEST CASES
================================================================================

1. test_uniform_cube - Default cube with uniform UVs should PASS
2. test_uniform_plane - Plane with uniform auto-projected UVs should PASS
3. test_inconsistent_plane - Plane with some UVs scaled should FAIL
4. test_no_uvs - Mesh without UVs should PASS (no faces to check)
5. test_empty_selection - Empty input should not crash
6. test_sphere_projection - Sphere with default UVs (inherent variation)
7. test_configurable_threshold - Verify thresholds can be adjusted
8. test_extreme_scaling - Dramatically different UV scales should FAIL

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
ORIGINAL_MIN = mc.TEXEL_DENSITY_THRESHOLD
ORIGINAL_MAX = mc.TEXEL_DENSITY_THRESHOLD_MAX
ORIGINAL_SIZE = mc.TEXEL_DENSITY_TEXTURE_SIZE

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
    Test: Default cube with automatic UV projection should have uniform density.
    """
    cmds.file(new=True, force=True)
    mc.TEXEL_DENSITY_THRESHOLD = 0.5
    mc.TEXEL_DENSITY_THRESHOLD_MAX = 2.0

    # Create a cube with automatic UVs
    cube = cmds.polyCube(name='uniform_cube')[0]
    shape = cmds.listRelatives(cube, shapes=True)[0]

    # Apply automatic UV projection for uniform UVs
    cmds.polyAutoProjection(cube, lm=0, pb=0, ibd=1, cm=0, l=2, sc=1, o=1, p=6, ps=0.2, ws=0)

    result_type, result_data = mc.texelDensity(None, get_selection_list(shape))

    total_inconsistent = sum(len(faces) for faces in result_data.values())

    if total_inconsistent == 0:
        print("PASS: test_uniform_cube - Uniform texel density")
        return True
    else:
        print("FAIL: test_uniform_cube - {} faces flagged as inconsistent".format(total_inconsistent))
        return False


def test_uniform_plane():
    """
    Test: Plane with uniform auto-projected UVs should have consistent density.
    """
    cmds.file(new=True, force=True)
    mc.TEXEL_DENSITY_THRESHOLD = 0.5
    mc.TEXEL_DENSITY_THRESHOLD_MAX = 2.0

    # Create a plane with multiple subdivisions
    plane = cmds.polyPlane(name='uniform_plane', sx=4, sy=4)[0]
    shape = cmds.listRelatives(plane, shapes=True)[0]

    # Auto-project UVs for uniformity
    cmds.polyAutoProjection(plane, lm=0, pb=0, ibd=1, cm=0, l=2, sc=1, o=1, p=6, ps=0.2, ws=0)

    result_type, result_data = mc.texelDensity(None, get_selection_list(shape))

    total_inconsistent = sum(len(faces) for faces in result_data.values())

    if total_inconsistent == 0:
        print("PASS: test_uniform_plane - Uniform texel density on plane")
        return True
    else:
        print("FAIL: test_uniform_plane - {} faces flagged".format(total_inconsistent))
        return False


def test_inconsistent_plane():
    """
    Test: Plane with some UVs dramatically scaled should be flagged.
    """
    cmds.file(new=True, force=True)
    mc.TEXEL_DENSITY_THRESHOLD = 0.5
    mc.TEXEL_DENSITY_THRESHOLD_MAX = 2.0

    # Create a plane with multiple subdivisions
    plane = cmds.polyPlane(name='inconsistent_plane', sx=4, sy=4)[0]
    shape = cmds.listRelatives(plane, shapes=True)[0]

    # Create uniform UVs first
    cmds.polyAutoProjection(plane, lm=0, pb=0, ibd=1, cm=0, l=2, sc=1, o=1, p=6, ps=0.2, ws=0)

    # Scale some UV coordinates dramatically to create inconsistent density
    cmds.select('{}.map[0:3]'.format(shape))
    cmds.polyEditUV(su=4.0, sv=4.0)  # 4x scale = 16x area = different density

    result_type, result_data = mc.texelDensity(None, get_selection_list(shape))

    total_inconsistent = sum(len(faces) for faces in result_data.values())

    if total_inconsistent > 0:
        print("PASS: test_inconsistent_plane - {} inconsistent faces detected".format(total_inconsistent))
        return True
    else:
        print("FAIL: test_inconsistent_plane - Inconsistent density not detected")
        return False


def test_no_uvs():
    """
    Test: Mesh without UVs should PASS (no faces to check).
    """
    cmds.file(new=True, force=True)
    mc.TEXEL_DENSITY_THRESHOLD = 0.5
    mc.TEXEL_DENSITY_THRESHOLD_MAX = 2.0

    # Create a cube
    cube = cmds.polyCube(name='no_uv_cube')[0]
    shape = cmds.listRelatives(cube, shapes=True)[0]

    # Delete all UVs
    cmds.polyMapDel(cube)

    result_type, result_data = mc.texelDensity(None, get_selection_list(shape))

    total_inconsistent = sum(len(faces) for faces in result_data.values())

    if total_inconsistent == 0:
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
        result_type, result_data = mc.texelDensity(None, selList)
        if len(result_data) == 0:
            print("PASS: test_empty_selection - Empty selection handled gracefully")
            return True
        else:
            print("FAIL: test_empty_selection - Unexpected results from empty selection")
            return False
    except Exception as e:
        print("FAIL: test_empty_selection - Exception: {}".format(str(e)))
        return False


def test_sphere_projection():
    """
    Test: Sphere with default UVs - poles typically have different density.
    """
    cmds.file(new=True, force=True)
    mc.TEXEL_DENSITY_THRESHOLD = 0.5
    mc.TEXEL_DENSITY_THRESHOLD_MAX = 2.0

    # Create a sphere - default UVs have inherent density variation at poles
    sphere = cmds.polySphere(name='test_sphere', sx=16, sy=16)[0]
    shape = cmds.listRelatives(sphere, shapes=True)[0]

    result_type, result_data = mc.texelDensity(None, get_selection_list(shape))

    total_inconsistent = sum(len(faces) for faces in result_data.values())

    # Spheres typically have density variation at poles
    print("INFO: test_sphere_projection - {} faces with inconsistent density (poles often vary)".format(total_inconsistent))
    print("PASS: test_sphere_projection - Check completed without errors")
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
    mc.TEXEL_DENSITY_THRESHOLD = 0.95
    mc.TEXEL_DENSITY_THRESHOLD_MAX = 1.05
    result_type, result_data = mc.texelDensity(None, get_selection_list(shape))
    tight_count = sum(len(faces) for faces in result_data.values())

    # Test with very loose threshold - should flag fewer faces
    mc.TEXEL_DENSITY_THRESHOLD = 0.1
    mc.TEXEL_DENSITY_THRESHOLD_MAX = 10.0
    result_type, result_data = mc.texelDensity(None, get_selection_list(shape))
    loose_count = sum(len(faces) for faces in result_data.values())

    if tight_count >= loose_count:
        print("PASS: test_configurable_threshold - Tight: {}, Loose: {}".format(tight_count, loose_count))
        return True
    else:
        print("FAIL: test_configurable_threshold - Threshold not affecting results")
        return False


def test_extreme_scaling():
    """
    Test: Mesh with dramatically different UV scales should be flagged.
    """
    cmds.file(new=True, force=True)
    mc.TEXEL_DENSITY_THRESHOLD = 0.5
    mc.TEXEL_DENSITY_THRESHOLD_MAX = 2.0

    # Create a plane with more subdivisions for better testing
    plane = cmds.polyPlane(name='extreme_plane', sx=6, sy=6)[0]
    shape = cmds.listRelatives(plane, shapes=True)[0]

    # Create uniform UVs first
    cmds.polyAutoProjection(plane, lm=0, pb=0, ibd=1, cm=0, l=2, sc=1, o=1, p=6, ps=0.2, ws=0)

    # Apply extreme scaling to half the UV coordinates
    cmds.select('{}.map[0:8]'.format(shape))
    cmds.polyEditUV(su=0.1, sv=0.1)  # 10% scale = very different density

    result_type, result_data = mc.texelDensity(None, get_selection_list(shape))

    total_inconsistent = sum(len(faces) for faces in result_data.values())

    if total_inconsistent > 0:
        print("PASS: test_extreme_scaling - {} faces with extreme density variation".format(total_inconsistent))
        return True
    else:
        print("FAIL: test_extreme_scaling - Extreme density variation not detected")
        return False


# =============================================================================
# RUN ALL TESTS
# =============================================================================

def run_all_tests():
    print("")
    print("=" * 70)
    print("  texelDensity Test Suite")
    print("=" * 70)
    print("")

    results = []
    results.append(("Uniform cube", test_uniform_cube()))
    results.append(("Uniform plane", test_uniform_plane()))
    results.append(("Inconsistent plane", test_inconsistent_plane()))
    results.append(("No UVs", test_no_uvs()))
    results.append(("Empty selection", test_empty_selection()))
    results.append(("Sphere projection", test_sphere_projection()))
    results.append(("Configurable threshold", test_configurable_threshold()))
    results.append(("Extreme scaling", test_extreme_scaling()))

    # Restore original thresholds
    mc.TEXEL_DENSITY_THRESHOLD = ORIGINAL_MIN
    mc.TEXEL_DENSITY_THRESHOLD_MAX = ORIGINAL_MAX
    mc.TEXEL_DENSITY_TEXTURE_SIZE = ORIGINAL_SIZE

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
    print("  Thresholds restored: {} - {}".format(mc.TEXEL_DENSITY_THRESHOLD, mc.TEXEL_DENSITY_THRESHOLD_MAX))
    print("=" * 70)

    return passed == total

run_all_tests()
'''


def get_test_script():
    """Return the Maya test script for copy/paste."""
    return MAYA_TEST_SCRIPT


if __name__ == "__main__":
    print("=" * 70)
    print("  texelDensity Test Suite")
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
    print("    Detects faces with inconsistent texel density (pixels per unit)")
    print("    across the model surface. Ensures uniform texture quality.")
    print()
    print("  DEFAULT THRESHOLDS:")
    print("    TEXEL_DENSITY_THRESHOLD = 0.5 (min ratio)")
    print("    TEXEL_DENSITY_THRESHOLD_MAX = 2.0 (max ratio)")
    print("    TEXEL_DENSITY_TEXTURE_SIZE = 1024 (assumed texture resolution)")
    print()
    print("  COMMON DENSITY ISSUES:")
    print("    - Spherical/cylindrical projections at poles")
    print("    - Manual UV scaling without planning")
    print("    - Mixing high-detail and low-detail areas")
    print("    - UV islands at different scales")
    print()
    print("=" * 70)
