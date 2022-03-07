from CompositeBridge import CompositeBridge
from CompositeBridge import CrossArrangement, Span
from CompositeBridge import Material

g1 = [1.2] + [4, ] * 3 + [1.2]
g2 = [1.2 + 2] + [4, ] * 2 + [2 + 1.2]
ca = CrossArrangement(sum(g1), g1, g2, 0.25, 0.05)

span1 = Span(0)
span2 = Span(30)
span3 = Span(60)
span4 = Span(90)
sps = [span1, span2, span3, span4]

m1 = Material(1, 206000, 7.85e-9, 1.2e5, 0.3, 'Q420')
m2 = Material(2, 206000, 7.85e-9, 1.2e5, 0.3, 'Q345')
m3 = Material(3, 34500, 2.5e-9, 1.1e5, 0.2, 'Q345')

Bridge = CompositeBridge(sps, ca)
kk=Bridge.more_value(0,30,4.8)

Bridge.add_material(m1)
Bridge.add_material(m2)
Bridge.add_material(m3)

Bridge.generate_fem()
Bridge.write_database(path="../bin/Model1", projectname="TestModelA")
