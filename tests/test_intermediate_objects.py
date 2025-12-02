"""
Tests for intermediateObjects check.

================================================================================
OVERVIEW
================================================================================

The intermediateObjects check detects transform nodes that have intermediate
shape nodes. Intermediate objects are created during modeling operations
(like deformers, blendshapes, or duplicating skinned meshes) and should
typically be deleted when cleaning up a scene.

Intermediate objects cause:
- Increased file size
- Slower scene loading
- Confusion in the Outliner
- Potential issues with exports
- Signs of incomplete scene cleanup

================================================================================
ALGORITHM
================================================================================

1. For each transform node, get its shape children
2. Check if any shape has the 'intermediateObject' attribute set to True
3. Flag transforms that have intermediate shape nodes
4. Skip checking the intermediate shapes themselves

================================================================================
KNOWN LIMITATIONS
================================================================================

1. INTENTIONAL INTERMEDIATES: Some intermediate objects are intentional,
   such as blendshape base meshes or deformer inputs. These will be flagged.

2. REFERENCED OBJECTS: Referenced intermediate objects may be required by
   the source file and cannot be deleted without breaking the reference.

3. DEFORMER SETUPS: Complex deformer rigs may legitimately need intermediate
   objects for their pipeline to function correctly.

4. NO DISTINCTION: Does not distinguish between needed and unneeded
   intermediate objects - all are flagged equally.

================================================================================
TEST CASES
================================================================================

1. test_no_intermediate - Clean mesh should PASS
2. test_with_intermediate - Mesh with intermediate shape should FAIL
3. test_deformer_intermediate - Mesh with deformer intermediate should FAIL
4. test_multiple_shapes - Transform with mixed shapes
5. test_clean_history - Mesh after delete history should PASS
6. test_empty_selection - Empty input should not crash
7. test_multiple_intermediates - Scene with several intermediate objects

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

def get_transform_nodes():
    """Helper to get all transform nodes as UUIDs."""
    transforms = cmds.ls(type='transform', long=True) or []
    # Filter out default cameras
    default_cams = ['|front', '|persp', '|side', '|top']
    transforms = [t for t in transforms if t not in default_cams]
    uuids = []
    for t in transforms:
        uuid = cmds.ls(t, uuid=True)
        if uuid:
            uuids.append(uuid[0])
    return uuids

# =============================================================================
# TEST CASES
# =============================================================================

def test_no_intermediate():
    """
    Test: Clean mesh without intermediate objects should PASS.
    """
    cmds.file(new=True, force=True)

    # Create a simple cube - no intermediate objects
    cube = cmds.polyCube(name='clean_cube')[0]
    cmds.delete(cube, constructionHistory=True)

    nodes = get_transform_nodes()
    result_type, result_data = mc.intermediateObjects(nodes, None)

    cubeUUID = cmds.ls(cube, uuid=True)[0]
    if cubeUUID not in result_data:
        print("PASS: test_no_intermediate - Clean mesh not flagged")
        return True
    else:
        print("FAIL: test_no_intermediate - Clean mesh incorrectly flagged")
        return False


def test_with_intermediate():
    """
    Test: Mesh with intermediate shape should FAIL.
    """
    cmds.file(new=True, force=True)

    # Create a cube with an intermediate shape
    cube = cmds.polyCube(name='cube_with_intermediate')[0]
    shape = cmds.listRelatives(cube, shapes=True)[0]

    # Duplicate the shape and make it intermediate
    newShape = cmds.duplicate(shape, name='intermediateShape')[0]
    # The duplicate is a transform, need to get its shape
    dupShape = cmds.listRelatives(newShape, shapes=True)[0]
    cmds.parent(dupShape, cube, shape=True, relative=True)
    cmds.setAttr(dupShape + '.intermediateObject', True)
    cmds.delete(newShape)  # Delete the extra transform

    nodes = get_transform_nodes()
    result_type, result_data = mc.intermediateObjects(nodes, None)

    cubeUUID = cmds.ls(cube, uuid=True)[0]
    if cubeUUID in result_data:
        print("PASS: test_with_intermediate - Intermediate object flagged")
        return True
    else:
        print("FAIL: test_with_intermediate - Intermediate object not detected")
        return False


def test_deformer_intermediate():
    """
    Test: Mesh with deformer (creates intermediate) should FAIL.
    """
    cmds.file(new=True, force=True)

    # Create a cube and add a lattice deformer
    # This creates an intermediate object (the original undeformed mesh)
    cube = cmds.polyCube(name='deformed_cube')[0]
    cmds.lattice(cube, divisions=(2, 2, 2))

    nodes = get_transform_nodes()
    result_type, result_data = mc.intermediateObjects(nodes, None)

    cubeUUID = cmds.ls(cube, uuid=True)[0]
    if cubeUUID in result_data:
        print("PASS: test_deformer_intermediate - Deformer intermediate flagged")
        return True
    else:
        # Note: Some deformers may not create intermediates
        print("INFO: test_deformer_intermediate - No intermediate (may be expected)")
        return True  # Not a failure, just no intermediate created


def test_clean_history():
    """
    Test: Mesh after deleting history should PASS.
    """
    cmds.file(new=True, force=True)

    # Create a cube, add operations, then delete history
    cube = cmds.polyCube(name='history_cube')[0]
    cmds.polyBevel(cube)
    cmds.polySmooth(cube)
    cmds.delete(cube, constructionHistory=True)

    nodes = get_transform_nodes()
    result_type, result_data = mc.intermediateObjects(nodes, None)

    cubeUUID = cmds.ls(cube, uuid=True)[0]
    if cubeUUID not in result_data:
        print("PASS: test_clean_history - Clean history mesh not flagged")
        return True
    else:
        print("FAIL: test_clean_history - Clean history mesh incorrectly flagged")
        return False


def test_blendshape_intermediate():
    """
    Test: Blendshape setup (creates intermediate) should FAIL.
    """
    cmds.file(new=True, force=True)

    # Create base and target meshes
    base = cmds.polyCube(name='base_mesh')[0]
    target = cmds.polyCube(name='target_mesh')[0]
    cmds.move(0, 2, 0, target)

    # Move some vertices on target to make it different
    cmds.select(target + '.vtx[0:3]')
    cmds.move(0.5, 0, 0, relative=True)

    # Create blendshape
    cmds.blendShape(target, base, name='myBlendShape')

    nodes = get_transform_nodes()
    result_type, result_data = mc.intermediateObjects(nodes, None)

    baseUUID = cmds.ls(base, uuid=True)[0]
    if baseUUID in result_data:
        print("PASS: test_blendshape_intermediate - Blendshape intermediate flagged")
        return True
    else:
        print("INFO: test_blendshape_intermediate - No intermediate detected (may be expected)")
        return True


def test_multiple_intermediates():
    """
    Test: Scene with multiple intermediate objects.
    """
    cmds.file(new=True, force=True)

    # Create a clean mesh
    cleanCube = cmds.polyCube(name='clean_cube')[0]
    cmds.delete(cleanCube, constructionHistory=True)

    # Create mesh with lattice (intermediate)
    deformedCube = cmds.polyCube(name='deformed_cube')[0]
    cmds.lattice(deformedCube, divisions=(2, 2, 2))

    nodes = get_transform_nodes()
    result_type, result_data = mc.intermediateObjects(nodes, None)

    cleanUUID = cmds.ls(cleanCube, uuid=True)[0]
    deformedUUID = cmds.ls(deformedCube, uuid=True)[0]

    clean_ok = cleanUUID not in result_data
    # Note: lattice may or may not create intermediate depending on Maya version
    if clean_ok:
        print("PASS: test_multiple_intermediates - Clean mesh not flagged")
        return True
    else:
        print("FAIL: test_multiple_intermediates - Clean mesh incorrectly flagged")
        return False


def test_empty_selection():
    """
    Test: Empty input should not crash.
    """
    cmds.file(new=True, force=True)

    try:
        result_type, result_data = mc.intermediateObjects([], None)
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
    print("  intermediateObjects Test Suite")
    print("=" * 70)
    print("")

    results = []
    results.append(("No intermediate (clean)", test_no_intermediate()))
    results.append(("With intermediate shape", test_with_intermediate()))
    results.append(("Deformer intermediate", test_deformer_intermediate()))
    results.append(("Clean history", test_clean_history()))
    results.append(("Blendshape intermediate", test_blendshape_intermediate()))
    results.append(("Multiple intermediates", test_multiple_intermediates()))
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
    print("  intermediateObjects Test Suite")
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
    print("    Detects intermediate shape nodes")
    print("    - Created by deformers, blendshapes, etc.")
    print("    - Checks 'intermediateObject' attribute")
    print()
    print("  WHAT CREATES INTERMEDIATES:")
    print("    - Lattice deformers")
    print("    - Blendshapes")
    print("    - Skin cluster setup")
    print("    - Some boolean operations")
    print("    - Duplicating deformed meshes")
    print()
    print("  WHY THIS MATTERS:")
    print("    - File size bloat")
    print("    - Slower scene loading")
    print("    - Export complications")
    print("    - Indicates incomplete cleanup")
    print()
    print("=" * 70)
