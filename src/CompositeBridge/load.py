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

    @staticmethod
    def auto_multi(width):
        locss = []
        for i in range(8):
            locss.append(i * 2.1 + 0.5 + 0.9)
        if width < 7:
            return locss[0:1]
        elif width < 10.5:
            return locss[0:2]
        elif width < 14.0:
            return locss[0:3]
        elif width < 17.5:
            return locss[0:4]
        elif width < 21.0:
            return locss[0:5]
        elif width < 24.5:
            return locss[0:6]
        elif width < 28.0:
            return locss[0:7]

    @staticmethod
    def get_multi(num):
        ret = []
        for i in range(num):
            ret.append(i * 2.1 + 0.5 + 0.9)
        return ret
