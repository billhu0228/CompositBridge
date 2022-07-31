from abc import ABCMeta, abstractmethod


class ApdlWriteable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def apdl_str(self):
        pass