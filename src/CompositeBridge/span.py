from PyAngle import Angle


class Span:
    def __init__(self, station: float, angle: 'Angle' = Angle.from_degrees(90.0)):
        self.station = station
        self.angle = angle