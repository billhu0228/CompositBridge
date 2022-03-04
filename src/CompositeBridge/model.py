import os
from typing import Tuple, List, Dict

from PyAngle import Angle
from ezdxf.math import Vec3

from .section import Section, Material


class Node:
    __slots__ = ('n', 'x', 'y', 'z', '_location')

    def __init__(self, n: int, x, y, z):
        self._location = Vec3(x, y, z)
        self.n = n
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "Node: (%i,%.1f,%.1f,%.1f)" % (self.n, self.x, self.y, self.z)

    def distance(self, other: 'Node'):
        return self._location.distance(other._location)


class Element:
    __slots__ = ('e', 'nlist', 'mat', 'etype', 'real', 'secn', '_npts')

    nlist: Tuple["Node"]

    def __init__(self, e: int, mat: int, etype: int, real: int, secn: int, *args: Node):
        self.e = e
        self.mat = mat
        self.etype = etype
        self.real = real
        self.secn = secn
        self._npts = len(args)
        if self.etype == 188:
            if len(args) != 3:
                raise Exception("BEAM188应使用3个Node.")
            else:
                self.nlist = args
        else:
            raise Exception("单元类型不支持.")

    def __str__(self):
        ss = "Elem: (%i,type=%i,secn=%i,nlist=[" % (self.e, self.etype, self.secn,)
        for n in self.nlist:
            ss += "%i," % n.n
        ss += "])"
        return ss


class CrossArrangement:
    """
    正交横截面
    """
    __slots__ = ("width", 'girder_arr', 'subgirder_arr', 'slab_thickness', 'slab_gap')
    width: float
    girder_arr: List[float]
    subgirder_arr: List[float]
    slab_thickness: float
    slab_gap: float

    def __init__(self, width, girder_arr, subgirder_arr, slab_thickness, slab_gap):
        self.width = width
        self.girder_arr = girder_arr
        self.subgirder_arr = subgirder_arr
        self.slab_thickness = slab_thickness
        self.slab_gap = slab_gap
        if sum(self.girder_arr) != self.width or sum(self.subgirder_arr) != self.width:
            raise Exception("梁间距配置有误.")


class Span:
    def __init__(self, station: float, angle: 'Angle' = Angle.from_degrees(90.0)):
        self.station = station
        self.angle = angle


class CompositeBridge:
    __slots__ = ('_node_list', '_elem_list', '_sect_list', '_mat_list', '_spans', 'cross_section', '_is_fem', '_apdl')
    _node_list: Dict[int, 'Node']
    _elem_list: Dict[int, 'Element']
    _sect_list: Dict[int, 'Section']
    _mat_list: Dict[int, 'Material']
    _spans: List['Span']
    cross_section: 'CrossArrangement'
    _is_fem: bool
    _apdl: str

    def __init__(self, spans: List['Span'], cross: 'CrossArrangement'):
        self._spans = spans
        self.cross_section = cross
        self._initialize()
        pass

    def add_material(self, mat: 'Material'):
        """
        添加材料
        :param mat:
        :return:
        """
        if self._mat_list.keys().__contains__(mat.id):
            raise Exception("材料编号 %i 重复" % mat.id)
        self._mat_list[mat.id] = mat

    def _initialize(self):
        """
        初始化模型。
        :return:
        """
        self._node_list = {}
        self._elem_list = {}
        self._sect_list = {}
        self._mat_list = {}
        self._is_fem = False
        self._apdl = ""
        pass

    def generate_fem(self):
        """
        生成有限元数据
        :return:
        """
        self._is_fem = True
        pass

    def write_database(self, projectname, path):
        if self._is_fem:
            self._apdl = ""
            self._apdl_begin(os.path.join(path, 'main.inp'), projectname)
            self._apdl_material(os.path.join(path, 'Material.inp'), projectname)

            pass
        else:

            print("到处前请先生成fem模型.")
            return

    @staticmethod
    def _apdl_begin(filestream, proj_name="Project A"):
        cmd = '''
!=======================================================
! Modeled by Bill with Python Automation 2022-03
!=======================================================
finish
/CLEAR,START
/FILNAME,main,0
/TITLE,%s
/input,Material,inp
/input,Section,inp
/input,Model,inp
/input,Debug,inp
!-------------------------------------------------------''' % proj_name
        with open(filestream, 'w+') as fid:
            fid.write(cmd)

    def _apdl_material(self, filestream, proj_name="Project A"):
        cmd = "/prep7"
        for k in self._mat_list.keys():
            val = self._mat_list[k]
            cmd += val.apdl_str
        with open(filestream, 'w+') as fid:
            fid.write(cmd)


if __name__ == "__main__":
    n1 = Node(1, 0, 0, 0)
    n2 = Node(2, 100, 100, 100)
    ele = Element(1, 1, 188, 1, 1, n1, n2, n1)
    print(ele)
