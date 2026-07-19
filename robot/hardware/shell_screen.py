from abc import ABC,abstractmethod

class ShellScreen(ABC):
    @abstractmethod
    def image(self,path): pass

    @abstractmethod
    def status(self,data): pass

    @abstractmethod
    def message(self,text,color=None): pass

    @abstractmethod
    def log(self,lines): pass

    @abstractmethod
    def clear(self): pass