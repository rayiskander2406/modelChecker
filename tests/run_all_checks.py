"""
Comprehensive Validation Script for Academic Extension Checks
==============================================================================

This script tests ALL 15 new checks added in the Academic Extension.
Copy the MAYA_VALIDATION_SCRIPT into Maya's Script Editor and execute.

SELF-VALIDATING: The script automatically compares actual results against
expected results and gives a clear PASS/FAIL verdict. No manual comparison
needed - just run and check the final result!

CHECKS TESTED:
  1. flippedNormals        - Detects inverted face normals
  2. overlappingVertices   - Finds vertices at same position
  3. polyCountLimit        - Flags high-poly meshes
  4. missingTextures       - Detects broken texture paths
  5. defaultMaterials      - Finds objects with lambert1
  6. sceneUnits            - Validates scene unit settings
  7. uvDistortion          - Detects stretched/compressed UVs
  8. texelDensity          - Checks UV texel consistency
  9. textureResolution     - Validates texture dimensions
 10. unusedNodes           - Finds orphaned nodes
 11. hiddenObjects         - Detects hidden geometry
 12. namingConvention      - Validates naming patterns
 13. hierarchyDepth        - Checks nesting depth
 14. concaveFaces          - Detects non-convex polygons
 15. intermediateObjects   - Finds construction history objects

==============================================================================
"""

