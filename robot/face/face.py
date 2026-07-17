from abc import ABC, abstractmethod


class Face(ABC):
    """
    Abstract face interface.

    The Brain interacts with this interface only.
    The implementation can be real OLED eyes or simulation.
    """

    @abstractmethod
    def play(self, expression):
        pass

    @abstractmethod
    def update(self):
        pass