import ContinuousBeamCalculator as CBC

from ContinuousBeamCalculator import ContinuousBeam, ConcentratedForce, DistributedForce

from pandas import DataFrame

from numpy import array





# 1. 建立连续梁
Beam = ContinuousBeam(span=[15, 15, ])

F1 = ConcentratedForce(x=7.5)
F2 = ConcentratedForce(x=15 + 7.5)
Q1 = DistributedForce(range=(0, 15))
Q2 = DistributedForce(range=(0, 30))

Beam.apply(F1)
Beam.apply(F2)
Beam.apply(Q1, ignore_range=True)
Beam.apply(Q2)

valA = Beam.get_moment(x=15)
valB = Beam.get_reaction(i=0)
valC = Beam.get_shear(x=10)