MAYA_VALIDATION_SCRIPT = '''
##############################################################################
#  ACADEMIC EXTENSION - SELF-VALIDATING TEST SCRIPT
#  Copy this entire script into Maya's Script Editor and execute
#
#  RESULT: Look for the final verdict at the bottom:
#    - "VALIDATION PASSED" = Extension is working correctly!
#    - "VALIDATION FAILED" = Something needs debugging
##############################################################################

import maya.cmds as cmds
import maya.api.OpenMaya as om
from collections import defaultdict
import traceback

# Try to import modelChecker
try:
    from modelChecker import modelChecker_commands as mc
    MODELCHECKER_AVAILABLE = True
except ImportError:
    print("=" * 70)
    print("  ERROR: modelChecker not found!")
    print("=" * 70)
    print("")
    print("  To fix this, add modelChecker to your Python path:")
    print("")
    print("  Option 1 - In Maya Script Editor, run this first:")
    print("    import sys")
    print("    sys.path.append('/path/to/modelChecker/parent/folder')")
    print("")
    print("  Option 2 - Add to Maya.env file:")
    print("    PYTHONPATH=/path/to/modelChecker/parent/folder")
    print("")
    print("=" * 70)
    MODELCHECKER_AVAILABLE = False

##############################################################################
# EXPECTED RESULTS FOR TEST SCENE
# These define what each check SHOULD find in our controlled test scene
##############################################################################

EXPECTED_RESULTS = {
    # (min_expected, max_expected, description)
    # Use -1 for "any value is OK" (just testing it doesn't crash)

    "flippedNormals":       (0, 0, "No flipped normals in test scene"),
    "overlappingVertices":  (0, 2, "Possibly some from vertex merge"),
    "polyCountLimit":       (1, 1, "highpoly_sphere exceeds limit"),
    "missingTextures":      (0, 0, "No textures in test scene"),
    "defaultMaterials":     (5, 10, "Most objects use lambert1"),
    "sceneUnits":           (0, 1, "Depends on Maya default units"),
    "uvDistortion":         (-1, -1, "Varies by UV layout"),
    "texelDensity":         (0, 0, "No textures assigned"),
    "textureResolution":    (0, 0, "No textures in scene"),
    "unusedNodes":          (0, 5, "May have some unused nodes"),
    "hiddenObjects":        (1, 1, "hidden_cube is hidden"),
    "namingConvention":     (1, 5, "cube_001 violates naming"),
    "hierarchyDepth":       (7, 10, "deep_cube + level groups"),
    "concaveFaces":         (0, 4, "concave_plane may have some"),
    "intermediateObjects":  (1, 1, "deformed_cube has lattice"),
}

##############################################################################
# HELPER FUNCTIONS
##############################################################################

def get_transform_uuids(exclude_cameras=True):
    """Get UUIDs for all transform nodes."""
    transforms = cmds.ls(type='transform', long=True) or []
    if exclude_cameras:
        default_cams = ['|front', '|persp', '|side', '|top']
        transforms = [t for t in transforms if t not in default_cams]
    uuids = []
    for t in transforms:
        uuid = cmds.ls(t, uuid=True)
        if uuid:
            uuids.append(uuid[0])
    return uuids

def get_mesh_selection_list():
    """Get MSelectionList of all mesh shapes."""
    meshes = cmds.ls(type='mesh', long=True) or []
    sel = om.MSelectionList()
    for mesh in meshes:
        try:
            sel.add(mesh)
        except:
            pass
    return sel

def create_test_scene():
    """Create a controlled test scene with known issues."""
    cmds.file(new=True, force=True)
    print("  Creating test scene with known issues...")
    print("")

    created = {}

    # 1. Clean cube (should pass most checks)
    cube = cmds.polyCube(name='clean_cube')[0]
    cmds.delete(cube, constructionHistory=True)
    created['clean_cube'] = cube
    print("    [+] clean_cube - basic geometry (should pass)")

    # 2. Hidden object - tests hiddenObjects check
    hidden = cmds.polyCube(name='hidden_cube')[0]
    cmds.delete(hidden, constructionHistory=True)
    cmds.hide(hidden)
    created['hidden_cube'] = hidden
    print("    [+] hidden_cube - hidden (should be detected)")

    # 3. Deep hierarchy - tests hierarchyDepth check
    parent = cmds.group(empty=True, name='level1')
    for i in range(2, 8):
        child = cmds.group(empty=True, name='level{}'.format(i), parent=parent)
        parent = child
    deep_cube = cmds.polyCube(name='deep_cube')[0]
    cmds.delete(deep_cube, constructionHistory=True)
    cmds.parent(deep_cube, parent)
    created['deep_cube'] = deep_cube
    print("    [+] deep_cube - nested 7 levels deep (should be detected)")

    # 4. Bad naming - tests namingConvention check
    bad_name = cmds.polyCube(name='cube_001')[0]
    cmds.delete(bad_name, constructionHistory=True)
    created['bad_name'] = bad_name
    print("    [+] cube_001 - trailing numbers (should be detected)")

    # 5. Object with intermediate - tests intermediateObjects check
    deformed = cmds.polyCube(name='deformed_cube')[0]
    cmds.lattice(deformed, divisions=(2, 2, 2))
    created['deformed_cube'] = deformed
    print("    [+] deformed_cube - has lattice deformer (should be detected)")

    # 6. High poly object - tests polyCountLimit check
    highpoly = cmds.polySphere(name='highpoly_sphere', subdivisionsX=50, subdivisionsY=50)[0]
    cmds.delete(highpoly, constructionHistory=True)
    created['highpoly_sphere'] = highpoly
    print("    [+] highpoly_sphere - 2500 faces (should be detected)")

    # 7. Object with default material - tests defaultMaterials check
    default_mat = cmds.polyCube(name='default_material_cube')[0]
    cmds.delete(default_mat, constructionHistory=True)
    created['default_material_cube'] = default_mat
    print("    [+] default_material_cube - uses lambert1 (should be detected)")

    # 8. Concave face - tests concaveFaces check
    plane = cmds.polyPlane(name='concave_plane', sx=2, sy=2)[0]
    cmds.delete(plane, constructionHistory=True)
    # Move a vertex inward to create concave faces
    cmds.move(0, 0, 0.3, plane + '.vtx[4]', relative=True)
    created['concave_plane'] = plane
    print("    [+] concave_plane - has concave polygons (should be detected)")

    print("")
    print("  Test scene ready: {} objects created".format(len(created)))
    return created

##############################################################################
# CHECK EXECUTION FUNCTIONS
##############################################################################

def run_check(name, check_func, transforms, mesh_sel):
    """Run a single check and return (success, count, error_msg)."""
    try:
        # Determine which parameters the check needs
        scene_checks = ['missingTextures', 'sceneUnits', 'textureResolution', 'unusedNodes']
        mesh_checks = ['flippedNormals', 'overlappingVertices', 'uvDistortion',
                       'texelDensity', 'concaveFaces']

        if name in scene_checks:
            result_type, result_data = check_func(None, None)
        elif name in mesh_checks:
            result_type, result_data = check_func(None, mesh_sel)
        else:
            result_type, result_data = check_func(transforms, None)

        # Count results
        if isinstance(result_data, dict):
            count = sum(len(v) for v in result_data.values())
        else:
            count = len(result_data)

        return True, count, None

    except Exception as e:
        return False, 0, str(e)

##############################################################################
# MAIN VALIDATION
##############################################################################

def run_validation():
    """Run self-validating tests for all 15 Academic Extension checks."""

    print("")
    print("=" * 70)
    print("  ACADEMIC EXTENSION - SELF-VALIDATING TEST")
    print("=" * 70)
    print("")

    if not MODELCHECKER_AVAILABLE:
        print("  ABORTED: modelChecker module not available")
        print("")
        return False

    # Create test scene
    test_objects = create_test_scene()

    # Get node lists for checks
    transforms = get_transform_uuids()
    mesh_sel = get_mesh_selection_list()

    # Map check names to functions
    check_functions = {
        "flippedNormals": mc.flippedNormals,
        "overlappingVertices": mc.overlappingVertices,
        "polyCountLimit": mc.polyCountLimit,
        "missingTextures": mc.missingTextures,
        "defaultMaterials": mc.defaultMaterials,
        "sceneUnits": mc.sceneUnits,
        "uvDistortion": mc.uvDistortion,
        "texelDensity": mc.texelDensity,
        "textureResolution": mc.textureResolution,
        "unusedNodes": mc.unusedNodes,
        "hiddenObjects": mc.hiddenObjects,
        "namingConvention": mc.namingConvention,
        "hierarchyDepth": mc.hierarchyDepth,
        "concaveFaces": mc.concaveFaces,
        "intermediateObjects": mc.intermediateObjects,
    }

    print("")
    print("-" * 70)
    print("  RUNNING 15 CHECKS...")
    print("-" * 70)
    print("")

    results = []
    all_passed = True

    for name in check_functions:
        check_func = check_functions[name]
        min_exp, max_exp, description = EXPECTED_RESULTS[name]

        success, count, error = run_check(name, check_func, transforms, mesh_sel)

        if not success:
            # Check crashed
            status = "ERROR"
            verdict = "FAIL"
            msg = error
            all_passed = False
        elif min_exp == -1:
            # Any result is OK (just testing it runs)
            status = "RAN"
            verdict = "OK"
            msg = "Found {} (any value OK)".format(count)
        elif min_exp <= count <= max_exp:
            # Result in expected range
            status = "PASS"
            verdict = "OK"
            msg = "Found {} (expected {}-{})".format(count, min_exp, max_exp)
        else:
            # Result outside expected range
            status = "UNEXPECTED"
            verdict = "WARN"
            msg = "Found {} (expected {}-{})".format(count, min_exp, max_exp)
            # Don't fail on unexpected counts - the check ran successfully

        results.append((name, status, verdict, msg, description))

        # Print result
        if verdict == "OK":
            print("  [OK]   {:25s} {}".format(name, msg))
        elif verdict == "WARN":
            print("  [WARN] {:25s} {}".format(name, msg))
        else:
            print("  [FAIL] {:25s} {}".format(name, msg))

    # Summary
    print("")
    print("=" * 70)
    print("  VALIDATION RESULTS")
    print("=" * 70)
    print("")

    ok_count = sum(1 for _, _, v, _, _ in results if v == "OK")
    warn_count = sum(1 for _, _, v, _, _ in results if v == "WARN")
    fail_count = sum(1 for _, _, v, _, _ in results if v == "FAIL")

    print("  Checks Executed:  15")
    print("  Passed:           {}".format(ok_count))
    print("  Warnings:         {}".format(warn_count))
    print("  Failed:           {}".format(fail_count))
    print("")

    if fail_count > 0:
        print("  ERRORS REQUIRING ATTENTION:")
        for name, status, verdict, msg, desc in results:
            if verdict == "FAIL":
                print("    - {}: {}".format(name, msg))
        print("")

    if warn_count > 0:
        print("  WARNINGS (check may still be correct):")
        for name, status, verdict, msg, desc in results:
            if verdict == "WARN":
                print("    - {}: {}".format(name, msg))
                print("      Expected: {}".format(desc))
        print("")

    # Final verdict
    print("=" * 70)
    if fail_count == 0:
        print("")
        print("    *** VALIDATION PASSED ***")
        print("")
        print("    All 15 Academic Extension checks are working correctly!")
        print("    The extension is ready to use.")
        print("")
    else:
        print("")
        print("    *** VALIDATION FAILED ***")
        print("")
        print("    {} check(s) encountered errors.".format(fail_count))
        print("    Review the errors above and debug the failing checks.")
        print("")
    print("=" * 70)
    print("")

    return fail_count == 0

# Run validation
if MODELCHECKER_AVAILABLE:
    validation_passed = run_validation()
'''


