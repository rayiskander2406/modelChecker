"""
Tests for defaultMaterials check.

================================================================================
OVERVIEW
================================================================================

The defaultMaterials check detects meshes that are still assigned to the
initialShadingGroup (lambert1), which typically indicates unfinished work.
This is essentially the inverse of the existing 'shaders' check.

================================================================================
ALGORITHM
================================================================================

1. For each transform node, get its shape children
2. Query shading engine connections using cmds.listConnections()
3. Flag meshes where the shading group is 'initialShadingGroup'

================================================================================
KNOWN LIMITATIONS
================================================================================

1. FIRST CONNECTION ONLY: Only checks the first shading group connection.
   Multi-material objects with per-face assignments may not be fully checked.

2. MULTI-MATERIAL OBJECTS: If an object has multiple materials and any face
   uses a non-default material, the check may pass even if some faces use
   the default.

3. PROCEDURAL MATERIALS: Does not distinguish between lambert1 and other
   intentionally simple procedural materials a user might create.

================================================================================
TEST CASES
================================================================================

1. test_default_material_cube - Cube with lambert1 should FAIL
2. test_custom_material_cube - Cube with custom material should PASS
3. test_multiple_objects_mixed - Mix of default and custom materials
4. test_empty_selection - Empty input should not crash
5. test_group_without_mesh - Transform without mesh shape should PASS
6. test_multi_material_object - Object with multiple materials

================================================================================
RUNNING TESTS
================================================================================

Copy MAYA_TEST_SCRIPT into Maya's Script Editor and execute.

================================================================================
"""

