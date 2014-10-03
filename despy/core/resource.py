from despy.core.root import _ModelMember
from despy.core import Event
from collections import namedtuple

# TODO: Fix check_queue method. It should set the resource to None and pass the
#   resource index to start_activity().

# TODO: Add different options for selection of empty resources, either
# prioritization by number, random selection, or equal loading.

class Resource(_ModelMember):
    def __init__(self, model, name, capacity):
        self._model = model
        self._name = name
        self.capacity = capacity
        # Each position is represented by a list with item [0] being the
        #   item being served by the resource and item[1] being the name of
        #   the position.
        self._positions = {index: {'name': "#{0}".format(index),
                                   'user': None,
                                   'start_time': None} \
                           for index in range(1, self.capacity + 1)}
                
        self._queue = None
        self._activity_time = None
    
    @property
    def queue(self):
        return self._queue

    @queue.setter
    def queue(self, queue):
        self._queue = queue
        
    @property
    def activity_time(self):
        return self._activity_time
    
    @activity_time.setter
    def activity_time(self, time_function):
        self._activity_time = time_function

    def get_activity_time(self):
        if self.activity_time is None:
            raise NotImplementedError
        else:
            return self.activity_time()
    
    def get_empty_position(self):
        for index in range(1, self.capacity + 1):
            if self[index]['user'] is None:
                return index
        return False
    
    def __getitem__(self, index):
        return self._positions[index]
    
    def __setitem__(self, index, item):
        self._positions[index] = item

    def request(self, user):
        index = self.get_empty_position()
        if index:
            self[index]['user'] = user
            self[index]['start_time'] = self.model.experiment.now
            self.start_activity(index)
            return index
        else:
            if self.queue is not None:
                self.queue.add(user)
            return False
        
    def start_activity(self, index):
        trace_output = "Trace: Position {0} ".format(self[index]['name'])
        trace_output += \
                "starting activity on {0} ".format(self[index]['user'].name)
        trace_output += "# {0}".format(self[index]['user'].number)
        self.model.experiment.trace.add_output(trace_output)
        
        service_time = self.get_activity_time()
        event_name = "Position {0} Finished Activity "\
                .format(self[index]['name'])
        event_name += "on {0} # {1}. ".format(self[index]['user'].name,
                                            self[index]['user'].number)
        event_name += "Service time was {0} minutes.".format(service_time)
        finish_event = ResourceFinishActivityEvent(\
            self, event_name, index)
        
        self.model.schedule(finish_event, service_time)
        
    def finish_activity(self, index):
        self.remove_user(index)
        if self.queue.length > 0:
            user = self.queue.remove()
            self.request(user)             
        
    def remove_user(self, index):
        user = self[index]['user']
        self[index]['user'] = None
        self[index]['start_time'] = None
        return user
    
class ResourceFinishActivityEvent(Event):
    def check_resource_queue(self):
        self._resource.finish_activity(self.index)
    
    def __init__(self, resource, name, index):
        self._resource = resource
        super().__init__(resource.model, name)
        self.append_callback(self.check_resource_queue)
        self.index = index
        