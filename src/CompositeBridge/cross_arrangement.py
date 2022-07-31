from typing import List


class CrossArrangement:
    """
    正交横截面
    """
    __slots__ = ("width", 'girder_arr', 'subgirder_arr', 'slab_thickness', 'slab_gap', 'cross_dist_a', 'cross_dist_b')
    width: float
    girder_arr: List[float]
    subgirder_arr: List[float]
    slab_thickness: float
    slab_gap: float
    cross_dist_a: float  # 横梁上弦至主梁上表面距离
    cross_dist_b: float  # 横梁下弦至横梁上弦上表面距离，0表示无下弦

    def __init__(self, width, girder_arr, subgirder_arr, slab_thickness, slab_gap, x_0, x_1):
        """
        配置正交横截面
        :param width: 横截面总宽（护栏外缘）
        :param girder_arr: 主梁间距列表（含边梁至护栏外缘距离）
        :param subgirder_arr: 次梁间距列表（含边梁至护栏外缘距离）
        :param slab_thickness: 桥面板厚度
        :param slab_gap: 桥面板-主梁上缘间距
        :param x_0: 横梁上弦至主梁上表面距离
        :param x_1: 横梁下弦至横梁上弦上表面距离，0表示无下弦
        """
        self.width = width
        self.girder_arr = girder_arr
        self.subgirder_arr = subgirder_arr
        self.slab_thickness = slab_thickness
        self.slab_gap = slab_gap
        if sum(self.girder_arr) != self.width or sum(self.subgirder_arr) != self.width:
            raise Exception("梁间距配置有误.")
        self.cross_dist_a = x_0
        self.cross_dist_b = x_1