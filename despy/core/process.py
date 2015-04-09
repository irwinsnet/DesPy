#!/usr/bin/env python3

from collections import namedtuple
import types
from despy.core.component import Component
from despy.core.simulation import FelItem as fi
from despy.core.event import Event

#TODO : Refactor processTuple. Make attribute names consistent with
#felItem class.

class Process(Component):
    """Represents a simulation process that periodically schedules events and
    maintains state (i.e., retains variable values) between events.
    """

    def __init__(self, model, name, generator_function = None):
        """Creates a process object.
        
        *Arguments*
            model (despy.model.Model
                A despy.Model object that contains the process object.
            name (String):
                A short string that will be displayed in trace reports
                and other outputs.
        """
        super().__init__(model, name)
        
        self.processTuple = namedtuple('processTuple', ['event_',
                                                        'delay_',
                                                        'priority_'])
        self.awake = False
        
        if generator_function != None:
            self.generator = generator_function
            
        if isinstance(self.generator, types.FunctionType):
            self._generator = self.generator(self)
        elif isinstance(self.generator, types.MethodType):
            self._generator = self.generator()
        else:
            raise TypeError(\
                    "generator_method must be a function or class method")
        
    def schedule_timeout(self, name, delay = 0,
                         priority = fi.PRIORITY_STANDARD,
                         trace_fields = None):
        event = ProcessTimeOutEvent(self, name, trace_fields)
        return self.processTuple(event_ = event,
                                 delay_ = delay,
                                 priority_ = priority)

    def call_process(self):
        scheduled_event = next(self._generator)
        if scheduled_event != None:
            self.model.schedule(scheduled_event.event_,
                                scheduled_event.delay_,
                                scheduled_event.priority_)
        
    def reset_process(self):
        self.generator = self._generator()
        
    def start(self, delay = 0, priority = fi.PRIORITY_STANDARD):
        self.model.schedule(ProcessTimeOutEvent(self, "Start " + self.name),
                            delay, priority)
        self.awake = True
        
    def sleep(self):
        self.awake = False
        return None
    
    def wake(self, delay = 0, priority = fi.PRIORITY_STANDARD):
        if not self.awake:
            self.start(delay, priority)
        
class ProcessTimeOutEvent(Event):
    def process_callback(self):
        self._process.call_process()
    
    def __init__(self, process, name, trace_fields = None):
        self._process = process
        super().__init__(process.model, name, trace_fields)
        self.append_callback(self.process_callback)
        
    def update_trace_record(self, trace_record):
        return super().update_trace_record(trace_record)
