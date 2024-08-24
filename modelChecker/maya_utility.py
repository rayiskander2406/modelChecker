""" Helpful utility functions for maya"""
from maya import cmds
import mayaUsd.lib as mayaUsdLib

def get_name_from_uuid(uuid):
    node_name = cmds.ls(uuid, long=True)
    if node_name:
        return node_name[0]
    return None

def get_uuid_from_name(node):
    node_uuid = cmds.ls(node, uuid=True)
    if node_uuid:
        return node_uuid[0]
    return None

def get_uuid_from_shape(shape_node):
    transform_node = cmds.listRelatives(shape_node, parent=True)[0]
    transform_uuid = cmds.ls(transform_node, uuid=True)[0]
    return transform_uuid


def _get_all_prims_from_proxy(proxy_shape_name):
    stage = mayaUsdLib.GetPrim(proxy_shape_name).GetStage()
    all_prim_paths = []
    for prim in stage.Traverse():
        full_path = f"{proxy_shape_name},{prim.GetPath().pathString}"
        all_prim_paths.append(full_path)
    return all_prim_paths

def get_all_nodes():
    all_nodes = []    
    for node in cmds.ls(transforms=True, long=True):
        if node not in {'|front', '|persp', '|top', '|side'}:
            children = cmds.listRelatives(node, shapes=True, fullPath=True) or []
            for child in children:
                if cmds.nodeType(child) == 'mayaUsdProxyShape':
                    all_prim_paths = _get_all_prims_from_proxy(child)
                    all_nodes.extend(all_prim_paths)
                else:
                    all_nodes.append(get_uuid_from_name(node))
    return all_nodes


def select_hierachy(nodes):
    hierachy = set()
    for node in nodes:
        node_name = cmds.ls(node, uuid=True, long=True)[0]
        children = cmds.listRelatives(node_name, typ="transform", allDescendents=True, fullPath=True)
        if children:
            uuids = [cmds.ls(child, uuid=True)[0] for child in children]
            hierachy.update(uuids)                
        hierachy.add(node)
    return list(hierachy)