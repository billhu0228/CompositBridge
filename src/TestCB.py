from CompositeBridge import CompositeBridge
from CompositeBridge import CrossArrangement, Span
from CompositeBridge import Material, ShellSection, ISection

g1 = [1.2] + [4, ] * 3 + [1.2]
g2 = [1.2 + 2] + [4, ] * 2 + [2 + 1.2]
ca = CrossArrangement(sum(g1), g1, g2, 0.25, 0.05)

span1 = Span(00)
span2 = Span(30)
span3 = Span(60)
span4 = Span(90)
sps = [span1, span2, span3, span4]

m1 = Material(1, 206000, 7.85e-9, 1.2e5, 0.3, 'Q420')
m2 = Material(2, 206000, 7.85e-9, 1.2e5, 0.3, 'Q345')
m3 = Material(3, 34500, 2.5e-9, 1.1e5, 0.2, 'Q345')
m184 = Material(184, 0, 0, 0, 0, 'MP184')

Bridge = CompositeBridge(sps, ca)

Bridge.add_material(m1)
Bridge.add_material(m2)
Bridge.add_material(m3)
Bridge.add_material(m184)

s1 = ShellSection(1, 'T250', th=0.250, offset=(0, 0.25 * 0.5 + 0.05))
s2 = ISection(2, "I2000", offset=(0, 1), w1=0.6, w2=0.6, w3=2.0, t1=0.060, t2=0.060, t3=0.020)
s3 = ISection(3, "I300", offset=(0, 0.15), w1=0.3, w2=0.3, w3=0.3, t1=0.010, t2=0.010, t3=0.008)

Bridge.add_section(s1)
Bridge.add_section(s2)
Bridge.add_section(s3)

Bridge.generate_fem(2, 0.5)
Bridge.write_database(path="../bin/Model1", projectname="TestModelA")

