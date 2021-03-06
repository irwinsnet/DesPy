#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
******************
despy.model.trigger
******************

..  autosummary::

    Trigger
    
..  todo

    
"""
from abc import ABCMeta, abstractmethod

from despy.session import Session

class AbstractTrigger(metaclass = ABCMeta):
    def __init__(self):
        self.session = Session()
    
    @abstractmethod
    def check(self):
        pass
    
    @abstractmethod
    def pull(self):
        return True
    

class TimeTrigger(AbstractTrigger):
    def __init__(self, until):
        super().__init__()
        self.until = until
        
    def check(self):
        return self.session.sim.peek() > self.until
    
    def pull(self):
        return False


if __name__ == '__main__':
    pass