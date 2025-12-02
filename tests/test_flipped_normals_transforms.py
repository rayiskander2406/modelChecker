"""
Tests for flippedNormals check - Transform/Coordinate Space Validation

================================================================================
BUG DESCRIPTION
================================================================================

The current flippedNormals implementation has a COORDINATE SPACE MISMATCH:

    boundingBox = mesh.boundingBox          # OBJECT SPACE
    meshCenter = boundingBox.center

    faceCenter = faceIt.center(om.MSpace.kWorld)    # WORLD SPACE
    faceNormal = faceIt.getNormal(om.MSpace.kWorld) # WORLD SPACE

This causes INCORRECT results for any mesh that:
- Is translated away from world origin
- Has rotation applied
- Has non-uniform scale

================================================================================
TEST STRATEGY
================================================================================

These tests create geometry with transforms and verify:
1. Clean geometry with transforms should have ZERO flipped normals
2. Reversed geometry with transforms should detect ALL flipped faces

If the bug exists:
- test_translated_cube_clean_normals will FAIL (false positives)
- test_rotated_cube_clean_normals will FAIL (false positives)

After the fix:
- All tests should PASS

================================================================================
RUNNING TESTS
================================================================================

Copy MAYA_TEST_SCRIPT into Maya's Script Editor and execute.
The test will report PASS/FAIL for each case and summarize results.

================================================================================
"""

