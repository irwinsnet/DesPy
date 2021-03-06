#!/usr/bin/env python3
"""
test_despy.py tests the methods in the despy.py module.
===============================================================================
"""

import unittest

import scipy.stats as stats

import despy.dp as dp
from default_config import get_config

class testDespyb(unittest.TestCase):
       
    ### Simulation Class Tests
    def test_now(self):
        # Verify that Simulation.now is set to 0 by default.
        dp.Session.new()
        config = get_config()
        exp1 = dp.Simulation(dp.model.Component("Test"), config)
        cfg = exp1.config
         
        self.assertEqual(exp1.now, 0)
        self.assertFalse(cfg.console_trace)
         
        # Test console_output property.
        cfg.console_trace = False
        self.assertFalse(cfg.console_trace)
        cfg.console_trace = True
        self.assertTrue(cfg.console_trace)
         
        # Verify that Simulation.now can be set by the class constructor.
        dp.Session.new()
        config = get_config()
        exp2 = dp.Simulation(dp.model.Component("Test"), config)
        exp2.config.initial_time = 42
        exp2.initialize()
        self.assertEqual(exp2.now, 42)
          
    ### Model Class Tests
    def test_name(self):
        #Create model with default simulation.
        dp.Session.new()
        config1 = get_config()
        session = dp.Session()
        testModel = dp.model.Component("Test_Model")
        session.model = testModel
        session.sim = dp.Simulation(config = config1)
        self.assertEqual(testModel.name, "Test_Model")
        self.assertIsNotNone(testModel.sim.model)
        self.assertEqual(testModel.sim.model.name, "Test_Model")
          
        # Verify Exception if name is not a string.
        self.assertRaises(TypeError, dp.model.Component, 1)
        self.assertRaises(TypeError, dp.model.Component, None)
          
        # Verify Exception if description is not a string.
        self.assertRaises(TypeError, dp.model.Component,
                          ("Model_Name", None, 365))
          
        #Check simulation.
        session.model = dp.model.Component("Test")
        exp = dp.Simulation()
        session.sim = exp
        self.assertIsInstance(session.sim, dp.Simulation)
          
        # Test description.
        modelDescription = \
        """ This is a test model. It does not have any components.
        It does not simulate any actual system."""
        testModel.description = modelDescription
        self.assertEqual(testModel.description, modelDescription)
          
        # Test component argument type checking.
        self.assertRaises(TypeError, dp.fel.Event, (29, "Event_Name"))
  
    ###Event Scheduling Tests
    def test_peek(self):
        dp.Session.new()
        config1 = get_config()
        session = dp.Session()
        session.model = dp.model.Component("Test_Model_1")
        sim = session.sim = dp.Simulation(config = config1)
          
        self.assertEqual(sim.peek(), float('Infinity'))
          
        sim.schedule(dp.fel.Event("Event_1"),
                       20,
                       dp.EARLY)
        self.assertEqual(sim.peek(), 20)
          
        sim.schedule(dp.fel.Event("Event_2"), 5)
        self.assertEqual(sim.peek(), 5)
          
    def test_step(self):
        #Create model and events.
        dp.Session.new()
        config1 = get_config()
        session = dp.Session()
        model = dp.model.Component("Test_Model_2")
        session.model = model
        session.sim = sim_ts = dp.Simulation(config = config1)
        sim_ts.initialize()
        sim_ts._setup()
        ev_early = dp.fel.Event("Early_Event")
        ev_standard = dp.fel.Event("Standard_Event")
        ev_late = dp.fel.Event("Late_Event")
          
        #Schedule Events
        sim_ts.schedule(ev_late, 5, dp.LATE)  
        model.sim.schedule(ev_early, 5, dp.EARLY)  
        model.sim.schedule(ev_standard, 5, dp.STANDARD)
          
        #Verify events run in correct order.
        print()
        felItem = model.sim._step()
        self.assertEqual(felItem.event.name, "Early_Event")
        felItem = model.sim._step()
        self.assertEqual(felItem.event.name, "Standard_Event")
        felItem = model.sim._step()
        self.assertEqual(felItem.event.name, "Late_Event")
        exp = model.sim
        self.assertEqual(exp.now, 5)
  
    def test_run(self):
        dp.Session.new()
        config1 = get_config()
        session = dp.Session()
        session.config = config1
        model = dp.model.Component("RunTest_Model")
        session.model = model
        session.sim = sim = dp.Simulation()
        model.sim.schedule(dp.fel.Event("First_Event"), 0)
        sim.schedule(dp.fel.Event("Second_Event"), 4)
        sim.schedule(dp.fel.Event("Third_Event"), 8)
        model.sim.initialize()
        model.sim.run()
        results = model.sim.finalize()
          
        self.assertEqual(results.trace.length, 3)
        evtTrace = results.trace
        self.assertEqual(evtTrace[0]['name'], "First_Event")
        self.assertEqual(evtTrace[1]['name'], "Second_Event")
        self.assertEqual(evtTrace[1]['time'], 4)
        self.assertEqual(evtTrace[2]['name'], "Third_Event")
        self.assertEqual(evtTrace[2]['time'], 8)
          
    class AppendCallbackModel(dp.model.Component):
        def __init__(self, name):
            super().__init__(name)
            self.evt1 = dp.fel.Event("First_Event")
            self.evt1.append_callback(self.evt1_callback)
          
        def setup(self):
            self.sim.schedule(self.evt1, 5)
              
        def evt1_callback(self):
            evt2 = dp.fel.Event("Callback_Event")
            self.sim.schedule(evt2, 10)
  
    def test_appendCallback(self):
        session = dp.Session.new()
        config1 = get_config()
        session.config = config1     
        model = self.AppendCallbackModel("AppendCallback_Model")
        session.model = model
 
        cfg = session.config
        self.assertEqual(cfg, config1)
        session.sim = sim_tc = dp.Simulation()
        cfg.folder_basename = ("C:/Projects/despy_output/"
                                        "append_callback1")
        self.assertEqual(cfg.write_files,
                         get_config().write_files)
        sim_tc.initialize()
        sim_tc.run()
        results = sim_tc.finalize()
        results.write_files()
          
        evtTrace = results.trace
        self.assertEqual(evtTrace.length, 2)
        self.assertEqual(evtTrace[0]['name'], "First_Event")
        self.assertEqual(evtTrace[0]['time'], 5)
        self.assertEqual(evtTrace[1]['name'], "Callback_Event")
        self.assertEqual(evtTrace[1]['time'], 15)
           
        #Test initialize method and until parameter
        model.sim.reset()
        self.assertEqual(sim_tc.results.trace.length, 0)
        cfg.folder_basename = \
                "C:/Projects/despy_output/append_callback2"
        self.assertEqual(session.config.folder_basename,
                         "C:/Projects/despy_output/append_callback2")
        model.sim.initialize()
        model.sim.run(10)
        evtTrace = model.sim.results.trace
        self.assertEqual(evtTrace.length, 1)
            
        #Verify that simulation can be restarted from current point.
        results = model.sim.runf(20)
        self.assertEqual(results.trace.length, 2)
        results.write_files()
          
    def test_process(self):
        session = dp.Session.new()
        config1 = get_config()
        session.config = config1
        model = dp.model.Component("Process_Model")
          
        def generator(self):
            while True:
                delay = round(stats.expon.rvs(scale = 3))
                yield self.schedule_timeout("Repeated_Event", delay)
          
        process = dp.model.Process("Test_Process", generator)
                   
        model.add_component(process)
        self.assertEqual(len(model.components), 1)
        session.model = model
        _ = dp.Simulation()
        session.config.seed = 42
        process.start()
        model.sim.initialize()
        model.sim.runf(20)
          
    def test_simultaneous_events(self):
        #Test simultaneous, different events.
        config1 = get_config()
        dp.Session.new(config1)
        model = dp.model.Component("Simultaneous_Events_Model")
          
        def setup(self):
            self.sim.schedule(dp.fel.Event("Event_1"), 3)
            self.sim.schedule(dp.fel.Event("Event_2"), 3)
        model.setup = setup
         
        session = dp.Session() 
        session.model = model
        session.sim = sim = dp.Simulation()
        sim.initialize()        
        sim.run()
        results = sim.finalize()
        self.assertEqual(results.trace.length, 2)
          
        #Test simultaneous, identical events.
        model2 = dp.model.Component("Simultaneous_Identical_Events_Model")
        session.model = model2
        sim = session.sim = dp.Simulation()
        event = dp.fel.Event("The_Event")
        model2.sim.schedule(event, 1)
        sim.schedule(event, 1)
        sim.initialize()
        results = sim.runf()
        self.assertEqual(results.trace.length, 2)
         
    def test_trace_control(self):
        config1 = get_config()
        dp.Session.new(config1)
        model = dp.model.Component("Trace_Control")
        session = dp.Session()
        session.model = model
        session.sim = sim = dp.Simulation()
        event = dp.fel.Event("Trace_Control_Event")
         
        def event_callback(self):
            self.sim.schedule(event, 10)
             
        event.append_callback(event_callback)
        sim.schedule(event, 0)
         
        # Default settings limit trace to time < 500
        sim.initialize()
        sim.run(1000)
        results = sim.finalize()
        self.assertEqual(results.trace.length, 50)
          
        # User can set trace start and stop times
        sim.reset()
        sim.schedule(event, 0)
         
        session.config.trace_start = 200
        session.config.trace_stop = 300
         
        sim.console_output = False
        sim.initialize()
        sim.run(1000)
        results = sim.finalize()
        self.assertEqual(results.trace.length, 10)
        self.assertEqual(results.trace[0]['time'], 200)
        self.assertEqual(results.trace[9]['time'], 290)
         
        # Default maximum trace length is 1000 lines.
        sim.reset()     
        evt2 = dp.fel.Event("Trace_Control_Event_Step_is1")
          
        def event_callback2(self):
            self.sim.schedule(evt2, 1)
          
        evt2.append_callback(event_callback2)
        model.sim.schedule(evt2, 0)
        session.config.trace_start = 0
        session.config.trace_stop = 1000
        model.sim.initialize()
        model.sim.run(5000)
        results = model.sim.finalize()
        self.assertEqual(results.trace.length, 1000)
          
        # User can set maximum trace length
        sim.name = "bigTrace"
        sim.reset()
        session.config.folder_basename = \
                "C:/Projects/despy_output/trace_control"
        sim.schedule(evt2, 0)
        session.config.trace_max_length = 2000
        session.config.trace_start = 365
        session.config.trace_stop = 2999
        sim.initialize()
        sim.run(3000)
        results = model.sim.finalize()
        results.write_files()
        self.assertEqual(results.trace.length, 2000)
        self.assertEqual(results.trace[0]['time'], 365)
        self.assertEqual(results.trace[1999]['time'], 2364)

if __name__ == '__main__':
    unittest.main()

