import maya.cmds as cmds
from pxr import Usd, UsdGeom
import mayaUsd.lib as mayaUsdLib

def get_stage_from_proxy_shape(proxy_shape):
    proxy_prim = mayaUsdLib.GetPrim(proxy_shape)
    
    if not proxy_prim.IsValid():
        raise ValueError(f"Invalid USD prim retrieved from proxy shape: {proxy_shape}")
    
    stage = proxy_prim.GetStage()
    
    if not stage:
        raise ValueError(f"Failed to retrieve USD stage from proxy shape: {proxy_shape}")
    
    return stage
def get_stage_and_prim(usd_node):
    proxy_path, prim_relative_path = usd_node.split(',')
    return proxy_path, prim_relative_path

def is_prim_a_mesh_from_proxy(stage, prim_relative_path):
    prim_path = f"/{prim_relative_path}"
    return is_prim_a_mesh(stage, prim_path)

def is_prim_a_mesh(usd_stage, prim_path):
    prim = usd_stage.GetPrimAtPath(prim_path)
    return prim.IsValid() and UsdGeom.Mesh(prim)