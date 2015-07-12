#!/usr/bin/env python3

import unittest
from collections import OrderedDict

import scipy.stats as stats

import despy.core as dp

class testResource(unittest.TestCase):
    def get_rnd_exp(self, user):
        return round(stats.expon.rvs(scale = 4))
    
    def test_resource_init(self):
        print()
        print("TEST RESOURCE INIT OUTPUT")
        model = dp.Model("Resource Test #1")
        server = dp.Resource(model, "Server", 2, self.get_rnd_exp)
        self.assertEqual(server.name, "Server")
        ents = []
        for _ in range(3):
            ents.append(dp.Entity(model, "Entity"))

        #   Verify resource has two positions with keys 1 and 2, and that both
        # are empty (i.e., contain None object).
        self.assertEqual(len(server.stations), 2)
        self.assertEqual(server.capacity, 2)
         
        self.assertTrue(server[0].entity is None)
        self.assertTrue(server[1].entity is None)
        self.assertEqual(server[0].start_time, None)
        self.assertEqual(server[1].start_time, None)
         
        #   Check that entities were created.
        self.assertEqual(ents[0].name, "Entity")
        self.assertEqual(ents[1].name, "Entity")
         
        #   Check get_empty_position()
        position = server.get_available_station()
        self.assertEqual(position, 0)
         
        #   Check request(user)
        position = server.request(ents[0])
        self.assertEqual(position, 0)
        self.assertTrue(server[position].entity is not None)
        self.assertTrue(server[position].start_time is not None)
        self.assertTrue(server[1].entity is None)
         
    class ResModel(dp.Model):
        class Customer(dp.Entity):
            def __init__(self, model):
                super().__init__(model, "Customer")
             
        def initialize(self):
            self.customer_process.start(0, dp.Priority.EARLY)
            super().initialize()
             
        class CustServiceResource(dp.ResourceQueue):
            def __init__(self, model, capacity):
                super().__init__(model, "ServerQueue")
                self.assign_resource(dp.Resource(model, "Server",
                                              capacity,
                                              self.get_service_time))
             
            def get_service_time(self, index):
                return round(stats.expon.rvs(scale = 4))
         
        class CustArrProcess(dp.Process):
            def __init__(self, model, server_resource):
                super().__init__(model, "Customer Generator",
                                 self.generator)
                self.server_resource = server_resource
             
            def generator(self):
                customer = self.model.Customer(self.model)
                args1 = OrderedDict()
                args1["Interarrival_Time"] = None
                args1["Customer"] = customer
                yield self.schedule_timeout("Customer Arrives", 0,
                                            trace_fields = args1)

                while True:
                    self.server_resource.request(customer)
                    delay = round(stats.expon.rvs(scale = 3))
                    customer = self.model.Customer(self.model)
                    args2 = OrderedDict()
                    args2["Interarrival_Time"] = delay                    
                    args2["Customer"] = customer
                    yield self.schedule_timeout("Customer Arrives", delay,
                            trace_fields = args2)
                     
        def __init__(self, name):
            super().__init__(name)
            self.server_resource = self.CustServiceResource(self, 2)
            self.customer_process = self.CustArrProcess(self,
                                                self.server_resource)
     
    def test_resource_in_simulation(self):
        print()
        print("TEST RESOURCE IN SIMULATION OUTPUT")
        self.ResModel.Customer.set_counter()
        model = self.ResModel("Resource Model")
        simulation = model.sim
        simulation.gen.folder_basename = "C:/Projects/despy_output/resource_sim"
        simulation.run(100)
        
if __name__ == '__main__':
    unittest.main()
    