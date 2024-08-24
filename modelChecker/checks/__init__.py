from .ngon_check import NgonCheck
from .triangle_check import TriangleCheck
from .trailing_number_check import TrailingNumberCheck
from .uv_range_check import UVRangeCheck
from .poles_check import PolesCheck
from .self_penetrating_uvs import SelfPenetratingUVsCheck
from .default_shader_check import DefaultShaderCheck
from .uncentered_pivots import UncenteredPivots
from .namespaces_check import NamespacesCheck
from .duplicated_name_check import DuplicatedNamesCheck
from .shape_names_check import ShapeNamesCheck
from .hard_edges_check import HardEdgesCheck
from .lamina_check import LaminaCheck
from .zero_area_faces_check import ZeroAreaFacesCheck
from .zero_length_edges_check import ZeroLengthEdgesCheck
from .none_manifold_eges_check import NoneManifoldEdgesCheck
from .parent_geometry_check import ParentGeometryCheck

all_checks = [
    NgonCheck,
    TrailingNumberCheck,
    TriangleCheck,
    UVRangeCheck,
    PolesCheck,
    NamespacesCheck,
    ShapeNamesCheck,
    HardEdgesCheck,
    LaminaCheck,
    SelfPenetratingUVsCheck,
    DefaultShaderCheck,
    UncenteredPivots,
    ZeroAreaFacesCheck,
    ZeroLengthEdgesCheck,
    NoneManifoldEdgesCheck,
    ParentGeometryCheck,
    DuplicatedNamesCheck
]