class GBLiveLoad:
    __slots__ = ('Pk', 'q', 'locations', 'multi_factors',)

    def __init__(self, cal_span, loc):
        if cal_span <= 5:
            self.Pk = 270000
        elif cal_span < 50:
            self.Pk = 2 * (cal_span + 130) * 1000
        else:
            self.Pk = 360000
        self.q = 10500
        self.locations = loc
        if len(loc) == 1:
            self.multi_factors = 1.2
        elif len(loc) == 2:
            self.multi_factors = 1.0
        elif len(loc) == 3:
            self.multi_factors = 0.78
        elif len(loc) == 4:
            self.multi_factors = 0.67
        elif len(loc) == 5:
            self.multi_factors = 0.6
        else:
            raise Exception("超过定义")