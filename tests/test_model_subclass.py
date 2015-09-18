#!/usr/bin/env python3
"""
test_core_queue.py tests queue performance.
===============================================================================
"""

import unittest
import types

import scipy.stats as stats

import despy.core as dp

class SubClassModel(dp.Model):
    def initialize(self):
        pass

class testQueue(unittest.TestCase):
    
    def test_simple_model_subclass(self):
        print()
        print("=====Testing Plain Model=====")
        pm_name = "Plain Model"
        pm_description = "Verifyin plain model attributes."
        p_model = dp.Model(pm_name, description = pm_description)
        self.assertEqual(p_model.name, pm_name)
        self.assertEqual(p_model.description, pm_description)
        self.assertIsInstance(p_model.initialize,
                              types.MethodType)
        
        self.assertFalse(p_model.initial_events_scheduled)
        self.assertEqual(len(p_model), 0)
        
        print()
        print("=====Testing Subclassed Model=====")
        scm_name = "Subclassed Model"
        scm_description = "Verifying subclassed model attributes."
        sc_model = SubClassModel(scm_name,
                                          description = scm_description)
        self.assertEqual(sc_model.name, scm_name)
        self.assertEqual(sc_model.description, scm_description)
        
        self.assertIsInstance(sc_model.initialize, types.MethodType)
        self.assertFalse(sc_model.initial_events_scheduled)
        self.assertEqual(len(sc_model), 0)

        print()
        print("=====Testing Queue Model=====")
        q_name = "Queued Model"
        q_description = "Verifying Complex Queued Model attributes"
        q_model = QModel(q_name, q_description)
        self.assertEqual(q_model.name, q_name)
        self.assertEqual(q_model.description, q_description)
        self.assertIsInstance(q_model.initialize, types.MethodType)
        self.assertFalse(q_model.initial_events_scheduled)
        self.assertEqual(len(q_model), 3)
        print(q_model.components)
        
        sim = dp.Simulation(model = q_model)
        sim.gen.folder_basename = "C:/Projects/despy_output/queue_sim"
        sim.run(100)
        
        
class QModel(dp.Model):
    def __init__(self, name, description):
        super().__init__(name, description)
        self["c_q"] = dp.Queue(self, "Customer Queue")
        self["service_process"] = CustServiceProcess(self)
        self["customer_process"] = CustArrProcess(self)
        
    def initialize(self):
        print("Initializing QuModel")
        self["customer_process"].start(0, dp.Priority.EARLY)
        self["service_process"].start()
        print("QuModel Components: {}".format(self.components))  
        
        
class Customer(dp.Entity):
    def __init__(self, model):
        super().__init__(model, "Customer")
      
        
class CustArrProcess(dp.Process):
    def __init__(self, model):
        super().__init__(model, "Customer Generator", self.generator)

    def generator(self):
        first_customer = Customer(self.mod)
        self.mod["c_q"].add(first_customer)                
        yield self.schedule_timeout(\
                "Customer #{0} arrives.".format(first_customer.number))
        while True:
            delay = round(stats.expon.rvs(scale = 3))
            customer = Customer(self.mod)                    
            yield self.schedule_timeout(\
                    "Customer #{0} arrives.".format(customer.number),
                    delay)
            self.mod["c_q"].add(customer)
            self.mod["service_process"].wake()


class CustServiceProcess(dp.Process):
    def __init__(self, model):
        super().__init__(model, "Customer Server", self.generator)
        
    def generator(self):
        while True:
            if self.mod["c_q"].length > 0:
                customer = self.mod["c_q"].remove()
                delay = round(stats.expon.rvs(scale = 4))
                yield self.schedule_timeout(\
                        "Finished serving customer #{0}, "
                        "Service time: {1}".format(customer.number,
                                                   delay),
                        delay)
            else:
                yield self.sleep()


if __name__ == '__main__':
    unittest.main()
