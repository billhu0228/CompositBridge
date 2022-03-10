import os
from typing import Tuple, List, Dict

import numpy as np
from PyAngle import Angle
from ezdxf.math import Vec3

from .section import Section, Material, ApdlWriteable


class Node(ApdlWriteable):
    __slots__ = ('n', 'x', 'y', 'z', '_location')

    def __init__(self, n: int, x, y, z):
        self._location = Vec3(x, y, z)
        self.n = n
        self.x = x
        self.y = y
        self.z = z

    @property
    def apdl_str(self):
        cmd_str = "n,%i,%.3f,%.3f,%.3f" % (self.n, self.x, self.z, self.y)
        return cmd_str

    def __str__(self):
        return "Node: (%i,%.1f,%.1f,%.1f)" % (self.n, self.x, self.y, self.z)

    def distance(self, other: 'Node'):
        return self._location.distance(other._location)


class Element:
    __slots__ = ('e', 'nlist', 'mat', 'etype', 'real', 'secn', '_npts')

    nlist: Tuple["Node"]

    def __init__(self, e: int, mat: int, etype: int, real: int, secn: int, nodes: Tuple):
        self.e = e
        self.mat = mat
        self.etype = etype
        self.real = real
        self.secn = secn
        self._npts = len(nodes)
        if self.etype == 188:
            if len(nodes) != 3:
                raise Exception("BEAM188应使用3个Node.")
            else:
                self.nlist = nodes
        elif etype == 181:
            if len(nodes) != 4:
                raise Exception("SHELL181应使用4个Node.")
            else:
                self.nlist = nodes
        else:
            raise Exception("单元类型不支持.")

    @property
    def apdl_str(self):
        cmd_str = '''mat,%i
type,%i
real,%i
secn,%i
e,''' % (self.mat, self.etype, self.real, self.secn)
        for nn in self.nlist:
            cmd_str += str(nn.n)
            cmd_str += ','
        return cmd_str

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
    __slots__ = ('_node_list', '_elem_list', '_sect_list', '_mat_list', '_spans', 'cross_section', '_is_fem', '_apdl',
                 'cross_beam_dist', '_xlist', '_ylist', '_main_xlist', '_main_ylist')
    _node_list: Dict[int, 'Node']
    _elem_list: Dict[int, 'Element']
    _sect_list: Dict[int, 'Section']
    _mat_list: Dict[int, 'Material']
    _spans: List['Span']
    cross_section: 'CrossArrangement'
    _is_fem: bool
    _apdl: str
    _main_xlist: List[float]  # 主x坐标位置
    _main_ylist: List[float]  # 主y坐标位置
    _xlist: List[float]  # 全x坐标位置
    _ylist: List[float]  # 全y坐标位置

    def __init__(self, spans: List['Span'], cross_arr: 'CrossArrangement', cross_beam_dist: float = 5.0, **kwargs):
        self._spans = spans
        self.cross_section = cross_arr
        self._initialize()
        self.cross_beam_dist = cross_beam_dist
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

    def add_section(self, secn: 'Section'):
        """
        添加截面
        :param secn:
        :return:
        """
        if self._sect_list.keys().__contains__(secn.id):
            raise Exception("截面编号 %i 重复" % secn.id)
        self._sect_list[secn.id] = secn

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
        self._xlist = []
        self._ylist = []
        self._main_xlist = []
        self._main_ylist = []
        pass

    def generate_fem(self, e_size_x: float, e_size_y):
        """
        生成有限元数据
        :return:
        """
        self._create_coord(e_size_x, e_size_y)
        self._create_plate()
        self._create_girder()
        self._create_cross_beam()
        self._create_boundary()
        self._is_fem = True
        pass

    def write_database(self, projectname, path):
        if self._is_fem:
            self._apdl = ""
            self._apdl_begin(os.path.join(path, 'main.inp'), projectname)
            self._apdl_etype(os.path.join(path, 'Etype.inp'))
            self._apdl_list_out(os.path.join(path, 'Material.inp'), self._mat_list)
            self._apdl_list_out(os.path.join(path, 'Section.inp'), self._sect_list)
            self._apdl_node(os.path.join(path, 'Node.inp'))
            self._apdl_elem(os.path.join(path, 'Element.inp'))

            pass
        else:

            print("导出前，请生成fem模型.")
            return

    @staticmethod
    def more_value(start: float, end: float, apx_dist: float):
        npts = int(np.round((end - start) / apx_dist, 0))
        return np.linspace(start, end, npts + 1).tolist()

    @staticmethod
    def _apdl_begin(filestream, proj_name="Project A"):
        cmd = '''!=======================================================
! Modeled by Bill with Python Automation 2022-03
!=======================================================
finish
/CLEAR,START
/FILNAME,main,0
/TITLE,%s
/input,Etype,inp
/input,Material,inp
/input,Section,inp
/input,Node,inp
/input,Element,inp
!/input,Debug,inp
!-------------------------------------------------------''' % proj_name
        with open(filestream, 'w+') as fid:
            fid.write(cmd)

    @staticmethod
    def _apdl_list_out(filestream, prep_dict):
        cmd = "/prep7\n"
        for k in prep_dict.keys():
            val = prep_dict[k]
            cmd += val.apdl_str
        with open(filestream, 'w+', encoding='utf-8') as fid:
            fid.write(cmd)

    @staticmethod
    def _apdl_etype(filestream):
        cmd = "/prep7"
        cmd += '''! 单元        
et,181,SHELL181
et,188,BEAM188
et,184,MPC184'''
        with open(filestream, 'w+', encoding='utf-8') as fid:
            fid.write(cmd)

    def _apdl_material(self, filestream):
        cmd = "/prep7"
        for k in self._mat_list.keys():
            val = self._mat_list[k]
            cmd += val.apdl_str
        cmd += '''
! 单元        
et,181,SHELL181
et,188,BEAM188
et,184,MPC184'''
        with open(filestream, 'w+', encoding='utf-8') as fid:
            fid.write(cmd)

        def _apdl_section(self, filestream):
            cmd = "/prep7"
            for k in self._mat_list.keys():
                val = self._mat_list[k]
                cmd += val.apdl_str
            cmd += '''
    ! 单元        
    et,181,SHELL181
    et,188,BEAM188
    et,184,MPC184'''
            with open(filestream, 'w+', encoding='utf-8') as fid:
                fid.write(cmd)

    def _apdl_node(self, filestream):
        cmd = "/prep7\n"
        for n in self._node_list.keys():
            cmd += self._node_list[n].apdl_str
            cmd += "\n"
        with open(filestream, 'w+') as fid:
            fid.write(cmd)

    def _apdl_elem(self, filestream):
        cmd = "/prep7\n"
        for e in self._elem_list.keys():
            cmd += self._elem_list[e].apdl_str
            cmd += "\n"
        with open(filestream, 'w+') as fid:
            fid.write(cmd)

    def _create_coord(self, e_size_x: float, e_size_y: float):
        """
        生成控制坐标
        """
        tmp = []
        for i in range(len(self._spans) - 1):
            tmp += self.more_value(self._spans[i].station, self._spans[i + 1].station, apx_dist=self.cross_beam_dist)
        self._main_xlist = np.unique(tmp).tolist()
        tmp = []
        for i in range(len(self._main_xlist) - 1):
            tmp += self.more_value(self._main_xlist[i], self._main_xlist[i + 1], apx_dist=e_size_x)
        self._xlist = np.unique(tmp).tolist()
        tmp = [0]
        for dist in self.cross_section.girder_arr:
            tmp.append(tmp[-1] + dist)
        tmp2 = [0]
        for dist in self.cross_section.subgirder_arr:
            tmp2.append(tmp2[-1] + dist)
        tmp += tmp2
        tmp.sort()
        self._main_ylist = np.unique(tmp).tolist()
        tmp = []
        for i in range(len(self._main_ylist) - 1):
            tmp += self.more_value(self._main_ylist[i], self._main_ylist[i + 1], apx_dist=e_size_y)
        self._ylist = np.unique(tmp).tolist()

    def _create_plate(self):
        n = 1
        for y in self._ylist:
            for x in self._xlist:
                self._node_list[n] = Node(n, x, y, 0)
                n += 1
        e = 1
        kk = int((n - 1) / len(self._ylist))
        for ny in range(len(self._ylist) - 1):
            for nx in range(len(self._xlist) - 1):
                A = ny * kk + nx + 1
                B = A + 1
                C = B + kk
                D = C - 1
                ns = (
                    self._node_list[A],
                    self._node_list[B],
                    self._node_list[C],
                    self._node_list[D],
                )
                self._elem_list[e] = Element(e, 1, 181, 1, 1, ns)
                e += 1
        pass

    def _create_girder(self):
        pass

    def _create_boundary(self):
        pass

    def _create_cross_beam(self):
        pass


if __name__ == "__main__":
    n1 = Node(1, 0, 0, 0)
    n2 = Node(2, 100, 100, 100)
    ele = Element(1, 1, 188, 1, 1, n1, n2, n1)
    print(ele)
