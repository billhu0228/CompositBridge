import os
import pickle
import subprocess
from typing import List, Dict

import numpy as np

from .cross_arrangement import CrossArrangement
from .element import Element
from .node import Node
from .section import Section, Material


class CompositeBridge:
    __slots__ = ('length', 'cal_span', 'live_load',
                 '_node_list', '_elem_list', '_sect_list', '_mat_list', '_spans', 'cross_section', '_is_fem', '_apdl',
                 'cross_beam_dist', '_xlist', '_ylist', '_main_xlist', '_main_ylist', '_sub_ylist', 'lane_matrix')
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
    _sub_ylist: List[float]  # 次y坐标位置
    _xlist: List[float]  # 全x坐标位置
    _ylist: List[float]  # 全y坐标位置
    lane_matrix: List
    length: float

    def __init__(self, spans: List['Span'], cross_arr: 'CrossArrangement', cross_beam_dist: float = 5.0):
        self._spans = spans
        self.cross_section = cross_arr
        self._initialize()
        self.cross_beam_dist = cross_beam_dist
        self.length = spans[-1].station - spans[0].station
        self.cal_span = self._get_cal_span()
        self.live_load = None
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
        self._sect_list: {int: Section} = {}
        self._mat_list = {}
        self._is_fem = False
        self._apdl = ""
        self._xlist = []
        self._ylist = []
        self._main_xlist = []
        self._main_ylist = []
        self._sub_ylist = []
        self.lane_matrix = []
        pass

    def generate_fem(self, e_size_x: float, e_size_y: float, plate_elem: int):
        """
        生成有限元数据
        :return:
        """
        self._create_coord(e_size_x, e_size_y)
        self._create_plate(elem=plate_elem)
        self._create_girder()
        self._create_cross_beam()
        self._is_fem = True
        pass

    def write_database(self, projectname, path):
        if not os.path.exists(path):
            os.mkdir(path)
        if self._is_fem:
            self._apdl = ""
            self._apdl_begin(os.path.join(path, 'main.inp'), projectname)
            self._apdl_etype(os.path.join(path, 'Etype.inp'))
            self._apdl_list_out(os.path.join(path, 'Material.inp'), self._mat_list)
            self._apdl_list_out(os.path.join(path, 'Section.inp'), self._sect_list)
            self._apdl_node(os.path.join(path, 'Node.inp'))
            self._apdl_elem(os.path.join(path, 'Element.inp'))
            self._apdl_boundary(os.path.join(path, 'Boundary.inp'))
            self._apdl_lane_load_gb(os.path.join(path, 'LiveloadGB.inp'))
            self._batch_file(os.path.join(path, 'run.bat'))
            # self._write_lane_factor(os.path.join(path, "lane_matrix.dat"))
            self._persistence_(path)
            pass
        else:
            print("导出前，请生成fem模型.")
            return

    @staticmethod
    def more_value(start: float, end: float, apx_dist: float):
        npts = int(np.round((end - start) / apx_dist, 0))
        return np.linspace(start, end, npts + 1).tolist()

    @staticmethod
    def _batch_file(filestream):
        cmd = r'''set ANS_CONSEC=YES
REM set ANSYS194_WORKING_DIRECTORY=%s
"D:\Program Files\ANSYS Inc\v194\ansys\bin\winx64\ANSYS194" -b -i main.inp -o main.out
        ''' % (os.path.dirname(filestream))
        with open(filestream, 'w+') as fid:
            fid.write(cmd)

    @staticmethod
    def _apdl_begin(filestream, proj_name="Project A"):
        cmd = '''!=======================================================
! Modeled by Bill with Python Automation 2022-03
! Units: N,m,kg,s
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
/input,Boundary,inp
!/input,Debug,inp
/input,LiveloadGB,inp
finish''' % proj_name
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

    def _apdl_etype(self, filestream):
        cmd = "/prep7"
        cmd += '''! 单元        
et,181,SHELL181
et,182,PLANE182
et,188,BEAM188
keyopt,188,1,1 
keyopt,188,3,2
keyopt,181,3,0
keyopt,182,3,3
et,1840,MPC184,1
et,1841,MPC184,1
'''
        cmd += "r,182,%.3f" % self._sect_list[1].thickness
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
        cmd += "esel,s,secn,,2\n"
        cmd += "cm,girder,elem\n"
        cmd += "nsle,s,1\n"
        cmd += "nsel,u,node,,999999\n"
        cmd += "cm,gnode,node\n"
        cmd += "allsel\n"
        with open(filestream, 'w+') as fid:
            fid.write(cmd)

    def _apdl_lane_load_gb(self, filestream):
        cmd = """/solu
allsel
antype,0        
outres,erase
acel,0,0,0
OUTPR,ESOL,last,girder
!OUTPR,NLOAD,last,girder
!OUTRES,all,none
!OUTRES,esol,last,girder
/OUTPUT,liveload,res

"""
        for lane_no, fact, nlist in self.lane_matrix:
            for nn in nlist:
                cmd += "fdele,all,all\n"
                cmd += "f,%i,fy,-1000\n" % nn
                cmd += "time,%i\n" % nn
                cmd += "solve\n"
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
        self._main_ylist = np.unique(tmp).tolist()
        tmp2 = [0]
        for dist in self.cross_section.subgirder_arr:
            tmp2.append(tmp2[-1] + dist)
        self._sub_ylist = np.unique(tmp2).tolist()

        kp_y = self._sub_ylist + self._main_ylist
        kp_y = np.unique(kp_y)
        kp_y.sort()

        tmp = []
        for i in range(len(kp_y) - 1):
            tmp += self.more_value(kp_y[i], kp_y[i + 1], apx_dist=e_size_y)
        self._ylist = np.unique(tmp).tolist()

    def _create_plate(self, elem=181):
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
                self._elem_list[e] = Element(e, 3, elem, elem, 1, ns)
                e += 1
        pass

    def get_layer_num(self):
        prefix = max(self._node_list.keys())
        dig = np.power(10, len(str(prefix)) - 1)
        lay_num = dig * 10
        return lay_num

    def _create_girder(self):
        lay_num = self.get_layer_num()
        self._node_list[999999] = Node(999999, 0, 0, 1e5)
        val = list(self._node_list.values())
        girder_y = self._main_ylist[1:-1]
        ei = list(self._elem_list.keys())[-1] + 1
        beam_h = self._sect_list[2].w3
        slab_h = self._sect_list[1].thickness
        slab_o = self._sect_list[1].offset[1]
        slab_gap = slab_o - slab_h * 0.5
        station_list = [sp.station for sp in self._spans]
        for ii, y0 in enumerate(girder_y):  # 主梁
            nn = filter(lambda x: x.y == y0, val)
            for jj, n in enumerate(nn):
                # self._node_list[n.n + lay_num * 1] = n.copy(lay_num * 1, 0, 0, -slab_gap - 0.5 * beam_h)  # 主梁节点
                self._node_list[n.n + lay_num * 2] = n.copy(lay_num * 2, 0, 0,
                                                            -slab_gap - self.cross_section.cross_dist_a)  # 主梁上接口
                if self.cross_section.cross_dist_b != 0:
                    self._node_list[n.n + lay_num * 3] = n.copy(lay_num * 3, 0, 0,
                                                                -slab_gap - self.cross_section.cross_dist_a
                                                                - self.cross_section.cross_dist_b)  # 主梁下接口
                # if n.x in station_list:
                #     self._node_list[n.n + lay_num * 4] = n.copy(lay_num * 4, 0, 0, -slab_gap - beam_h)  # 主梁支座接口

                # ns = (n, self._node_list[n.n + lay_num * 1])
                # self._elem_list[ei] = Element(ei, 184, 1840, 1, 1, ns)  # MPC 板-梁
                # ei += 1

                ns = (n, self._node_list[n.n + lay_num * 2])
                self._elem_list[ei] = Element(ei, 184, 1841, 1, 1, ns)  # MPC 梁-梁上口
                ei += 1
                # if n.x in station_list:
                #     ns = (n, self._node_list[n.n + lay_num * 4])
                #     self._elem_list[ei] = Element(ei, 184, 184, 1, 1, ns)  # MPC 板-支座
                #     ei += 1
                if self.cross_section.cross_dist_b != 0:
                    ns = (self._node_list[n.n + lay_num * 2], self._node_list[n.n + lay_num * 3])
                    self._elem_list[ei] = Element(ei, 1841, 184, 1, 1, ns)  # MPC 梁上口-梁下口
                    ei += 1
                if jj != 0:
                    ns = (self._node_list[n.n + lay_num * 0 - 1], self._node_list[n.n + lay_num * 0], self._node_list[999999])
                    self._elem_list[ei] = Element(ei, 2, 188, 1, 2, ns)  # 梁
                    ei += 1
        girder_y = self._sub_ylist[1:-1]
        beam_h = self._sect_list[3].w3
        for ii, y0 in enumerate(girder_y):  # 纵梁
            nn = filter(lambda x: x.y == y0, val)
            for jj, n in enumerate(nn):
                # self._node_list[n.n + lay_num * 1] = n.copy(lay_num * 1, 0, 0, -slab_gap - 0.5 * beam_h)  # 小纵梁节点
                self._node_list[n.n + lay_num * 2] = n.copy(lay_num * 2, 0, 0, -slab_gap - beam_h)  # 小纵梁梁底节点
                # ns = (n, self._node_list[n.n + lay_num * 1])
                # self._elem_list[ei] = Element(ei, 184, 1840, 1, 1, ns)  # MPC 板-梁
                # ei += 1
                ns = (self._node_list[n.n + lay_num * 0], self._node_list[n.n + lay_num * 2])
                self._elem_list[ei] = Element(ei, 184, 1841, 1, 1, ns)  # MPC 梁-梁
                ei += 1
                if jj != 0:
                    ns = (self._node_list[n.n + lay_num * 0 - 1], self._node_list[n.n + lay_num * 0], self._node_list[999999])
                    self._elem_list[ei] = Element(ei, 2, 188, 1, 3, ns)
                    ei += 1

    def _create_cross_beam(self):
        ei = list(self._elem_list.keys())[-1] + 1
        lay_num = self.get_layer_num()
        val = list(self._node_list.values())
        z0 = -self.cross_section.slab_gap - self.cross_section.cross_dist_a
        z1 = z0 - self.cross_section.cross_dist_b
        for x0 in self._main_xlist:
            nn = filter(lambda node: node.x == x0 and node.z == z0, val)
            nnlist = [node for node in nn]
            nnlist.sort()
            for jj, n in enumerate(nnlist):
                if jj != 0:
                    ns = (nnlist[jj], nnlist[jj - 1], self._node_list[999999])
                    self._elem_list[ei] = Element(ei, 2, 188, 1, 4, ns)
                    ei += 1
            if self.cross_section.cross_dist_b != 0:
                mm = filter(lambda node: node.x == x0 and node.z == z1, val)
                mmlist = [node for node in mm]
                mmlist.sort()
                for jj, n in enumerate(mmlist):
                    if jj != 0:
                        ns = (mmlist[jj], mmlist[jj - 1], self._node_list[999999])
                        self._elem_list[ei] = Element(ei, 2, 188, 1, 5, ns)
                        ei += 1
                for k in range(len(nnlist)):
                    if k % 2 != 0:
                        p = divmod((k + 1), 2)[0]
                        ns = (nnlist[k], mmlist[p - 1], self._node_list[999999])
                        self._elem_list[ei] = Element(ei, 2, 188, 1, 6, ns)
                        ei += 1
                        ns = (nnlist[k], mmlist[p], self._node_list[999999])
                        self._elem_list[ei] = Element(ei, 2, 188, 1, 6, ns)
                        ei += 1

    def _apdl_boundary(self, filestream):
        cmd = "/prep7\n"
        x_fix = int(len(self._spans) / 2) - 1
        y_fix = int((len(self._main_ylist) - 2) / 2) - 1
        station_list = [sp.station for sp in self._spans]
        # z0 = -self.cross_section.slab_gap - self._sect_list[2].w3 * 0.5
        z0 = 0
        val = list(self._node_list.values())
        ylist = list(self._main_ylist)[1:-1]
        for i, x0 in enumerate(station_list):
            nn = filter(lambda node: node.x == x0 and abs(node.z - z0) < 1e-3 and node.y in ylist, val)
            nnlist = [node for node in nn]
            for j, node in enumerate(nnlist):
                cmd += "d,%i,uy,0\n" % node.n
                if i == x_fix:
                    cmd += "d,%i,ux,0\n" % node.n
                if j == y_fix:
                    cmd += "d,%i,uz,0\n" % node.n
        with open(filestream, 'w+') as fid:
            fid.write(cmd)

    def _get_cal_span(self):
        tmp = []
        for i in range(len(self._spans) - 1):
            tmp.append(self._spans[i + 1].station - self._spans[i].station)
        return max(tmp)

    def get_nodes_by_y(self, y0: float):
        """
        桥面点序列
        :param y0:
        :return:
        """
        val = list(self._node_list.values())
        nn = filter(lambda node: node.y == y0 and node.z == 0.0, val)
        nnlist = [node.n for node in nn]
        return nnlist

    def get_parameters(self):
        S = self.cross_section.girder_arr[1] * 1e3
        L = (self._spans[1].station - self._spans[0].station) * 1e3
        Nb = len(self.cross_section.girder_arr) - 1
        Eb = self._mat_list[1].ex
        Ed = self._mat_list[3].ex
        A = self._sect_list[2].area * 1e6
        I = self._sect_list[2].inertia * 1e12
        y0 = self._sect_list[2].yg
        n = Eb / Ed
        eg = self.cross_section.slab_gap + (self._sect_list[2].w3 - y0) + self._sect_list[1].thickness * 0.5
        eg = eg * 1e3
        Kg = n * (I + A * eg ** 2)
        ts = self._sect_list[1].thickness * 1e3
        return {'S': S, "L": L, "Kg": Kg, 'ts': ts}

    def add_live_load(self, load):
        self.live_load = load
        self._def_lane_gb(load.locations)

    def _def_lane_gb(self, loc):
        """
        定义国标车道
        :param loc: 车道横向位置列表
        :return:
        """

        res = []
        for ii, y0 in enumerate(loc):
            if y0 in self._ylist:
                res.append((ii, 1.0, self.get_nodes_by_y(y0)))
            else:
                tmp = self._ylist + [y0, ]
                tmp.sort()
                ni = tmp.index(y0)
                ya = self._ylist[ni - 1]
                yb = self._ylist[ni]
                fa = (yb - y0) / (yb - ya)
                fb = (y0 - ya) / (yb - ya)
                res.append((ii, fa, self.get_nodes_by_y(ya)))
                res.append((ii, fb, self.get_nodes_by_y(yb)))
        self.lane_matrix = res

    @staticmethod
    def run_ansys(path):
        subprocess.call(os.path.join(path, 'run.bat'), shell=True, cwd=path)
        pass

    def _persistence_(self, path):
        with open(os.path.join(path, "bridge.pickle"), 'wb') as fid:
            pickle.dump(self, fid, pickle.HIGHEST_PROTOCOL)

    def _write_lane_factor(self, param):
        with open(param, 'wb') as fid:
            pickle.dump(self.lane_matrix, fid, pickle.HIGHEST_PROTOCOL)
