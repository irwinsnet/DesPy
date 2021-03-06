#!/usr/bin/env python3
"""
test_core_queue.py tests queue performance.
===============================================================================
"""

import unittest
import types

import scipy.stats as stats

import despy.dp as dp

class SubClassModel(dp.model.Component):
    def initialize(self):
        pass

class testQueue(unittest.TestCase):
    
    def test_simple_model_subclass(self):
        print()
        print("=====Testing Plain Model=====")
        pm_name = "Plain_Model"
        pm_description = "Verifying plain model attributes."
        p_model = dp.model.Component(pm_name, description = pm_description)
        self.assertEqual(p_model.name, pm_name)
        self.assertEqual(p_model.description, pm_description)
        self.assertIsInstance(p_model.initialize,
                              types.MethodType)
        
        self.assertEqual(len(p_model.components), 0)
        
        print()
        print("=====Testing Subclassed Model=====")
        scm_name = "Subclassed_Model"
        scm_description = "Verifying subclassed model attributes."
        sc_model = SubClassModel(scm_name,
                                          description = scm_description)
        self.assertEqual(sc_model.name, scm_name)
        self.assertEqual(sc_model.description, scm_description)
        
        self.assertIsInstance(sc_model.initialize, types.MethodType)
        self.assertEqual(len(sc_model.components), 0)

        print()
        print("=====Testing Queue Model=====")
        q_name = "Queued_Model"
        q_description = "Verifying Complex Queued Model attributes"
        q_model = QModel(q_name, q_description)
        self.assertEqual(q_model.name, q_name)
        self.assertEqual(q_model.description, q_description)
        self.assertIsInstance(q_model.initialize, types.MethodType)
        self.assertEqual(len(q_model.components), 3)
        print(q_model.components)
        
        session = dp.Session.new()
        session.model = q_model
        session.sim = sim = dp.Simulation()
        session.config.folder_basename = "C:/Projects/despy_output/queue_sim"
        sim.irunf(100).write_files()
        
        
class QModel(dp.model.Component):
    def __init__(self, name, description):
        super().__init__(name, description)
        self.add_component(dp.model.Queue("c_q"))
        self.add_component(CustServiceProcess())
        self.add_component(CustArrProcess())
        
    def initialize(self):
        self.customer_process.start(0, dp.EARLY)
        self.service_process.start()
       
        
class Customer(dp.model.Entity):
    def __init__(self):
        super().__init__("Customer")
      
        
class CustArrProcess(dp.model.Process):
    def __init__(self):
        super().__init__("customer_process", self.generator)

    def generator(self):
        first_customer = Customer()
        self.owner.c_q.add(first_customer)                
        yield self.schedule_timeout(\
                "Customer_{0}__arrives".format(first_customer.number))
        while True:
            delay = round(stats.expon.rvs(scale = 3))
            customer = Customer()                    
            yield self.schedule_timeout(\
                    "Customer_{0}__arrives".format(customer.number),
                    delay)
            self.owner.c_q.add(customer)
            self.owner.service_process.wake()


class CustServiceProcess(dp.model.Process):
    def __init__(self):
        super().__init__("service_process", self.generator)
        
    def generator(self):
        while True:
            if self.owner.c_q.length > 0:
                customer = self.owner.c_q.remove()
                delay = round(stats.expon.rvs(scale = 4))
                yield self.schedule_timeout(\
                        "Finished_serving_customer_{0}__"
                        "Service_time_is{1}".format(customer.number,
                                                   delay),
                        delay)
            else:
                yield self.sleep()


if __name__ == '__main__':
    unittest.main()

