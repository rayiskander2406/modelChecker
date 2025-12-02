from collections import defaultdict

import maya.cmds as cmds
import maya.api.OpenMaya as om

# Returns Error Tuple
#     "uv": {}, [UUID] : [... uvId]
#     "vertex": {},[UUID] : [... vertexId ]
#     "edge" : {},[UUID] : [... edgeId ]
#     "polygon": {}, -> [UUID] : [... polygonId ]
#     "nodes" : [] -> [... nodes UUIDs]

# Internal Utility Functions
def _getNodeName(uuid):
    nodeName = cmds.ls(uuid, uuid=True)
    if nodeName:
        return nodeName[0]
    return None


# Functions to be imported
def trailingNumbers(nodes, _):
    trailingNumbers = []
    for node in nodes:
        nodeName = _getNodeName(node)
        if nodeName and nodeName[-1].isdigit():
                trailingNumbers.append(node)
    return "nodes", trailingNumbers

def duplicatedNames(nodes, _):
    nodesByShortName = defaultdict(list)
    for node in nodes:
        nodeName = _getNodeName(node)
        name = nodeName.rsplit('|', 1)[-1]
        nodesByShortName[name].append(node)
    invalid = []
    for name, shortNameNodes in nodesByShortName.items():
        if len(shortNameNodes) > 1:
            invalid.extend(shortNameNodes)
    return "nodes", invalid


def namespaces(nodes, _):
    namespaces = []
    for node in nodes:
        nodeName = _getNodeName(node)
        if nodeName and ':' in nodeName:
            namespaces.append(node)
    return "nodes", namespaces


def shapeNames(nodes, _):
    shapeNames = []
    for node in nodes:
        nodeName = _getNodeName(node)
        if nodeName:
            new = nodeName.split('|')
            shape = cmds.listRelatives(nodeName, shapes=True)
            if shape:
                shapename = new[-1] + "Shape"
                if shape[0] != shapename:
                    shapeNames.append(node)
    return "nodes", shapeNames

def triangles(_, SLMesh):
    triangles = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not faceIt.isDone():
            numOfEdges = faceIt.getEdges()
            if len(numOfEdges) == 3:
                triangles[uuid].append(faceIt.index())
            faceIt.next()
        selIt.next()
    return "polygon", triangles


def ngons(_, SLMesh):
    ngons = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not faceIt.isDone():
            numOfEdges = faceIt.getEdges()
            if len(numOfEdges) > 4:
                ngons[uuid].append(faceIt.index())
            faceIt.next()
        selIt.next()
    return "polygon", ngons

def hardEdges(_, SLMesh):
    hardEdges = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not edgeIt.isDone():
            if edgeIt.isSmooth is False and edgeIt.onBoundary() is False:
                hardEdges[uuid].append(edgeIt.index())
            edgeIt.next()
        selIt.next()
    return "edge", hardEdges

def lamina(_, SLMesh):
    lamina = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not faceIt.isDone():
            laminaFaces = faceIt.isLamina()
            if laminaFaces is True:
                lamina[uuid].append(faceIt.index())
            faceIt.next()
        selIt.next()
    return "polygon", lamina


def zeroAreaFaces(_, SLMesh):
    zeroAreaFaces = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not faceIt.isDone():
            faceArea = faceIt.getArea()
            if faceArea <= 0.00000001:
                zeroAreaFaces[uuid].append(faceIt.index())
            faceIt.next()
        selIt.next()
    return "polygon", zeroAreaFaces


def zeroLengthEdges(_, SLMesh):
    zeroLengthEdges = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not edgeIt.isDone():
            if edgeIt.length() <= 0.00000001:
                zeroLengthEdges[uuid].append(edgeIt.index())
            edgeIt.next()
        selIt.next()
    return "edge", zeroLengthEdges

def selfPenetratingUVs(transformNodes, _):
    selfPenetratingUVs = defaultdict(list)
    for node in transformNodes:
        nodeName = _getNodeName(node)
        shapes = cmds.listRelatives(
            nodeName,
            shapes=True,
            type="mesh",
            noIntermediate=True)
        if shapes:
            overlapping = cmds.polyUVOverlap("{}.f[*]".format(shapes[0]), oc=True)
            if overlapping:
                formatted = [ overlap.split("{}.f[".format(shapes[0]))[1][:-1] for overlap in overlapping ]
                selfPenetratingUVs[node].extend(formatted)
    return "polygon", selfPenetratingUVs

def noneManifoldEdges(_, SLMesh):
    noneManifoldEdges = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not edgeIt.isDone():
            if edgeIt.numConnectedFaces() > 2:
                noneManifoldEdges[uuid].append(edgeIt.index())
            edgeIt.next()
        selIt.next()
    return "edge", noneManifoldEdges


def openEdges(_, SLMesh):
    openEdges = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not edgeIt.isDone():
            if edgeIt.numConnectedFaces() < 2:
                openEdges[uuid].append(edgeIt.index())
            edgeIt.next()
        selIt.next()
    return "edge", openEdges


