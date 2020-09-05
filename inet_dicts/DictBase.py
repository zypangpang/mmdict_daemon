import abc
class DictBase(abc.ABC):
    @abc.abstractmethod
    def lookup(cls,word):
        pass