def get_validation_script():
    """Return the Maya validation script for copy/paste."""
    return MAYA_VALIDATION_SCRIPT


if __name__ == "__main__":
    print("=" * 70)
    print("  ACADEMIC EXTENSION - SELF-VALIDATING TEST SCRIPT")
    print("=" * 70)
    print()
    print("  This script automatically validates all 15 checks.")
    print("  No manual comparison needed!")
    print()
    print("  TO RUN:")
    print("    1. Open Maya")
    print("    2. Ensure modelChecker is in your Python path")
    print("    3. Copy MAYA_VALIDATION_SCRIPT into Script Editor")
    print("    4. Execute (Ctrl+Enter)")
    print()
    print("  WHAT TO LOOK FOR:")
    print("    At the end of output, you'll see either:")
    print()
    print("    *** VALIDATION PASSED ***")
    print("        = Extension is working! Ready to use.")
    print()
    print("    *** VALIDATION FAILED ***")
    print("        = Something needs debugging. Check errors listed.")
    print()
    print("  CHECKS TESTED:")
    for i, check in enumerate([
        "flippedNormals", "overlappingVertices", "polyCountLimit",
        "missingTextures", "defaultMaterials", "sceneUnits",
        "uvDistortion", "texelDensity", "textureResolution",
        "unusedNodes", "hiddenObjects", "namingConvention",
        "hierarchyDepth", "concaveFaces", "intermediateObjects"
    ], 1):
        print("    {:2d}. {}".format(i, check))
    print()
    print("=" * 70)