MAYA_TEST_SCRIPT = '''
import maya.cmds as cmds
import maya.api.OpenMaya as om
from modelChecker import modelChecker_commands as mc

def get_selection_list(shape):
    """Helper to create MSelectionList from shape name."""
    selList = om.MSelectionList()
    selList.add(shape)
    return selList

# =============================================================================
# BASELINE TESTS (should pass with current code)
# =============================================================================

def test_cube_at_origin_clean():
    """
    BASELINE: Cube at origin with default (correct) normals.
    Expected: PASS - 0 flipped faces
    """
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name='origin_cube')[0]
    shape = cmds.listRelatives(cube, shapes=True)[0]

    result_type, result_data = mc.flippedNormals(None, get_selection_list(shape))

    total = sum(len(f) for f in result_data.values()) if result_data else 0

    if total == 0:
        print("PASS: test_cube_at_origin_clean - 0 flipped faces (expected 0)")
        return True
    else:
        print("FAIL: test_cube_at_origin_clean - {} flipped faces (expected 0)".format(total))
        return False


def test_cube_at_origin_reversed():
    """
    BASELINE: Cube at origin with ALL normals reversed.
    Expected: FAIL detection - 6 flipped faces
    """
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name='reversed_cube')[0]

    # Reverse all normals
    cmds.polyNormal(cube, normalMode=0, userNormalMode=0)

    shape = cmds.listRelatives(cube, shapes=True)[0]
    result_type, result_data = mc.flippedNormals(None, get_selection_list(shape))

    total = sum(len(f) for f in result_data.values()) if result_data else 0

    if total == 6:
        print("PASS: test_cube_at_origin_reversed - {} flipped faces (expected 6)".format(total))
        return True
    else:
        print("FAIL: test_cube_at_origin_reversed - {} flipped faces (expected 6)".format(total))
        return False


# =============================================================================
# TRANSFORM TESTS - These will FAIL with the coordinate space bug
# =============================================================================

def test_translated_cube_clean():
    """
    BUG TEST: Cube translated 100 units on X with correct normals.
    Expected: PASS - 0 flipped faces

    WITH BUG: Will likely report false positives because:
    - Bounding box center is at (0,0,0) in object space
    - Face centers are at ~(100,0,0) in world space
    - The vector comparison is invalid across coordinate spaces
    """
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name='translated_cube')[0]

    # Translate far from origin
    cmds.move(100, 0, 0, cube)

    shape = cmds.listRelatives(cube, shapes=True)[0]
    result_type, result_data = mc.flippedNormals(None, get_selection_list(shape))

    total = sum(len(f) for f in result_data.values()) if result_data else 0

    if total == 0:
        print("PASS: test_translated_cube_clean - 0 flipped faces (expected 0)")
        return True
    else:
        print("FAIL: test_translated_cube_clean - {} flipped faces (expected 0)".format(total))
        print("      This indicates the COORDINATE SPACE BUG exists!")
        return False


def test_translated_cube_reversed():
    """
    Cube translated 100 units with ALL normals reversed.
    Expected: 6 flipped faces detected
    """
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name='translated_reversed')[0]

    # Translate and reverse
    cmds.move(100, 0, 0, cube)
    cmds.polyNormal(cube, normalMode=0, userNormalMode=0)

    shape = cmds.listRelatives(cube, shapes=True)[0]
    result_type, result_data = mc.flippedNormals(None, get_selection_list(shape))

    total = sum(len(f) for f in result_data.values()) if result_data else 0

    if total == 6:
        print("PASS: test_translated_cube_reversed - {} flipped faces (expected 6)".format(total))
        return True
    else:
        print("FAIL: test_translated_cube_reversed - {} flipped faces (expected 6)".format(total))
        return False


def test_negative_translated_cube_clean():
    """
    BUG TEST: Cube translated to negative coordinates with correct normals.
    Expected: PASS - 0 flipped faces
    """
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name='neg_translated_cube')[0]

    # Translate to negative coordinates
    cmds.move(-50, -50, -50, cube)

    shape = cmds.listRelatives(cube, shapes=True)[0]
    result_type, result_data = mc.flippedNormals(None, get_selection_list(shape))

    total = sum(len(f) for f in result_data.values()) if result_data else 0

    if total == 0:
        print("PASS: test_negative_translated_cube_clean - 0 flipped faces (expected 0)")
        return True
    else:
        print("FAIL: test_negative_translated_cube_clean - {} flipped faces (expected 0)".format(total))
        print("      This indicates the COORDINATE SPACE BUG exists!")
        return False


def test_rotated_cube_clean():
    """
    BUG TEST: Cube rotated 45 degrees on all axes with correct normals.
    Expected: PASS - 0 flipped faces

    WITH BUG: Rotation changes world-space face normals but not object-space
    bounding box, causing potential misdetection.
    """
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name='rotated_cube')[0]

    # Apply rotation
    cmds.rotate(45, 45, 45, cube)

    shape = cmds.listRelatives(cube, shapes=True)[0]
    result_type, result_data = mc.flippedNormals(None, get_selection_list(shape))

    total = sum(len(f) for f in result_data.values()) if result_data else 0

    if total == 0:
        print("PASS: test_rotated_cube_clean - 0 flipped faces (expected 0)")
        return True
    else:
        print("FAIL: test_rotated_cube_clean - {} flipped faces (expected 0)".format(total))
        print("      This indicates the COORDINATE SPACE BUG exists!")
        return False


def test_scaled_cube_clean():
    """
    BUG TEST: Cube with non-uniform scale and correct normals.
    Expected: PASS - 0 flipped faces
    """
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name='scaled_cube')[0]

    # Apply non-uniform scale
    cmds.scale(2, 0.5, 3, cube)

    shape = cmds.listRelatives(cube, shapes=True)[0]
    result_type, result_data = mc.flippedNormals(None, get_selection_list(shape))

    total = sum(len(f) for f in result_data.values()) if result_data else 0

    if total == 0:
        print("PASS: test_scaled_cube_clean - 0 flipped faces (expected 0)")
        return True
    else:
        print("FAIL: test_scaled_cube_clean - {} flipped faces (expected 0)".format(total))
        print("      This indicates the COORDINATE SPACE BUG exists!")
        return False


def test_combined_transforms_clean():
    """
    BUG TEST: Cube with translation + rotation + scale, correct normals.
    Expected: PASS - 0 flipped faces

    This is the most comprehensive transform test.
    """
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name='transformed_cube')[0]

    # Apply all transforms
    cmds.move(25, -10, 50, cube)
    cmds.rotate(30, 60, 15, cube)
    cmds.scale(1.5, 2.0, 0.8, cube)

    shape = cmds.listRelatives(cube, shapes=True)[0]
    result_type, result_data = mc.flippedNormals(None, get_selection_list(shape))

    total = sum(len(f) for f in result_data.values()) if result_data else 0

    if total == 0:
        print("PASS: test_combined_transforms_clean - 0 flipped faces (expected 0)")
        return True
    else:
        print("FAIL: test_combined_transforms_clean - {} flipped faces (expected 0)".format(total))
        print("      This indicates the COORDINATE SPACE BUG exists!")
        return False


def test_combined_transforms_reversed():
    """
    Cube with all transforms AND reversed normals.
    Expected: 6 flipped faces detected
    """
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name='transformed_reversed')[0]

    # Apply all transforms and reverse
    cmds.move(25, -10, 50, cube)
    cmds.rotate(30, 60, 15, cube)
    cmds.scale(1.5, 2.0, 0.8, cube)
    cmds.polyNormal(cube, normalMode=0, userNormalMode=0)

    shape = cmds.listRelatives(cube, shapes=True)[0]
    result_type, result_data = mc.flippedNormals(None, get_selection_list(shape))

    total = sum(len(f) for f in result_data.values()) if result_data else 0

    if total == 6:
        print("PASS: test_combined_transforms_reversed - {} flipped faces (expected 6)".format(total))
        return True
    else:
        print("FAIL: test_combined_transforms_reversed - {} flipped faces (expected 6)".format(total))
        return False


def test_sphere_translated_clean():
    """
    BUG TEST: Sphere translated with correct normals.
    Spheres are a good test because all faces point outward uniformly.
    Expected: PASS - 0 flipped faces
    """
    cmds.file(new=True, force=True)
    sphere = cmds.polySphere(name='translated_sphere', subdivisionsX=8, subdivisionsY=8)[0]

    # Translate away from origin
    cmds.move(0, 100, 0, sphere)

    shape = cmds.listRelatives(sphere, shapes=True)[0]
    result_type, result_data = mc.flippedNormals(None, get_selection_list(shape))

    total = sum(len(f) for f in result_data.values()) if result_data else 0

    if total == 0:
        print("PASS: test_sphere_translated_clean - 0 flipped faces (expected 0)")
        return True
    else:
        print("FAIL: test_sphere_translated_clean - {} flipped faces (expected 0)".format(total))
        print("      This indicates the COORDINATE SPACE BUG exists!")
        return False


def test_frozen_transforms_cube():
    """
    CONTROL TEST: Cube with transforms that have been FROZEN.
    After freezing, transforms are baked into vertices, so object space = world space.
    This should PASS even with the bug (proves the bug is transform-related).
    Expected: PASS - 0 flipped faces
    """
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name='frozen_cube')[0]

    # Apply transforms
    cmds.move(100, 50, -25, cube)
    cmds.rotate(45, 30, 60, cube)

    # FREEZE transforms - bakes into vertex positions
    cmds.makeIdentity(cube, apply=True, translate=True, rotate=True, scale=True)

    shape = cmds.listRelatives(cube, shapes=True)[0]
    result_type, result_data = mc.flippedNormals(None, get_selection_list(shape))

    total = sum(len(f) for f in result_data.values()) if result_data else 0

    if total == 0:
        print("PASS: test_frozen_transforms_cube - 0 flipped faces (expected 0)")
        print("      (Frozen transforms work because object space == world space)")
        return True
    else:
        print("FAIL: test_frozen_transforms_cube - {} flipped faces (expected 0)".format(total))
        return False


# =============================================================================
# NEGATIVE SCALE TEST (special case)
# =============================================================================

def test_negative_scale_cube():
    """
    EDGE CASE: Cube with negative scale (mirrors geometry).
    Negative scale ACTUALLY flips normals in world space!
    Expected: Should detect flipped faces (this is correct behavior)

    Note: This is a known Maya behavior - negative scale inverts normals.
    """
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name='neg_scale_cube')[0]

    # Negative scale on one axis mirrors the geometry
    cmds.scale(-1, 1, 1, cube)

    shape = cmds.listRelatives(cube, shapes=True)[0]
    result_type, result_data = mc.flippedNormals(None, get_selection_list(shape))

    total = sum(len(f) for f in result_data.values()) if result_data else 0

    # With negative scale, normals ARE actually flipped in world space
    # So detecting them is CORRECT behavior
    print("INFO: test_negative_scale_cube - {} flipped faces detected".format(total))
    print("      Negative scale inverts normals - detection is expected behavior")
    return True  # This documents behavior, not a pass/fail test


# =============================================================================
# RUN ALL TESTS
# =============================================================================

def run_all_tests():
    print("")
    print("=" * 75)
    print("  flippedNormals COORDINATE SPACE BUG - Test Suite")
    print("=" * 75)
    print("")
    print("  If the bug EXISTS, transform tests will FAIL (false positives).")
    print("  After the fix, ALL tests should PASS.")
    print("")
    print("-" * 75)

    results = []

    # Baseline tests (should pass with or without bug)
    print("\\n[BASELINE TESTS - Origin]")
    results.append(("Cube at origin (clean)", test_cube_at_origin_clean()))
    results.append(("Cube at origin (reversed)", test_cube_at_origin_reversed()))

    # Transform tests (will FAIL with bug)
    print("\\n[TRANSFORM TESTS - Will expose bug]")
    results.append(("Translated cube (clean)", test_translated_cube_clean()))
    results.append(("Translated cube (reversed)", test_translated_cube_reversed()))
    results.append(("Negative translated cube", test_negative_translated_cube_clean()))
    results.append(("Rotated cube (clean)", test_rotated_cube_clean()))
    results.append(("Scaled cube (clean)", test_scaled_cube_clean()))
    results.append(("Combined transforms (clean)", test_combined_transforms_clean()))
    results.append(("Combined transforms (reversed)", test_combined_transforms_reversed()))
    results.append(("Sphere translated (clean)", test_sphere_translated_clean()))

    # Control test
    print("\\n[CONTROL TESTS]")
    results.append(("Frozen transforms cube", test_frozen_transforms_cube()))

    # Edge case (informational)
    print("\\n[EDGE CASES - Informational]")
    test_negative_scale_cube()

    # Summary
    print("")
    print("=" * 75)
    print("  SUMMARY")
    print("=" * 75)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        print("  [{}] {}".format(status, name))

    print("")
    print("  Total: {}/{} tests passed".format(passed, total))
    print("")

    if passed < total:
        print("  *** COORDINATE SPACE BUG CONFIRMED ***")
        print("  The failing tests prove the bug exists.")
        print("  Fix: Use consistent coordinate space (object or world)")
    else:
        print("  All tests passed - bug is FIXED!")

    print("=" * 75)

    return passed == total

# Run the tests
run_all_tests()
'''


def get_test_script():
    """Return the Maya test script for copy/paste."""
    return MAYA_TEST_SCRIPT


if __name__ == "__main__":
    print("=" * 75)
    print("  flippedNormals Coordinate Space Bug - Test Suite")
    print("=" * 75)
    print()
    print("  PURPOSE: Validate the coordinate space bug fix for flippedNormals")
    print()
    print("  BUG: The current implementation compares:")
    print("    - Bounding box center in OBJECT space")
    print("    - Face center/normal in WORLD space")
    print()
    print("  IMPACT: False positives for meshes with transforms")
    print()
    print("  TO RUN:")
    print("    1. Open Maya")
    print("    2. Ensure modelChecker is in your Python path")
    print("    3. Copy MAYA_TEST_SCRIPT into Script Editor")
    print("    4. Execute")
    print()
    print("  EXPECTED RESULTS:")
    print("    - BEFORE fix: Transform tests will FAIL")
    print("    - AFTER fix: All tests should PASS")
    print()
    print("=" * 75)
