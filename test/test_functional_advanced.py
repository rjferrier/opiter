import sys
sys.path.append('..')

from test_functional_common import *
import unittest
import numpy


class TestOptionsDictTreePostprocessing(
        TestOptionsDictTreeIteration):
    
    def setUp(self):
        """
        The scenario here is that I have run my simulations and, for
        each one, computed an error metric.  I want to investigate the
        metric's dependence on mesh resolution.
        """
        TestOptionsDictTreeIteration.setUp(self)
        self.simulation_errors = {
            'sim_1d_10': 0.112,
            'sim_1d_20': 0.053,
            'sim_1d_40': 0.024,
            'sim_1d_80': 0.013,
            'sim_2d_10': 0.124,
            'sim_2d_20': 0.056,
            'sim_2d_40': 0.025,
            'sim_3d_10': 0.129,
            'sim_3d_20': 0.059, }

    def check_convergence(self, postprocess):
        resulting_rates = map(postprocess, self.tree)
        expect_not_applicable = (0, 4, 7)
        for i, result in enumerate(resulting_rates):
            if i in expect_not_applicable:
                self.assertIsNone(result)
            else:
                self.assertAlmostEqual(result, 1., delta=0.1)

    # def test_postprocessing_with_position_strategy(self):
    #     self.check_convergence(
    #         Postprocessor(self.simulation_errors,
    #                       PositionStrategy()))

    # def test_postprocessing_with_lookup_strategy(self):
    #     self.check_convergence(
    #         Postprocessor(self.simulation_errors,
    #                       DictionaryStrategy()))

        
class Postprocessor:
    def __init__(self, simulation_errors, strategy):
        """
        In this contrived example, results of simulations are provided
        directly from the simulation_errors dictionary.  In a
        real-life application, we would need to read and possibly
        postprocess some external results files.
        """
        self.simulation_errors = simulation_errors
        self.strategy = strategy

    @merges_dicts
    def __call__(self, options):
        
        # get the current mesh resolution and error metric
        current_ID = options.str()
        current_res = options['res']
        current_err = self.simulation_errors[current_ID]
        
        # to assess the performance of our simulator, we need to know
        # by how much the error metric reduces between the preceding
        # mesh resolution and the current one (keeping the other
        # options the same).
        try:
            previous_res, previous_err = self.strategy.get_previous_info(
                options, current_err)

            # the performance is given by the convergence rate which is
            # calculated as
            # log(error_difference)/log(resolution_difference)
            return numpy.log(current_error - previous_error) / \
                numpy.log(current_res - previous_res) 

        except NotEnoughInfoException:
            return None
            
        
class NotEnoughInfoException(Exception):
    "Exception class for when we can't compute the convergence rate"
    pass

    
class PositionStrategy:
    def get_previous_info(self, options, current_err):
        pos = options.get_position('res')
        if pos.is_first():
            # if this is the first in a series of mesh resolutions, we
            # can't return anything
            raise NotEnoughInfoException
        else:
            # otherwise, load previous values
            return_res = self.previous_res
            return_err = self.previous_err
        if not pos.is_last():
            # store current values for next time if appropriate
            self.previous_res = options['dx']
            self.previous_err = current_err
        else:
            # for completeness, remove stored values when they are no
            # longer needed
            del(self.previous_res)
            del(self.previous_err)
        return return_res, return_err
        

class DictionaryStrategy:
    # keep a running register of values
    resolutions = {}
    errors = {}
    def get_previous_info(self, options, current_err):
        # register current values for future reference
        current_ID = options.str()
        self.resolutions[current_ID] = options['res']
        self.errors[current_ID] = current_err
        # now try loading the previous values.  If we can't, exit
        # gracefully
        previous_ID = options.str(relative={'res': -1})
        try:
            return self.resolutions[previous_ID], self.errors[previous_ID]
        except KeyError:
            raise NotEnoughInfoException
