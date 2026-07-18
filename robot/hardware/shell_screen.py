from abc import ABC, abstractmethod

class ShellScreen(ABC):
    @abstractmethod
    def image(self,path): pass

    @abstractmethod
    def text(self,title,lines): pass

    @abstractmethod
    def clear(self): pass