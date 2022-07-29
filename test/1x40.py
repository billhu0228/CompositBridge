from src.CompositeBridge import *
from src.CompositeBridge.load import GBLiveLoad

# from src.CompositeBridge.span import Span
# from src.CompositeBridge.cross_arrangement import CrossArrangement
# from src.CompositeBridge import Material, ShellSection, ISection

g1 = [1.2] + [4.7, ] * 3 + [1.2]
# g2 = [1.2 + 2.35] + [4.7, ] * 2 + [2.35 + 1.2]
g2 = [16.5]
ca = CrossArrangement(sum(g1), g1, g2, 0.25, 0.05, 0.3, 0.0)

span1 = Span(00)
span2 = Span(40)
sps = [span1, span2]
# sps = [span1, span2]

m1 = Material(1, 206000e6, 7850, 1.2e5, 0.3, 'Q420')
m2 = Material(2, 206000e6, 7850, 1.2e5, 0.3, 'Q345')
m3 = Material(3, 34500e6, 2500, 1.1e5, 0.2, 'Concrete')
m184 = Material(184, 0, 0, 0, 0, 'MP184')

Bridge = CompositeBridge(sps, ca, cross_beam_dist=40)

Bridge.add_material(m1)
Bridge.add_material(m2)
Bridge.add_material(m3)
Bridge.add_material(m184)

s1 = ShellSection(1, 'T250', th=0.050, offset=(0, 0.05 * 0.5 + 0.05))
s2 = ISection(2, "I1800", offset=(0, 1.8), w1=0.7, w2=0.6, w3=1.8, t1=0.032, t2=0.024, t3=0.018)
s3 = ISection(3, "I300", offset=(0, 0.3), w1=0.3, w2=0.6, w3=0.3, t1=0.010, t2=0.010, t3=0.008)
s4 = ISection(4, "I700", offset=(0, 0.7), w1=0.3, w2=0.3, w3=0.7, t1=0.024, t2=0.024, t3=0.013)
s5 = ISection(5, "I300", offset=(0, 0.3), w1=0.3, w2=0.3, w3=0.3, t1=0.010, t2=0.010, t3=0.008)
# s6 = ISection(6, "I300", offset=(0, 0.2), w1=0.15, w2=0.15, w3=0.2, t1=0.010, t2=0.010, t3=0.008)

Bridge.add_section(s1)
Bridge.add_section(s2)
Bridge.add_section(s3)
Bridge.add_section(s4)
Bridge.add_section(s5)
# Bridge.add_section(s6)

Bridge.generate_fem(0.5, 0.5, 181)
# Bridge.def_lane_gb(loc=[2.0, ])  # 定义车道位置，国标

modelName = "M1"

LiveLoad = GBLiveLoad(Bridge.cal_span, loc=[5.9])
Bridge.add_live_load(LiveLoad)  # 定义车道位置，国标
Bridge.write_database(path=r"E:\20220217 组合梁论文\02 Python\bin\%s" % modelName, projectname="TestModelA")
Bridge.run_ansys(path=r"E:\20220217 组合梁论文\02 Python\bin\%s" % modelName)
