class ContinuousBeam:
    span_num = 0
    span_list = []
    force_list = []
    __script__ = ""

    def __init__(self, span: list):
        """
        连续梁模型
        """
        self.span_list = span
        self.span_num = len(span)

        pass

    def apply(self, F1, ignore_range=True):
        pass

    def get_moment(self, x):
        pass

    def get_reaction(self, i):
        pass

    def get_shear(self, x):
        pass