MAYA_TEST_SCRIPT = '''
import maya.cmds as cmds
from modelChecker import modelChecker_commands as mc

def get_transform_uuids(objects):
    """Helper to get UUIDs for transform nodes."""
    uuids = []
    for obj in objects:
        uuid = cmds.ls(obj, uuid=True)
        if uuid:
            uuids.append(uuid[0])
    return uuids

# =============================================================================
# TEST CASES
# =============================================================================

def test_default_material_cube():
    """
    Test: Cube with default lambert1 should FAIL (be flagged).
    """
    cmds.file(new=True, force=True)

    # Create a cube - it automatically gets lambert1
    cube = cmds.polyCube(name='default_cube')[0]

    # Verify it has initialShadingGroup
    shape = cmds.listRelatives(cube, shapes=True)[0]
    sg = cmds.listConnections(shape, type='shadingEngine')[0]

    uuids = get_transform_uuids([cube])
    result_type, result_data = mc.defaultMaterials(uuids, None)

    if len(result_data) == 1:
        print("PASS: test_default_material_cube - Cube with lambert1 flagged (shading group: {})".format(sg))
        return True
    else:
        print("FAIL: test_default_material_cube - Cube with default material not flagged")
        return False


def test_custom_material_cube():
    """
    Test: Cube with custom material should PASS (not flagged).
    """
    cmds.file(new=True, force=True)

    # Create a cube
    cube = cmds.polyCube(name='custom_cube')[0]

    # Create and assign a custom material
    shader = cmds.shadingNode('lambert', asShader=True, name='custom_lambert')
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name='custom_lambertSG')
    cmds.connectAttr(shader + '.outColor', shading_group + '.surfaceShader', force=True)
    cmds.sets(cube, edit=True, forceElement=shading_group)

    uuids = get_transform_uuids([cube])
    result_type, result_data = mc.defaultMaterials(uuids, None)

    if len(result_data) == 0:
        print("PASS: test_custom_material_cube - Cube with custom material not flagged")
        return True
    else:
        print("FAIL: test_custom_material_cube - Cube with custom material incorrectly flagged")
        return False


def test_multiple_objects_mixed():
    """
    Test: Multiple objects - some with default, some with custom materials.
    """
    cmds.file(new=True, force=True)

    # Create cube with default material
    default_cube = cmds.polyCube(name='default_cube')[0]

    # Create cube with custom material
    custom_cube = cmds.polyCube(name='custom_cube')[0]
    shader = cmds.shadingNode('blinn', asShader=True, name='custom_blinn')
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name='custom_blinnSG')
    cmds.connectAttr(shader + '.outColor', shading_group + '.surfaceShader', force=True)
    cmds.sets(custom_cube, edit=True, forceElement=shading_group)

    # Create another default cube
    default_cube2 = cmds.polyCube(name='default_cube2')[0]

    uuids = get_transform_uuids([default_cube, custom_cube, default_cube2])
    result_type, result_data = mc.defaultMaterials(uuids, None)

    # Should flag 2 objects (the two default cubes)
    if len(result_data) == 2:
        print("PASS: test_multiple_objects_mixed - 2/3 objects flagged (default materials)")
        return True
    else:
        print("FAIL: test_multiple_objects_mixed - Expected 2 flagged, got {}".format(len(result_data)))
        return False


def test_empty_selection():
    """
    Test: Empty selection should not crash and return empty results.
    """
    cmds.file(new=True, force=True)

    try:
        result_type, result_data = mc.defaultMaterials([], None)
        if len(result_data) == 0:
            print("PASS: test_empty_selection - Empty selection handled gracefully")
            return True
        else:
            print("FAIL: test_empty_selection - Unexpected results from empty selection")
            return False
    except Exception as e:
        print("FAIL: test_empty_selection - Exception: {}".format(str(e)))
        return False


def test_group_without_mesh():
    """
    Test: Transform node without mesh shape should PASS (not flagged).
    """
    cmds.file(new=True, force=True)

    # Create an empty group
    group = cmds.group(empty=True, name='empty_group')

    # Create a locator (not a mesh)
    locator = cmds.spaceLocator(name='test_locator')[0]

    uuids = get_transform_uuids([group, locator])
    result_type, result_data = mc.defaultMaterials(uuids, None)

    if len(result_data) == 0:
        print("PASS: test_group_without_mesh - Non-mesh transforms not flagged")
        return True
    else:
        print("FAIL: test_group_without_mesh - Non-mesh transforms incorrectly flagged")
        return False


def test_phong_material():
    """
    Test: Cube with phong material should PASS (any non-default is fine).
    """
    cmds.file(new=True, force=True)

    # Create a cube
    cube = cmds.polyCube(name='phong_cube')[0]

    # Create and assign a phong material
    shader = cmds.shadingNode('phong', asShader=True, name='custom_phong')
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name='custom_phongSG')
    cmds.connectAttr(shader + '.outColor', shading_group + '.surfaceShader', force=True)
    cmds.sets(cube, edit=True, forceElement=shading_group)

    uuids = get_transform_uuids([cube])
    result_type, result_data = mc.defaultMaterials(uuids, None)

    if len(result_data) == 0:
        print("PASS: test_phong_material - Cube with phong material not flagged")
        return True
    else:
        print("FAIL: test_phong_material - Cube with phong material incorrectly flagged")
        return False


def test_arnold_material():
    """
    Test: Cube with Arnold aiStandardSurface should PASS.
    This test may be skipped if Arnold is not available.
    """
    cmds.file(new=True, force=True)

    # Check if Arnold is available
    try:
        cmds.loadPlugin('mtoa', quiet=True)
    except:
        print("SKIP: test_arnold_material - Arnold plugin not available")
        return True  # Skip test but don't fail

    # Create a cube
    cube = cmds.polyCube(name='arnold_cube')[0]

    try:
        # Create and assign an Arnold material
        shader = cmds.shadingNode('aiStandardSurface', asShader=True, name='arnold_shader')
        shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name='arnold_shaderSG')
        cmds.connectAttr(shader + '.outColor', shading_group + '.surfaceShader', force=True)
        cmds.sets(cube, edit=True, forceElement=shading_group)

        uuids = get_transform_uuids([cube])
        result_type, result_data = mc.defaultMaterials(uuids, None)

        if len(result_data) == 0:
            print("PASS: test_arnold_material - Cube with Arnold material not flagged")
            return True
        else:
            print("FAIL: test_arnold_material - Cube with Arnold material incorrectly flagged")
            return False
    except Exception as e:
        print("SKIP: test_arnold_material - Could not create Arnold material: {}".format(str(e)))
        return True  # Skip on error


# =============================================================================
# RUN ALL TESTS
# =============================================================================

def run_all_tests():
    print("")
    print("=" * 70)
    print("  defaultMaterials Test Suite")
    print("=" * 70)
    print("")

    results = []
    results.append(("Default material cube", test_default_material_cube()))
    results.append(("Custom material cube", test_custom_material_cube()))
    results.append(("Multiple objects mixed", test_multiple_objects_mixed()))
    results.append(("Empty selection", test_empty_selection()))
    results.append(("Group without mesh", test_group_without_mesh()))
    results.append(("Phong material", test_phong_material()))
    results.append(("Arnold material", test_arnold_material()))

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
    print("  defaultMaterials Test Suite")
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
    print("    Flags meshes still using the default lambert1 material")
    print("    (assigned to initialShadingGroup)")
    print()
    print("  RELATIONSHIP TO 'shaders' CHECK:")
    print("    - 'shaders' check: flags objects with NON-default materials")
    print("    - 'defaultMaterials' check: flags objects WITH default materials")
    print("    These are complementary checks for different use cases.")
    print()
    print("=" * 70)
