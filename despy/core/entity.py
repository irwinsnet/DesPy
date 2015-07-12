#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
*****************
despy.core.entity
*****************
   
..  autosummary::

    Entity
    
..  todo

    Add data fields to track and report number of entities created.
    
    Add a dictionary object so designers can add custom data fields
    without sub-classing.
"""

from despy.core.component import Component

class Entity(Component):
    """Represents a real world object that moves through a system.
    
    **Inherited Classes**
      * :class:`despy.base.named_object.NamedObject`
      * :class:`despy.core.component.Component`
    """
    
    def __init__(self, model, name, description = None):
        """Create an entity object.
        
        *Arguments*
            ``model`` (:class:`despy.core.model.Model`)
                The model that represents the system that the entity
                belongs to.
            ``name`` (String)
                A descriptive short name that will appear in the trace
                and output reports.
            ``description`` (String)
                A descriptive paragraph. Optional.
        """
        
        super().__init__(model, name, description)