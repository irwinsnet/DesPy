#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
*******************
despy.core.resource
*******************

:class:`ResourceQueue`
    Represents a limited, real-world, entity that provides a service.
"""

from collections import OrderedDict, namedtuple
from scipy.stats import randint
from despy.core.component import Component
from despy.core.event import Event
from despy.core.queue import Queue

# TODO: Test different options for selection of empty resources, either
# prioritization by number, random selection, or equal loading.

# TODO: Fix trace report. Label the interarrival time state on which
# customer service was finished.

class Resource(Component):
    """Represents a limited, real-world entity that provides a service.
    
    An object or entity with limited availability that provides some
    kind of service.
    
    **Inherited Classes**
      * :class:`despy.base.named_object.NamedObject`
      * :class:`despy.core.component.Component`
      
    **Attributes**
      * :attr:`Resource.capacity`: The number of entities that can be
        served simultaneously.
      * :attr:`Resource.res_queue`: The resourceQueue that contains the
        queue of incoming users.
      * :attr:`Resource.service_time`: A method that returns the
        time required by the resource.
      * :attr:`Resource.Station_tuple`: A Python namedtuple with an
        'entity' field and a 'start_time' field.
      * :attr:`Resource.stations`: A list of resource stations
        with length = Resource.capacity. 
        
    **Methods**
      * :meth:`Resource.__str__`: Magic method that converts the
        resource object to a string.
      * :meth:`Resource.__getitem__`: Allows accessing resource
        stations with array brackets.
      * :meth:`Resource.__setitem__`: Allows setting resource stations
        with array brackets.
      * :meth:`Resource.get_available_station`: Gets the empty resource
        position with the lowest number.
      * :meth:`Resource.request`: Request a resource for a entity.        
      * :meth:`Resource.get_service_time`: Gets the time needed for a
        position to complete an activity.
      * :meth:`Resource.start_service`: Commence servicing a entity at the
        index position.
      * :meth:`Resource.finish_service`:
      * :meth:`Resource.remove_entity`: Remove entity from a resource
        station.
    """
    
    
    def __init__(self, model, name, capacity = 1, time_function = None):
        """Create a Resource object.
        
        *Arguments*
            ``model`` (:class:`despy.core.model.Model`)
                The Resource must be assigned to a Model object.
            ``name`` (String)
                A short descriptive name for the Resource object.
            ``capacity`` (Integer)
                Optional, defaults to 1. The number of stations that the
                Resource object contains. Each station can service one
                object.
            ``time_function`` (Python function object)
                Optional, defaults to None. A function that returns the
                time required to service an entity.
        """
        super().__init__(model, name)
        
        #Instance Attributes
        self._capacity = capacity
        self._res_queue = None
        self._service_time = time_function
        
        self._Station_tuple = namedtuple('Station',
                                        ['entity', 'start_time'])
    
        empty_station = self.Station_tuple(entity = None,
                                           start_time = None)
        self._stations = [empty_station] * self.capacity
        """  """
        
    @property
    def capacity(self):
        """The number of entities that can be served simultaneously.
        
        *Type:* Integer
        """
        return self._capacity
    
    @capacity.setter
    def capacity(self, capacity):
        self._capacity = capacity
        
    @property    
    def res_queue(self):
        """The resourceQueue that contains the queue of incoming users.
        
        *Type:* :class:`despy.core.resource.ResourceQueue`, read-only
        """
        return self._res_queue
    
    @property
    def service_time(self):
        """Property that contains a service time function object.
        
        Designers can customize the resource's method for determining
        the time required for service by setting this property to a
        function object. The function should accept the resource class
        and the station index as parameters and return a positive
        integer.
        
        *Type:* Function object.
        """
        return self._service_time
    
    @service_time.setter
    def service_time(self, time_function):
        self._service_time = time_function
        
    @property
    def Station_tuple(self):
        """A Python namedtuple with 'entity' and 'start_time' fields.
        
        *Type:* :class:`collections.namedtuple`, read-only
        """
        return self._Station_tuple
    
    @property
    def stations(self):
        """A list of resource stations with length = Resource.capacity.
        
        *Type:* :class:`Resource.Station_tuple`
        """
        return self._stations
    
    def __str__(self):
        """Magic method that converts the resource object to a string.
        
        *Returns:* The name property of the resource object.
        """
        return self.name
    
    def __getitem__(self, index):
        """Allows using array brackets to access resource stations.
        
        A Python magic method that allows using array brackets to get
        a resource station.
        
        *Arguments:*
            ``index`` (Integer)
                The index number of the resource station.
                
        *Returns:* (ResourceStation tuple)
            A ResourceStation namedtuple object.
        """
        return self.stations[index]
    
    def __setitem__(self, index, entity):
        """Allows setting resource stations with array brackets.
        
        *Arguments:*
            ``index`` (Integer)
                The index number of the resource station.
            ``entity`` (ResourceStation namedtuple)
                A ResourceStation namedtuple object.
        """
        self.stations[index] = entity

    def get_available_station(self, random = False):
        """Returns the index of an empty station.
        
        *Arguments*
            ``random`` (Boolean)
                If set to True, randomly chooses the index of an empty
                station. Otherwise, returns the index of the empty
                station with the lowest index value.
                
        *Returns:* A positive integer representing the index number of
        the station. ``None`` if no stations are empty.
        """
        empty_stations = []
        for index in range(self.capacity):
            if self.stations[index].entity == None:
                empty_stations.append(index)
        
        if len(empty_stations) == 0:
            return None
        elif not random:
            return empty_stations[0]
        else:
            return empty_stations[randint(0, len(empty_stations) - 1)]        

    def request(self, entity, random = False):
        """Request a resource for a entity.
        
        Checks if a resource position is available. If so, starts
        serving the entity and returns the index of the resource position.
        Otherwise returns False and adds the entity to the resource queue.
        
        *Arguments*
            ``entity``
                The entity that will be serviced by the resource.
                
        *Returns:* If a resource position is available, returns the
        index value of the resource that will serve the entity. Otherwise
        returns False.
        """
            
        index = self.get_available_station()

        if index is not None:
            #ResourceQueue position is available
            assert(self.stations[index].entity == None) #Resource is open
            self.start_service(index, entity)
            return index
        else:
            #Resources all busy
            if self.res_queue is not None:
                self.res_queue.add(entity)
            return False 

    def get_service_time(self, station_index):
        """Gets the time needed for a position to complete an activity.
        
        *Arguments*
            ``station_index``
                The index of the applicable resource station.
            
        *Raises*
            ``NotImplementedError``: Raised if entity has not set the
            ``ResourceQueue.service_time`` property to a function.
        """
        try:
            return self.service_time(station_index)
        except:
            if self.service_time is None:
                raise NotImplementedError  
    
    def start_service(self, index, entity):
        """Commence servicing a entity at the index position.
        
        *Arguments*
            ``index``
                The index number of the resource position that will
                be servicing the entity.
        """

        #Assign entity to station
        self.stations[index] = self.Station_tuple(entity, self.sim.now)
        
        #Create trace record for starting the service.
        fields = OrderedDict()
        fields['Resource'] = self.name + '-' + str(index)
        fields['User'] = self.stations[index].entity
        message = "Starting Service"
        self.sim.gen.trace.add_message(message, fields)
        
        #Get service time and schedule end of service on FEL.
        service_time = self.get_service_time(index)
        finish_event = ResourceFinishServiceEvent(\
            self, index, service_time)
        self.model.schedule(finish_event, service_time)
        
    def finish_service(self, index):
        """Remove entity from a resource station.
        
        *Arguments:*
            ``index``: (Integer)
                The index number of the resource station.
        """
        self.stations[index] = self.Station_tuple(None, None)
        if self.res_queue:
            if self.res_queue.length > 0:
                entity = self.res_queue.remove()
                self.start_service(index, entity)   
    
    def remove_entity(self, index):
        """Remove entity from a resource station.
        
        *Arguments*
            ``index``
                The index number of the station from which the entity will
                be removed.
        
        *Returns:* The entity that was being serviced by the resource.
        """
        entity = self.stations[index].entity
        self.stations[index].entity = None
        self.stations[index].start_time = None
        return entity


class ResourceFinishServiceEvent(Event):
    """Event that is called when the resource completes it's service.
    
    **Inherited Classes**
      * :class:`despy.base.named_object.NamedObject`
      * :class:`despy.core.component.Component`
      * :class:`despy.core.event.Event`
      
    The ResourceFinishServiceEvent object occurs when the resource
    finishes servicing the assigned entity (after the designated
    service time has elapsed). 
    
    **Attributes**
      * :attr:`ResourceFinishServiceEvent.resource`: The applicable
        :class:`despy.core.resource.Resource` object.
      * :attr:`ResourceFinishServiceEvent.station_index`: The index
        number of the station that is finishing it's service.
      * :attr:`ResourceFinishServiceEvent.service_time`: The elapsed
        service time.
        
    **Methods**
      * :meth:`ResourceFinishServiceEvent.check_resource_queue`: The
        event's callback method that checks the queue for a waiting
        entity.
      * :meth:`ResourceFinishServiceEvent._update_trace_record`: Adds
        the entity name and service time to the trace report.
    """
    
    
    def __init__(self, resource, station_index, service_time):
        """Create a ResourceFinishServiceEvent object.
        
        *Arguments:*
            ``resource`` (:class:`Resource`)
                The Resource that will complete the service.
            ``station_index`` (Integer)
                The index number of the resource station.
            ``service_time`` (Integer)
                The time required to complete the service.
        """
        super().__init__(resource.model, "Finished Service")
        
        self._resource = resource
        self._station_index = station_index
        self._service_time = service_time
        self.append_callback(self.check_resource_queue)
        
    @property
    def resource(self):
        """The applicable Resource object.
        
        *Type*: class:`despy.core.resource.Resource`, read-only
        """
        return self._resource
    
    @property
    def station_index(self):
        """Index number of the station that is finishing service.
        
        *Type:* Integer, read-only
        """
        return self._station_index
    
    @property
    def service_time(self):
        """The elapsed service time.
        
        *Type:* Integer, read-only
        """
        return self._service_time
        
    def check_resource_queue(self):
        """The event's callback method that checks the queue for a
        waiting entity.
        """
        self.resource.finish_service(self.station_index)        
        
    def _update_trace_record(self, trace_record):
        """Adds the entity name and service time to the trace report.
        """
        trace_record['entity'] = \
                self.resource.stations[self.station_index].entity
        trace_record['duration_label'] = 'Service Time:'
        trace_record['duration_field'] = self.service_time
        return trace_record


class ResourceQueue(Queue):
    """A queue that provides entities to a resource object.
    
    A specialized queue that provides entities to one or more resource
    objects.
    
    **Inherited Classes**
      * :class:`despy.base.named_object.NamedObject`
      * :class:`despy.core.component.Component`
      * :class:`despy.core.queue.Queue`
      
    **Attributes**
      * :attr:`num_resources`: The number of resources added to the
      resourceQueue object.
        
    **Methods**
      * :meth:`ResourceQueue.get_available_resource`: Gets the empty
        resource position with the lowest number.
      * :meth:`ResourceQueue.__getitem__`: Allows accessing resource
        positions with array brackets.
      * :meth:`ResourceQueue.__setitem__`: Allows setting resource
        positions with array brackets.
      * :meth:`ResourceQueue.assign_resource`: Assign a resource to the
        resourceQueue object.
      * :meth:`ResourceQueue.get_available_resource`: Gets the index
        number of an available resource.
      * :meth:`ResourceQueue.request`: Request a resource for a entity.
      * :meth:`ResourceQueue.start_service: Commence servicing a entity
        at the index position.
    """
    
    def __init__(self, model, name):
        """Instantiates a resourceQueue object.
        
        *Arguments*
            ``model``
                Every :class:`despy.core.component.Component` must be
                assigned to a `despy.core.model.Model`.
            ``name`` (String)
                The name of the resourceQueue.
                
        """
        super().__init__(model, name)
        self._resources = {}
         
    @property
    def num_resources(self):
        """The number of resources added to the resourceQueue object.
        
        The number of resources that have been added to the
        resourceQueue object with the :meth:`.assign_resource` method.
        (Integer)
        """
        return len(self._resources)
    
    def __getitem__(self, index):
        """Allows accessing resource positions with array brackets.
        
        A Python magic method that makes a ResourceQueue object act like an
        array. It allows users to specify a resource position index in
        square brackets on a ResourceQueue object.
        
        *Returns*: :class:`despy.core.resource.ResourceQueue.Resource`
        """
        return self._resources[index]
    
    def __setitem__(self, index, item):
        """Allows setting resource positions with array brackets.
        
        *Arguments*
            ``index``
                An integer ranging from 1 to ``ResourceQueue.capacity``.
                The ``index`` argument is specified inside square
                brackets.
            ``item``
                An instance of
                :class:`despy.core.resource.ResourceQueue.Resource`. The
                ``item`` object is assigned with an equals sign::
                
                    ResourceQueue[index] = item
        
        """
        self._resources[index] = item
        
    def assign_resource(self, resource):
        """Assign a resource to the resourceQueue object.
        
        *Arguments*
            ``resource``
                A :class:`despy.core.resource.Resource object that will
                be appended to the ResourceQueue object.
        """
        index = self.num_resources
        self[index] = resource
        resource._res_queue = self
    
    def get_available_resource(self, random = False):
        """Gets the index number of an available resource.
        
        *Arguments*
            ``random`` (Boolean)
                If set to True, randomly chooses the index of an
                available resource. Otherwise, returns the index of the
                available resource with the lowest index value.
                
        *Returns:* A positive integer representing the index number of
        the resource. ``None`` if all resources are busy.
        
        """
    
        empty_resources = []
        for index in range(self.num_resources):
            if self[index].get_available_station:
                empty_resources.append(index)
        
        if len(empty_resources) == 0:
            return None
        elif not random:
            return empty_resources[0]
        else:
            return empty_resources[randint(0, len(empty_resources) - 1)] 

    def request(self, entity, random = False):
        """Request a resource for a entity.
        
        Checks if a resource position is available. If so, starts
        serving the entity and returns the index of the resource position.
        Otherwise returns False and adds the entity to the resource queue.
        
        *Arguments*
            ``entity``
                The entity that will be serviced by the resource.
                
        *Returns:* If a resource position is available, returns the
        index value of the resource that will serve the entity. Otherwise
        returns False.
        """    
        
        index = self.get_available_resource(random)

        if index is not None:
            #ResourceQueue position is available
            self[index].request(entity, random)
            return index
        else:
            #Resources all busy
            self.add(entity)
            return False         
    

        