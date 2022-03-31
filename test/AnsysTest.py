from src.CompositeBridge import CompositeBridge
from src.CompositeBridge import CrossArrangement, Span
from src.CompositeBridge import Material, ShellSection, ISection

g1 = [1.2] + [4, ] * 3 + [1.2]
g2 = [1.2 + 2] + [4, ] * 2 + [2 + 1.2]
ca = CrossArrangement(sum(g1), g1, g2, 0.25, 0.05, 0.3, 1.0)

span1 = Span(00)
span2 = Span(32)
span3 = Span(68)
span4 = Span(115)
sps = [span1, span2, span3, span4]
# sps = [span1, span2]

m1 = Material(1, 206000e6, 7850, 1.2e5, 0.3, 'Q420')
m2 = Material(2, 206000e6, 7850, 1.2e5, 0.3, 'Q345')
m3 = Material(3, 34500e6, 2500, 1.1e5, 0.2, 'Concrete')
m184 = Material(184, 0, 0, 0, 0, 'MP184')

Bridge = CompositeBridge(sps, ca)

Bridge.add_material(m1)
Bridge.add_material(m2)
Bridge.add_material(m3)
Bridge.add_material(m184)

s1 = ShellSection(1, 'T250', th=0.250, offset=(0, 0.25 * 0.5 + 0.05))
s2 = ISection(2, "I2000", offset=(0, 1), w1=0.6, w2=0.6, w3=2.0, t1=0.060, t2=0.060, t3=0.020)
s3 = ISection(3, "I300", offset=(0, 0.15), w1=0.3, w2=0.3, w3=0.3, t1=0.010, t2=0.010, t3=0.008)
s4 = ISection(4, "I300", offset=(0, 0.3), w1=0.3, w2=0.3, w3=0.3, t1=0.010, t2=0.010, t3=0.008)
s5 = ISection(5, "I300", offset=(0, 0.3), w1=0.3, w2=0.3, w3=0.3, t1=0.010, t2=0.010, t3=0.008)
s6 = ISection(6, "I300", offset=(0, 0.2), w1=0.15, w2=0.15, w3=0.2, t1=0.010, t2=0.010, t3=0.008)

Bridge.add_section(s1)
Bridge.add_section(s2)
Bridge.add_section(s3)
Bridge.add_section(s4)
Bridge.add_section(s5)
Bridge.add_section(s6)

Bridge.generate_fem(2, 0.5)
Bridge.def_lane_gb(loc=[4.2, 10, 12])  # 定义车道位置，国标
Bridge.write_database(path=r"G:\20220217 组合梁论文\02 Python\bin\Model2", projectname="TestModelA")
Bridge.run_ansys(path=r"G:\20220217 组合梁论文\02 Python\bin\Model2")
