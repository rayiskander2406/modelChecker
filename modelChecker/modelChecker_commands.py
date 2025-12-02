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