def poles(_, SLMesh):
    poles = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        vertexIt = om.MItMeshVertex(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not vertexIt.isDone():
            if vertexIt.numConnectedEdges() > 5:
                poles[uuid].append(vertexIt.index())
            vertexIt.next()
        selIt.next()
    return "vertex", poles


def starlike(_, SLMesh):
    noneStarlike = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        polyIt = om.MItMeshPolygon(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not polyIt.isDone():
            if polyIt.isStarlike() is False:
                noneStarlike[uuid].append(polyIt.index())
            polyIt.next()
        selIt.next()
    return "polygon", noneStarlike

def missingUVs(_, SLMesh):
    missingUVs = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not faceIt.isDone():
            if faceIt.hasUVs() is False:
                missingUVs[uuid].append(faceIt.index())
            faceIt.next()
        selIt.next()
    return "polygon", missingUVs

def uvRange(_, SLMesh):
    uvRange = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        mesh = om.MFnMesh(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        Us, Vs = mesh.getUVs()
        for i in range(len(Us)):
            if Us[i] < 0 or Us[i] > 10 or Vs[i] < 0:
                uvRange[uuid].append(i)
        selIt.next()
    return "uv", uvRange

def onBorder(_, SLMesh):
    onBorder = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        mesh = om.MFnMesh(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        Us, Vs = mesh.getUVs()
        for i in range(len(Us)):
            if abs(int(Us[i]) - Us[i]) < 0.00001 or abs(int(Vs[i]) - Vs[i]) < 0.00001:
                onBorder[uuid].append(i)
        selIt.next()
    return "uv", onBorder

def crossBorder(_, SLMesh):
    crossBorder = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not faceIt.isDone():
            U, V = set(), set()
            try:
                UVs = faceIt.getUVs()
                Us, Vs, = UVs[0], UVs[1]
                for i in range(len(Us)):
                    uAdd = int(Us[i]) if Us[i] > 0 else int(Us[i]) - 1
                    vAdd = int(Vs[i]) if Vs[i] > 0 else int(Vs[i]) - 1
                    U.add(uAdd)
                    V.add(vAdd)
                if len(U) > 1 or len(V) > 1:
                    crossBorder[uuid].append(faceIt.index())
                faceIt.next()
            except:
                cmds.warning("Face " + str(faceIt.index()) + " has no UVs")
                faceIt.next()
        selIt.next()
    return "polygon", crossBorder

def unfrozenTransforms(nodes, _):
    unfrozenTransforms = []
    for node in nodes:
        nodeName = _getNodeName(node)
        translation = cmds.xform(
            nodeName, q=True, worldSpace=True, translation=True)
        rotation = cmds.xform(nodeName, q=True, worldSpace=True, rotation=True)
        scale = cmds.xform(nodeName, q=True, worldSpace=True, scale=True)
        if translation != [0.0, 0.0, 0.0] or rotation != [0.0, 0.0, 0.0] or scale != [1.0, 1.0, 1.0]:
            unfrozenTransforms.append(node)
    return "nodes", unfrozenTransforms

def layers(nodes, _):
    layers = []
    for node in nodes:
        nodeName = _getNodeName(node)
        layer = cmds.listConnections(nodeName, type="displayLayer")
        if layer:
            layers.append(node)
    return "nodes", layers

def shaders(transformNodes, _):
    shaders = []
    for node in transformNodes:
        nodeName = _getNodeName(node)
        shape = cmds.listRelatives(nodeName, shapes=True, fullPath=True)
        if cmds.nodeType(shape) == 'mesh' and shape:
            shadingGrps = cmds.listConnections(shape, type='shadingEngine')
            if shadingGrps[0] != 'initialShadingGroup':
                shaders.append(node)
    return "nodes", shaders

def history(nodes, _):
    history = []
    for node in nodes:
        nodeName = _getNodeName(node)
        shape = cmds.listRelatives(nodeName, shapes=True, fullPath=True)
        if shape and cmds.nodeType(shape[0]) == 'mesh':
            historySize = len(cmds.listHistory(shape))
            if historySize > 1:
                history.append(node)
    return "nodes", history

def uncenteredPivots(nodes, _):
    uncenteredPivots = []
    for node in nodes:
        nodeName = _getNodeName(node)
        if cmds.xform(nodeName, q=1, ws=1, rp=1) != [0, 0, 0]:
            uncenteredPivots.append(node)
    return "nodes", uncenteredPivots


def emptyGroups(nodes, _):
    emptyGroups = []
    for node in nodes:
        nodeName = _getNodeName(node)
        if not cmds.listRelatives(nodeName, ad=True):
            emptyGroups.append(node)
    return "nodes", emptyGroups

def parentGeometry(transformNodes, _):
    parentGeometry = []
    for node in transformNodes:
        nodeName = _getNodeName(node)
        parents = cmds.listRelatives(nodeName, p=True, fullPath=True)
        if parents:
            for parent in parents:
                children = cmds.listRelatives(parent, fullPath=True)
                for child in children:
                    if cmds.nodeType(child) == 'mesh':
                        parentGeometry.append(node)
    return "nodes", parentGeometry


def flippedNormals(_, SLMesh):
    """Detect faces with normals pointing inward (reversed/flipped normals).

    This check identifies polygons whose normals point toward the mesh center
    rather than outward, which typically causes rendering issues (black faces)
    and problems with lighting calculations.

    Algorithm:
        1. Calculate mesh bounding box center as reference point (object space)
        2. For each face, get its center and normal in object space
        3. Calculate vector from mesh center to face center
        4. If dot product of normal and this vector is negative,
           the normal points inward (flipped)

    Note:
        All calculations are performed in object space to ensure correct
        results regardless of the mesh's transform (translation, rotation,
        scale). This means the check works correctly even if the mesh is
        not at the world origin or has unfrozen transforms.

    Args:
        _: Unused parameter (node list, maintained for API consistency)
        SLMesh: MSelectionList containing mesh shapes to check

    Returns:
        tuple: ("polygon", dict) where dict maps UUID -> list of face indices
               with flipped normals

    Known Limitations:
        - Uses bounding box center as reference, which works well for convex
          and mostly-convex meshes (typical student/production models)
        - May produce false positives on highly concave meshes where faces
          legitimately point toward the bounding box center
        - For complex concave geometry, consider using Maya's native
          'Mesh Display > Reverse' or manual inspection

    Academic Use:
        This check is designed for academic evaluation where models are
        expected to be "clean" with consistent outward-facing normals.
        Students should review flagged faces and verify if they are
        intentionally inward-facing or errors.
    """
    flippedNormals = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        dagPath = selIt.getDagPath()
        mesh = om.MFnMesh(dagPath)
        fn = om.MFnDependencyNode(dagPath.node())
        uuid = fn.uuid().asString()

        # Get mesh bounding box center as reference point
        boundingBox = mesh.boundingBox
        meshCenter = boundingBox.center

        faceIt = om.MItMeshPolygon(dagPath)
        while not faceIt.isDone():
            # Get face center and normal in OBJECT space (matches bounding box space)
            faceCenter = faceIt.center(om.MSpace.kObject)
            faceNormal = faceIt.getNormal(om.MSpace.kObject)

            # Vector from mesh center to face center
            toFace = om.MVector(
                faceCenter.x - meshCenter.x,
                faceCenter.y - meshCenter.y,
                faceCenter.z - meshCenter.z
            )

            # If normal points toward center (negative dot product), it's flipped
            dotProduct = (faceNormal.x * toFace.x +
                         faceNormal.y * toFace.y +
                         faceNormal.z * toFace.z)

            if dotProduct < 0:
                flippedNormals[uuid].append(faceIt.index())

            faceIt.next()
        selIt.next()
    return "polygon", flippedNormals


def overlappingVertices(_, SLMesh):
    """Detect vertices that occupy the same position (stacked/overlapping vertices).

    This check identifies vertices that share the same spatial coordinates within
    a tolerance threshold. Overlapping vertices are a common issue that causes:
    - Shading artifacts (pinching, dark spots)
    - Problems with edge flow and topology
    - Export issues (FBX, OBJ may produce unexpected results)
    - Difficulty with proper welding/merging

    Algorithm:
        1. Get all vertex positions using MFnMesh.getPoints()
        2. Build a spatial hash grid for efficient O(n) comparison
        3. For each vertex, check nearby vertices within tolerance
        4. Report vertices that share positions with other vertices

    Args:
        _: Unused parameter (node list, maintained for API consistency)
        SLMesh: MSelectionList containing mesh shapes to check

    Returns:
        tuple: ("vertex", dict) where dict maps UUID -> list of vertex indices
               that have overlapping positions

    Known Limitations:
        - Default tolerance of 0.0001 may need adjustment for very small models
        - Does not distinguish between intentionally stacked vertices (e.g., for
          UV seams) and accidental overlaps
        - For meshes with UV seams, some "overlapping" vertices are expected
          behavior; use in conjunction with merge vertex operations

    Academic Use:
        Overlapping vertices often result from:
        - Incomplete merge operations after combining meshes
        - Accidental duplicate vertex creation
        - Boolean operations that leave stacked geometry
        Students should merge vertices or investigate why overlaps exist.
    """
    overlapping = defaultdict(list)
    tolerance = 0.0001  # Position tolerance for overlap detection

    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        dagPath = selIt.getDagPath()
        mesh = om.MFnMesh(dagPath)
        fn = om.MFnDependencyNode(dagPath.node())
        uuid = fn.uuid().asString()

        # Get all vertex positions in world space
        points = mesh.getPoints(om.MSpace.kWorld)
        numVerts = len(points)

        if numVerts == 0:
            selIt.next()
            continue

        # Build spatial hash for efficient lookup
        # Grid cell size slightly larger than tolerance
        cellSize = tolerance * 10
        spatialHash = defaultdict(list)

        for i, pt in enumerate(points):
            # Calculate grid cell for this vertex
            cellX = int(pt.x / cellSize)
            cellY = int(pt.y / cellSize)
            cellZ = int(pt.z / cellSize)
            spatialHash[(cellX, cellY, cellZ)].append((i, pt))

        # Track vertices we've already marked as overlapping
        markedVerts = set()

        # Check each vertex against nearby vertices
        for i, pt in enumerate(points):
            if i in markedVerts:
                continue

            cellX = int(pt.x / cellSize)
            cellY = int(pt.y / cellSize)
            cellZ = int(pt.z / cellSize)

            # Check this cell and adjacent cells
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        cell = (cellX + dx, cellY + dy, cellZ + dz)
                        if cell in spatialHash:
                            for j, otherPt in spatialHash[cell]:
                                if j <= i:
                                    continue  # Only compare forward to avoid duplicates

                                # Calculate distance
                                dist = ((pt.x - otherPt.x) ** 2 +
                                       (pt.y - otherPt.y) ** 2 +
                                       (pt.z - otherPt.z) ** 2) ** 0.5

                                if dist < tolerance:
                                    # Both vertices overlap
                                    if i not in markedVerts:
                                        overlapping[uuid].append(i)
                                        markedVerts.add(i)
                                    if j not in markedVerts:
                                        overlapping[uuid].append(j)
                                        markedVerts.add(j)

        selIt.next()
    return "vertex", overlapping


# Default polygon limit per mesh (can be customized)
POLY_COUNT_LIMIT = 10000


def polyCountLimit(nodes, SLMesh):
    """Detect meshes that exceed the polygon count limit.

    This check identifies meshes with more polygons than the configured limit.
    Exceeding polygon budgets is a common issue in academic projects where
    assignments often have strict poly count requirements.

    Algorithm:
        1. For each mesh in the selection, get the polygon count using MFnMesh
        2. Compare against the configured limit (default: 10,000 polygons)
        3. Flag meshes that exceed the limit

    Args:
        nodes: List of node UUIDs to check
        SLMesh: MSelectionList containing mesh shapes to check

    Returns:
        tuple: ("nodes", list) where list contains UUIDs of meshes
               that exceed the polygon limit

    Configuration:
        The default limit is 10,000 polygons per mesh. To customize:
        - Edit POLY_COUNT_LIMIT at the top of this file
        - Common academic limits: 5000, 10000, 15000, 50000

    Known Limitations:
        - Checks per-mesh, not total scene polygon count
        - Does not account for instances (each instance is counted separately)
        - Subdivision preview levels are not included in count

    Academic Use:
        Most academic 3D assignments specify polygon budgets:
        - Game character: 5,000 - 15,000 polys
        - Game prop: 500 - 5,000 polys
        - Environment asset: varies by scope
        Exceeding the limit typically results in point deductions.
    """
    overLimit = []

    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        dagPath = selIt.getDagPath()
        mesh = om.MFnMesh(dagPath)
        fn = om.MFnDependencyNode(dagPath.node())
        uuid = fn.uuid().asString()

        # Get polygon count
        polyCount = mesh.numPolygons

        if polyCount > POLY_COUNT_LIMIT:
            overLimit.append(uuid)

        selIt.next()

    return "nodes", overLimit


def missingTextures(nodes, _):
    """Detect file texture nodes referencing missing or non-existent files.

    This check identifies file texture nodes in the scene where the referenced
    texture file does not exist on disk. Missing textures are a common issue
    that causes:
    - Pink/magenta rendering in viewports and renders
    - Failed exports to game engines
    - Broken material appearance
    - File path issues when moving projects between computers

    Algorithm:
        1. Find all 'file' texture nodes in the scene
        2. For each file node, get the 'fileTextureName' attribute
        3. Check if the file exists on disk using os.path.exists
        4. Flag nodes where the file path is set but file doesn't exist

    Args:
        nodes: List of node UUIDs to check (not used - scene-wide check)
        _: MSelectionList (not used - scene-wide check)

    Returns:
        tuple: ("nodes", list) where list contains UUIDs of file texture
               nodes with missing texture files

    Known Limitations:
        - Only checks 'file' node type (not procedural textures)
        - Does not resolve UDIM patterns or animated textures
        - Network paths may report as missing if network is unavailable
        - Relative paths are resolved from Maya's current working directory

    Academic Use:
        Students often encounter missing textures when:
        - Moving projects between home and school computers
        - Using absolute paths instead of relative paths
        - Forgetting to include textures when submitting assignments
        This check helps catch these issues before submission.
    """
    import os

    missingFiles = []

    # Get all file texture nodes in the scene
    fileNodes = cmds.ls(type='file') or []

    for fileNode in fileNodes:
        # Get the file path from the texture node
        texturePath = cmds.getAttr(fileNode + '.fileTextureName')

        # Skip if no path is set (empty string)
        if not texturePath:
            continue

        # Check if the file exists
        if not os.path.exists(texturePath):
            # Get UUID for the file node
            uuid = cmds.ls(fileNode, uuid=True)
            if uuid:
                missingFiles.append(uuid[0])

    return "nodes", missingFiles


def defaultMaterials(transformNodes, _):
    """Detect meshes still using the default lambert1 material.

    This check identifies meshes that are assigned to the initialShadingGroup
    (lambert1), which typically indicates unfinished work. Default gray
    materials in a submission signal to evaluators that:
    - Texturing/material work was not completed
    - The model may have been rushed
    - Professional standards were not met

    Algorithm:
        1. For each transform node, get its shape(s)
        2. Query shading engine connections
        3. Flag meshes connected to 'initialShadingGroup'

    Args:
        transformNodes: List of transform node UUIDs to check
        _: MSelectionList (not used for this check)

    Returns:
        tuple: ("nodes", list) where list contains UUIDs of transforms
               whose meshes use the default material (lambert1)

    Known Limitations:
        - Only checks the first shading group connection
        - Multi-material objects may pass if any face has non-default material
        - Does not distinguish between lambert1 and other procedural materials

    Academic Use:
        In academic projects, using default materials signals incomplete work.
        Evaluators expect students to create and assign proper materials,
        even for simple models. This check catches objects that were
        forgotten during the texturing phase.
    """
    defaultMats = []

    for node in transformNodes:
        nodeName = _getNodeName(node)
        shape = cmds.listRelatives(nodeName, shapes=True, fullPath=True)

        if shape and cmds.nodeType(shape[0]) == 'mesh':
            # Get shading engines connected to this shape
            shadingGrps = cmds.listConnections(shape, type='shadingEngine')

            if shadingGrps:
                # Check if using initialShadingGroup (lambert1)
                if shadingGrps[0] == 'initialShadingGroup':
                    defaultMats.append(node)

    return "nodes", defaultMats


# Expected linear units for academic projects (can be customized)
# Common values: 'cm' (centimeters - Maya default, game engines)
#               'm' (meters - architectural, some engines)
#               'mm' (millimeters - precision work)
EXPECTED_LINEAR_UNIT = 'cm'


def sceneUnits(_, __):
    """Verify scene linear units match the expected standard.

    This check validates that the scene's linear unit setting matches the
    expected value (default: centimeters). Incorrect units are a common
    cause of scale issues when:
    - Exporting to game engines (Unity, Unreal)
    - Importing into other 3D software
    - Collaborating with team members
    - Submitting academic work for evaluation

    Algorithm:
        1. Query Maya's current linear unit using cmds.currentUnit()
        2. Compare against the expected unit (EXPECTED_LINEAR_UNIT)
        3. Return a special indicator if units don't match

    Args:
        _: Not used (scene-level check, not per-node)
        __: Not used (scene-level check)

    Returns:
        tuple: ("nodes", list) where list contains a single special marker
               'SCENE_UNITS_MISMATCH' if units don't match expected,
               or empty list if units are correct

    Configuration:
        The expected unit is set via EXPECTED_LINEAR_UNIT at the top of
        this file. Common values:
        - 'cm' (centimeters) - Maya default, most game engines
        - 'm' (meters) - architectural, some engines like Unreal
        - 'mm' (millimeters) - precision/mechanical work
        - 'in' (inches) - some US-based workflows
        - 'ft' (feet) - architectural (US)

    Known Limitations:
        - Only checks linear units (not angular or time units)
        - Does not auto-fix units (would require scaling all objects)
        - Hard-coded expected value requires code edit to change

    Academic Use:
        Most 3D courses specify required units in their style guide.
        Wrong units cause models to appear microscopic or gigantic
        when imported into game engines or rendering software.
        This is often caught too late during integration.
    """
    # Get current linear unit
    currentUnit = cmds.currentUnit(query=True, linear=True)

    # Check if it matches expected
    if currentUnit != EXPECTED_LINEAR_UNIT:
        # Return a special marker indicating scene-level issue
        # The UI can display this appropriately
        return "nodes", ['SCENE_UNITS_MISMATCH:{}_expected:{}'.format(
            currentUnit, EXPECTED_LINEAR_UNIT)]

    return "nodes", []


# UV distortion threshold - ratio of UV area to 3D area deviation
# A ratio significantly different from 1.0 indicates stretching/compression
# Default: 0.5 means UV area is 50% of expected, 2.0 means 200% (stretched)
UV_DISTORTION_THRESHOLD = 0.5  # Min ratio (below = compressed)
UV_DISTORTION_THRESHOLD_MAX = 2.0  # Max ratio (above = stretched)


def uvDistortion(_, SLMesh):
    """Detect polygons with stretched or compressed UV coordinates.

    This check identifies faces where the UV mapping is significantly
    distorted relative to the 3D geometry. UV distortion causes:
    - Blurry or stretched textures
    - Visible seams and artifacts
    - Inconsistent texture resolution across the model
    - Professional quality issues in renders

    Algorithm:
        1. For each polygon, calculate its 3D world-space area
        2. Calculate the corresponding UV-space area
        3. Compute the ratio: UV_area / (3D_area * normalization_factor)
        4. Flag faces where ratio is outside threshold bounds

    The normalization factor accounts for the fact that UV space (0-1)
    and world space (scene units) have different scales. We use the
    mesh's average ratio as the baseline for comparison.

    Args:
        _: Not used
        SLMesh: MSelectionList containing mesh shapes to check

    Returns:
        tuple: ("polygon", dict) where dict maps UUID -> list of
               polygon indices with UV distortion

    Configuration:
        UV_DISTORTION_THRESHOLD (default 0.5): Min ratio threshold
        UV_DISTORTION_THRESHOLD_MAX (default 2.0): Max ratio threshold
        Ratios outside this range are flagged as distorted.

    Known Limitations:
        - Requires UVs to exist (faces without UVs are skipped)
        - Uses simple area comparison, not angle-based distortion
        - May flag intentionally scaled UVs (e.g., tiled textures)
        - Threshold is uniform; doesn't account for artistic intent

    Academic Use:
        UV distortion is one of the most visible quality issues in
        3D models. Stretched textures immediately signal poor craftsmanship
        to evaluators and are a common point deduction in assignments.
    """
    import math

    distortedFaces = defaultdict(list)

    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        dagPath = selIt.getDagPath()
        mesh = om.MFnMesh(dagPath)
        fn = om.MFnDependencyNode(dagPath.node())
        uuid = fn.uuid().asString()

        # First pass: calculate average ratio for normalization
        ratios = []
        faceIt = om.MItMeshPolygon(dagPath)
        while not faceIt.isDone():
            if faceIt.hasUVs():
                # Get 3D area
                area3D = faceIt.getArea()

                # Get UV area - need to calculate from UV coordinates
                try:
                    uvs = faceIt.getUVs()
                    uvArea = _calculateUVPolygonArea(uvs[0], uvs[1])

                    if area3D > 0.0001 and uvArea > 0.0000001:
                        ratio = uvArea / area3D
                        ratios.append((faceIt.index(), ratio, area3D, uvArea))
                except:
                    pass  # Skip faces with UV errors

            faceIt.next()

        # Calculate median ratio for normalization
        if not ratios:
            selIt.next()
            continue

        sortedRatios = sorted([r[1] for r in ratios])
        medianRatio = sortedRatios[len(sortedRatios) // 2]

        if medianRatio < 0.0000001:
            selIt.next()
            continue

        # Second pass: flag faces that deviate significantly from median
        for faceIdx, ratio, area3D, uvArea in ratios:
            normalizedRatio = ratio / medianRatio

            if normalizedRatio < UV_DISTORTION_THRESHOLD or normalizedRatio > UV_DISTORTION_THRESHOLD_MAX:
                distortedFaces[uuid].append(faceIdx)

        selIt.next()

    return "polygon", distortedFaces


def _calculateUVPolygonArea(uCoords, vCoords):
    """Calculate the area of a polygon in UV space using the shoelace formula.

    Args:
        uCoords: List of U coordinates
        vCoords: List of V coordinates

    Returns:
        float: Area of the polygon in UV space
    """
    n = len(uCoords)
    if n < 3:
        return 0.0

    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += uCoords[i] * vCoords[j]
        area -= uCoords[j] * vCoords[i]

    return abs(area) / 2.0


# Texel density threshold - how much deviation from median is acceptable
# Default: 0.5 means faces with <50% or >200% of median texel density are flagged
TEXEL_DENSITY_THRESHOLD = 0.5  # Min ratio (below = too low density)
TEXEL_DENSITY_THRESHOLD_MAX = 2.0  # Max ratio (above = too high density)

# Assumed texture resolution for texel density calculation (pixels)
# This is used when no texture is connected - common default texture size
TEXEL_DENSITY_TEXTURE_SIZE = 1024


def texelDensity(_, SLMesh):
    """Detect faces with inconsistent texel density across the mesh.

    Texel density measures how many texture pixels cover each unit of 3D
    surface area. Consistent texel density ensures uniform texture quality
    across the entire model - no areas appear blurrier or sharper than others.

    This check identifies faces where texel density deviates significantly
    from the mesh's median, indicating:
    - Some parts will appear blurry (low density)
    - Some parts will appear overly sharp (high density)
    - Visible seams where density changes abruptly
    - Wasted texture resolution or insufficient detail

    Algorithm:
        1. For each polygon, calculate its 3D world-space area
        2. Calculate the corresponding UV-space area
        3. Convert UV area to pixel area: UV_area * texture_size^2
        4. Compute texel density: pixel_area / 3D_area (pixels per unit)
        5. Compare each face's density against the median density
        6. Flag faces where density ratio is outside threshold bounds

    Args:
        _: Not used
        SLMesh: MSelectionList containing mesh shapes to check

    Returns:
        tuple: ("polygon", dict) where dict maps UUID -> list of
               polygon indices with inconsistent texel density

    Configuration:
        TEXEL_DENSITY_THRESHOLD (default 0.5): Min ratio threshold
        TEXEL_DENSITY_THRESHOLD_MAX (default 2.0): Max ratio threshold
        TEXEL_DENSITY_TEXTURE_SIZE (default 1024): Assumed texture size

    Known Limitations:
        - Requires UVs to exist (faces without UVs are skipped)
        - Assumes uniform texture size; multi-resolution not supported
        - Uses assumed texture size, not actual connected textures
        - Very small faces may have unstable density calculations
        - Intentional density variation (detail areas) may be flagged

    Academic Use:
        Consistent texel density is a hallmark of professional UV work.
        Inconsistent density is immediately visible in renders and shows
        that proper UV planning was not done. This is frequently checked
        in portfolio reviews and assignment grading.
    """
    import math

    densityErrors = defaultdict(list)

    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        dagPath = selIt.getDagPath()
        mesh = om.MFnMesh(dagPath)
        fn = om.MFnDependencyNode(dagPath.node())
        uuid = fn.uuid().asString()

        # Calculate texel density for each face
        densities = []
        faceIt = om.MItMeshPolygon(dagPath)
        while not faceIt.isDone():
            if faceIt.hasUVs():
                # Get 3D area
                area3D = faceIt.getArea()

                # Get UV area
                try:
                    uvs = faceIt.getUVs()
                    uvArea = _calculateUVPolygonArea(uvs[0], uvs[1])

                    # Convert UV area to pixel area (UV 0-1 space to texture pixels)
                    pixelArea = uvArea * (TEXEL_DENSITY_TEXTURE_SIZE ** 2)

                    # Calculate texel density (pixels per world unit squared)
                    if area3D > 0.0001:
                        texelDensityValue = pixelArea / area3D
                        if texelDensityValue > 0:
                            densities.append((faceIt.index(), texelDensityValue))
                except:
                    pass  # Skip faces with UV errors

            faceIt.next()

        # Need enough samples to calculate meaningful median
        if len(densities) < 2:
            selIt.next()
            continue

        # Calculate median texel density for this mesh
        sortedDensities = sorted([d[1] for d in densities])
        medianDensity = sortedDensities[len(sortedDensities) // 2]

        if medianDensity < 0.0001:
            selIt.next()
            continue

        # Flag faces that deviate significantly from median
        for faceIdx, density in densities:
            ratio = density / medianDensity

            if ratio < TEXEL_DENSITY_THRESHOLD or ratio > TEXEL_DENSITY_THRESHOLD_MAX:
                densityErrors[uuid].append(faceIdx)

        selIt.next()

    return "polygon", densityErrors


def _isPowerOfTwo(n):
    """Check if a number is a power of 2.

    Args:
        n: Integer to check

    Returns:
        bool: True if n is a power of 2, False otherwise
    """
    if n <= 0:
        return False
    return (n & (n - 1)) == 0


def textureResolution(_, __):
    """Detect textures with non-power-of-2 resolutions.

    This check identifies file texture nodes where the image dimensions are
    not powers of 2 (e.g., 512, 1024, 2048, 4096). Non-power-of-2 textures
    cause problems because:
    - GPU memory is allocated in power-of-2 blocks, wasting space
    - Many game engines require or prefer power-of-2 textures
    - Mipmapping may not work correctly with non-power-of-2 textures
    - Performance can suffer with odd-sized textures

    Algorithm:
        1. Find all 'file' texture nodes in the scene
        2. For each file node, get the texture file path
        3. Query the image dimensions using Maya's getAttr on outSize
        4. Check if both width and height are powers of 2
        5. Flag nodes where either dimension is not a power of 2

    Args:
        _: Not used (scene-wide check)
        __: Not used (scene-wide check)

    Returns:
        tuple: ("nodes", list) where list contains UUIDs of file texture
               nodes with non-power-of-2 resolutions

    Known Limitations:
        - Only checks 'file' node type (not procedural textures)
        - Requires texture file to exist to read dimensions
        - Cannot check textures that fail to load
        - UDIM and animated textures may report unexpected sizes
        - Some modern engines support non-power-of-2 (NPOT) textures

    Academic Use:
        Power-of-2 texture sizes are a fundamental requirement in game
        development. Students learning real-time graphics need to
        understand this constraint. Using improper texture sizes is a
        common mistake that results in wasted memory and compatibility
        issues when exporting to game engines.
    """
    import os

    nonPowerOfTwoNodes = []

    # Get all file texture nodes in the scene
    fileNodes = cmds.ls(type='file') or []

    for fileNode in fileNodes:
        # Get the file path from the texture node
        texturePath = cmds.getAttr(fileNode + '.fileTextureName')

        # Skip if no path is set
        if not texturePath:
            continue

        # Skip if file doesn't exist (missingTextures check handles this)
        if not os.path.exists(texturePath):
            continue

        try:
            # Get the output size of the texture (width, height)
            # This queries the actual loaded image dimensions
            outSizeX = cmds.getAttr(fileNode + '.outSizeX')
            outSizeY = cmds.getAttr(fileNode + '.outSizeY')

            # Check if both dimensions are powers of 2
            if outSizeX and outSizeY:
                width = int(outSizeX)
                height = int(outSizeY)

                if not _isPowerOfTwo(width) or not _isPowerOfTwo(height):
                    # Get UUID for the file node
                    uuid = cmds.ls(fileNode, uuid=True)
                    if uuid:
                        nonPowerOfTwoNodes.append(uuid[0])
        except Exception:
            # Skip nodes that fail to query (corrupted, missing, etc.)
            pass

    return "nodes", nonPowerOfTwoNodes


# Default shading groups that should never be flagged as unused
DEFAULT_SHADING_GROUPS = {'initialShadingGroup', 'initialParticleSE'}
# Default materials that should never be flagged as unused
DEFAULT_MATERIALS = {'lambert1', 'particleCloud1', 'standardSurface1'}


def unusedNodes(_, __):
    """Detect unused materials and shading nodes that clutter the scene.

    This check identifies materials and shading groups that are not assigned
    to any geometry. Unused nodes indicate:
    - Leftover materials from deleted objects
    - Imported materials that were never used
    - Duplicate materials from copy-paste operations
    - Unprofessional scene organization
    - Unnecessary file size increase

    Algorithm:
        1. Get all shading engines (shadingEngine nodes) in the scene
        2. For each shading engine, check if it has any geometry assigned
        3. Identify shading engines with no assignments (excluding defaults)
        4. Also check for orphaned materials not connected to any shading engine
        5. Return list of unused node UUIDs

    Args:
        _: Not used (scene-level check)
        __: Not used (scene-level check)

    Returns:
        tuple: ("nodes", list) where list contains UUIDs of unused
               shading engines and materials

    Known Limitations:
        - Does not detect unused textures (use with missingTextures)
        - Does not detect unused utility nodes (samplerInfo, etc.)
        - Some unused materials may be kept for reference
        - Materials in referenced files may appear unused
        - Does not flag default Maya materials (lambert1, etc.)

    Academic Use:
        A clean scene with only the necessary nodes demonstrates
        professional workflow practices. Instructors often check for
        scene organization as part of grading. Unused materials
        suggest sloppy work habits and are a common issue in
        student submissions.
    """
    unusedNodesList = []

    # Get all shading engines in the scene
    shadingEngines = cmds.ls(type='shadingEngine') or []

    for shadingEngine in shadingEngines:
        # Skip default shading groups
        if shadingEngine in DEFAULT_SHADING_GROUPS:
            continue

        # Check if this shading engine has any geometry assigned
        # The 'dagSetMembers' attribute lists connected geometry
        try:
            members = cmds.sets(shadingEngine, query=True) or []
            if len(members) == 0:
                # No geometry assigned - this is unused
                uuid = cmds.ls(shadingEngine, uuid=True)
                if uuid:
                    unusedNodesList.append(uuid[0])
        except Exception:
            pass  # Skip problematic shading engines

    # Also check for orphaned materials (materials not connected to any shading engine)
    # This catches materials that were disconnected but not deleted
    materialTypes = ['lambert', 'blinn', 'phong', 'phongE', 'standardSurface',
                     'aiStandardSurface', 'surfaceShader', 'useBackground']

    for matType in materialTypes:
        materials = cmds.ls(type=matType) or []
        for material in materials:
            # Skip default materials
            if material in DEFAULT_MATERIALS:
                continue

            # Check if material is connected to any shading engine
            try:
                connections = cmds.listConnections(material + '.outColor',
                                                    type='shadingEngine') or []
                if len(connections) == 0:
                    # Material not connected to any shading engine
                    uuid = cmds.ls(material, uuid=True)
                    if uuid:
                        unusedNodesList.append(uuid[0])
            except Exception:
                pass  # Skip problematic materials

    return "nodes", unusedNodesList


def hiddenObjects(transformNodes, _):
    """Detect hidden objects that may be forgotten in the scene.

    This check identifies transform nodes that are hidden (visibility=False)
    or have display layer visibility turned off. Hidden objects can cause:
    - Unexpected geometry appearing in renders
    - File size bloat from forgotten objects
    - Confusion when collaborating with others
    - Missing geometry in game engine exports
    - Unprofessional scene organization

    Algorithm:
        1. For each transform node, check the 'visibility' attribute
        2. Also check if the object is in a hidden display layer
        3. Flag objects that are hidden by either method
        4. Only check mesh shapes (not cameras, lights, etc.)

    Args:
        transformNodes: List of transform node UUIDs to check
        _: MSelectionList (not used for this check)

    Returns:
        tuple: ("nodes", list) where list contains UUIDs of hidden
               transform nodes

    Known Limitations:
        - Does not detect objects hidden via render layers
        - Does not detect objects with visibility animated to 0
        - May flag intentionally hidden reference geometry
        - Does not check lodVisibility or template status
        - Parent node visibility affects children (only direct visibility checked)

    Academic Use:
        Hidden objects are a common cause of issues when students submit
        work. Objects hidden during work sessions can accidentally remain
        in the file, causing unexpected renders or export issues. A clean
        scene should only contain visible, necessary geometry.
    """
    hiddenNodes = []

    for node in transformNodes:
        nodeName = _getNodeName(node)

        # Check if this transform has a mesh shape child
        shapes = cmds.listRelatives(nodeName, shapes=True, fullPath=True) or []
        hasMesh = any(cmds.nodeType(s) == 'mesh' for s in shapes)

        if not hasMesh:
            continue  # Skip non-mesh transforms (cameras, lights, etc.)

        try:
            # Check direct visibility attribute
            visibility = cmds.getAttr(nodeName + '.visibility')
            if not visibility:
                hiddenNodes.append(node)
                continue

            # Check if object is in a hidden display layer
            drawOverride = cmds.listConnections(nodeName + '.drawOverride',
                                                 type='displayLayer') or []
            for layer in drawOverride:
                if layer != 'defaultLayer':  # Ignore default layer
                    layerVisible = cmds.getAttr(layer + '.visibility')
                    if not layerVisible:
                        hiddenNodes.append(node)
                        break

        except Exception:
            pass  # Skip nodes that fail to query

    return "nodes", hiddenNodes


# =============================================================================
# Naming Convention Patterns (Configurable)
# =============================================================================
# Standard Maya naming convention prefixes for different object types.
# These follow common industry standards used in studios and schools.
NAMING_CONVENTION_PATTERNS = {
    'mesh': ['geo_', 'mesh_', 'msh_', 'GEO_', 'MESH_'],
    'group': ['grp_', 'group_', 'GRP_', 'GROUP_'],
    'joint': ['jnt_', 'joint_', 'JNT_', 'JOINT_', 'bn_', 'bone_'],
    'locator': ['loc_', 'locator_', 'LOC_', 'LOCATOR_'],
    'curve': ['crv_', 'curve_', 'CRV_', 'CURVE_'],
    'control': ['ctrl_', 'control_', 'CTRL_', 'CONTROL_', 'con_'],
    'camera': ['cam_', 'camera_', 'CAM_', 'CAMERA_'],
    'light': ['lgt_', 'light_', 'LGT_', 'LIGHT_'],
}

# Default names created by Maya that should be flagged
MAYA_DEFAULT_NAMES = {
    'pCube', 'pSphere', 'pCylinder', 'pCone', 'pTorus', 'pPlane',
    'pPyramid', 'pPipe', 'pHelix', 'pPrism', 'pDisc',
    'nurbsSphere', 'nurbsCube', 'nurbsCylinder', 'nurbsCone', 'nurbsPlane',
    'nurbsTorus', 'nurbsCircle', 'nurbsSquare',
    'polySurface', 'transform', 'group', 'null', 'locator',
    'curve', 'bezierCurve',
}


def namingConvention(transformNodes, _):
    """Validate that objects follow proper naming conventions.

    This check identifies objects that use Maya's default names (like pCube1,
    pSphere2) or don't follow standard naming conventions with type prefixes.
    Proper naming is essential for:
    - Professional scene organization
    - Easy asset identification
    - Team collaboration
    - Script and pipeline compatibility

    Algorithm:
        1. For each transform node, get its short name (without path)
        2. Check if the name matches any of Maya's default names
        3. Determine the object type (mesh, group, joint, etc.)
        4. Check if the name has an appropriate prefix for its type
        5. Flag objects that fail either check

    Args:
        transformNodes: List of transform node UUIDs to check
        _: MSelectionList (not used for this check)

    Returns:
        tuple: ("nodes", list) where list contains UUIDs of nodes
               that don't follow naming conventions

    Known Limitations:
        - Only checks for prefix-based naming (geo_, grp_, etc.)
        - Does not enforce specific naming styles (camelCase, snake_case)
        - Cannot detect semantic naming issues (e.g., "geo_blah" passes)
        - Custom studio conventions may differ from built-in patterns
        - Does not check material or shader node names

    Academic Use:
        Students often submit work with default names like "pCube1" and
        "pSphere2", which indicates lack of attention to professional
        standards. Properly named objects demonstrate understanding of
        industry practices and make grading/review much easier.
    """
    invalidNodes = []

    for node in transformNodes:
        nodeName = _getNodeName(node)
        if not nodeName:
            continue

        # Get the short name (without the DAG path)
        shortName = nodeName.rsplit('|', 1)[-1]

        # Remove any trailing numbers for base name check
        baseName = shortName.rstrip('0123456789')

        # Check 1: Is this a Maya default name?
        if baseName in MAYA_DEFAULT_NAMES:
            invalidNodes.append(node)
            continue

        # Check 2: Determine object type and verify prefix
        shapes = cmds.listRelatives(nodeName, shapes=True, fullPath=True) or []

        objectType = None
        if shapes:
            # Has shapes - check what type
            shapeType = cmds.nodeType(shapes[0])
            if shapeType == 'mesh':
                objectType = 'mesh'
            elif shapeType in ('nurbsCurve', 'bezierCurve'):
                objectType = 'curve'
            elif shapeType == 'locator':
                objectType = 'locator'
            elif shapeType == 'camera':
                objectType = 'camera'
            elif shapeType in ('pointLight', 'spotLight', 'directionalLight',
                               'areaLight', 'ambientLight', 'volumeLight'):
                objectType = 'light'
            elif shapeType == 'joint':
                objectType = 'joint'
        else:
            # No shapes - it's a group (empty transform)
            children = cmds.listRelatives(nodeName, children=True) or []
            if children:
                objectType = 'group'
            # Empty groups without children are handled elsewhere

        # Check if the node is a joint (joints are transforms, not shapes)
        if cmds.nodeType(nodeName) == 'joint':
            objectType = 'joint'

        # Skip objects without a defined type (empty groups, unknown types)
        if objectType is None:
            continue

        # Check if name has valid prefix for its type
        validPrefixes = NAMING_CONVENTION_PATTERNS.get(objectType, [])
        hasValidPrefix = any(shortName.startswith(prefix) for prefix in validPrefixes)

        if not hasValidPrefix:
            invalidNodes.append(node)

    return "nodes", invalidNodes


# =============================================================================
# Hierarchy Depth Configuration
# =============================================================================
# Maximum allowed hierarchy depth before flagging.
# A depth of 1 means the object is at the root level.
# Depth of 5 means: root > level1 > level2 > level3 > level4 > object
HIERARCHY_DEPTH_MAX = 5


def hierarchyDepth(transformNodes, _):
    """Detect objects that are nested too deeply in the scene hierarchy.

    This check identifies transform nodes that are nested beyond a configurable
    maximum depth. Excessive hierarchy depth indicates poor scene organization
    and can cause:
    - Difficulty navigating the Outliner
    - Confusion when working on teams
    - Performance issues with very deep hierarchies
    - Complications when exporting to game engines
    - Unprofessional scene structure

    Algorithm:
        1. For each transform node, get its full DAG path
        2. Count the number of '|' separators to determine depth
        3. Compare against HIERARCHY_DEPTH_MAX threshold
        4. Flag objects that exceed the maximum allowed depth

    Args:
        transformNodes: List of transform node UUIDs to check
        _: MSelectionList (not used for this check)

    Returns:
        tuple: ("nodes", list) where list contains UUIDs of nodes
               that are nested too deeply

    Known Limitations:
        - Does not consider whether deep nesting is intentional (rigs, etc.)
        - Referenced objects may have additional depth from their source file
        - Depth threshold is global, not context-aware
        - Does not distinguish between group hierarchies and constraint targets

    Academic Use:
        Students often create deeply nested hierarchies accidentally by
        repeatedly grouping objects or importing nested assets. Clean,
        shallow hierarchies demonstrate good organizational skills and
        make scenes easier to review and grade.
    """
    tooDeepNodes = []

    for node in transformNodes:
        nodeName = _getNodeName(node)
        if not nodeName:
            continue

        # Get the full DAG path
        try:
            fullPath = cmds.ls(nodeName, long=True)
            if not fullPath:
                continue
            fullPath = fullPath[0]
        except Exception:
            continue

        # Count depth by counting '|' separators
        # A path like "|grp1|grp2|geo" has depth 3
        depth = fullPath.count('|')

        # Check against threshold
        if depth > HIERARCHY_DEPTH_MAX:
            tooDeepNodes.append(node)

    return "nodes", tooDeepNodes


def concaveFaces(_, SLMesh):
    """Detect concave (non-convex) polygon faces.

    This check identifies polygon faces that are not convex. A convex polygon
    is one where all interior angles are less than 180 degrees, and any line
    segment between two points inside the polygon stays entirely inside.
    Concave faces can cause:
    - Unpredictable triangulation during rendering
    - Rendering artifacts and shading errors
    - Boolean operation failures
    - Issues with subdivision surfaces
    - Problems when exporting to game engines

    Algorithm:
        1. Iterate through each polygon face in the mesh
        2. Use Maya's built-in isConvex() method on MItMeshPolygon
        3. Flag faces that return False (non-convex)
        4. Triangles are always convex, so they pass automatically

    Args:
        _: List of node UUIDs (not used for this check)
        SLMesh: MSelectionList containing mesh shapes to check

    Returns:
        tuple: ("polygon", dict) where dict maps UUID -> list of
               face indices that are concave

    Known Limitations:
        - Does not distinguish between slightly and severely concave faces
        - Very small concave angles may not be detected due to floating point
        - Triangles are always convex by definition (never flagged)
        - Does not provide severity metric or angle measurement

    Academic Use:
        Concave faces often result from careless modeling or complex boolean
        operations. Students should understand that clean quad topology with
        convex faces produces more predictable results in rendering and
        game engines.
    """
    concave = defaultdict(list)

    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()

        while not faceIt.isDone():
            # Triangles are always convex, skip them for efficiency
            if faceIt.polygonVertexCount() > 3:
                # isConvex() returns True for convex faces
                if not faceIt.isConvex():
                    concave[uuid].append(faceIt.index())
            faceIt.next()

        selIt.next()

    return "polygon", concave


def intermediateObjects(transformNodes, _):
    """Detect intermediate (construction history) objects in the scene.

    This check identifies transform nodes that have intermediate shape nodes.
    Intermediate objects are created during modeling operations (like deformers,
    blendshapes, or duplicating skinned meshes) and should typically be deleted
    when cleaning up a scene. They cause:
    - Increased file size
    - Slower scene loading
    - Confusion in the Outliner
    - Potential issues with exports
    - Signs of incomplete scene cleanup

    Algorithm:
        1. For each transform node, get its shape children
        2. Check if any shape has the 'intermediateObject' attribute set to True
        3. Flag transforms that have intermediate shape nodes
        4. Skip checking the intermediate shapes themselves

    Args:
        transformNodes: List of transform node UUIDs to check
        _: MSelectionList (not used for this check)

    Returns:
        tuple: ("nodes", list) where list contains UUIDs of transform
               nodes that have intermediate shape children

    Known Limitations:
        - Some intermediate objects are intentional (blendshape targets, etc.)
        - Referenced intermediate objects may be required by the source file
        - Deformer setups may legitimately need intermediate objects
        - Does not distinguish between needed and unneeded intermediates

    Academic Use:
        Students often forget to delete construction history properly,
        leaving intermediate objects in their scenes. This check helps
        identify these leftover objects that bloat file size and indicate
        incomplete scene cleanup - a common issue in student submissions.
    """
    nodesWithIntermediates = []

    for node in transformNodes:
        nodeName = _getNodeName(node)
        if not nodeName:
            continue

        try:
            # Get all shape children of this transform
            shapes = cmds.listRelatives(nodeName, shapes=True, fullPath=True) or []

            for shape in shapes:
                # Check if this shape is marked as intermediate
                if cmds.attributeQuery('intermediateObject', node=shape, exists=True):
                    isIntermediate = cmds.getAttr(shape + '.intermediateObject')
                    if isIntermediate:
                        nodesWithIntermediates.append(node)
                        break  # Only need to flag once per transform

        except Exception:
            pass  # Skip nodes that fail to query

    return "nodes", nodesWithIntermediates
