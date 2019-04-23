from .optimizer import optimal_switch_time
from .two_stage_dfba import two_stage_timecourse, one_stage_timecourse
from .fermentation_metrics import *
import numpy as np

objective_dict = {'batch_productivity': batch_productivity,
                  'batch_yield': batch_yield,
                  'batch_titer': batch_end_titer,
                  'dupont_metric': dupont_metric,
                  'linear_combination': linear_combination}


class TwoStageFermentation(object):
    def __init__(self, stage_one_fluxes, stage_two_fluxes, settings):
        self.settings = settings
        self.stage_one_fluxes = stage_one_fluxes
        self.stage_two_fluxes = stage_two_fluxes
        self.initial_concentrations = [self.settings.initial_biomass, self.settings.initial_substrate,
                                       self.settings.initial_product]
        self.time_end = self.settings.time_end
        self.data = []
        self.time = []
        self.optimal_switch_time = None
        self.batch_yield = None
        self.batch_productivity = None
        self.batch_titer = None
        self.dupont_metric = None
        self.linear_combination = None
        self.objective_value = None
        try:
            self.objective = objective_dict[self.settings.objective]
        except KeyError:
            self.objective = objective_dict['batch_productivity']

        self.calculate_fermentation_data()

    def calculate_fermentation_data(self):
        opt_result = optimal_switch_time(self.initial_concentrations, self.time_end,
                                         [self.stage_one_fluxes, self.stage_two_fluxes], self.settings,
                                         self.objective)
        self.optimal_switch_time = opt_result.x[0]
        self.data, self.time = two_stage_timecourse(self.initial_concentrations, self.time_end,
                                                    self.optimal_switch_time,
                                                    [self.stage_one_fluxes, self.stage_two_fluxes],
                                                    num_of_points=self.settings.num_timepoints)
        self.time_end = self.time[-1]
        self.batch_productivity = batch_productivity(self.data, self.time, self.settings)
        self.batch_productivity = self.batch_productivity*(self.batch_productivity > 0)
        self.batch_yield = batch_yield(self.data, self.time, self.settings)
        self.batch_yield = self.batch_yield*(self.batch_yield > 0)
        self.batch_titer = batch_end_titer(self.data, self.time, self.settings)
        self.batch_titer = self.batch_titer*(self.batch_titer > 0)
        self.dupont_metric = dupont_metric(self.data, self.time, self.settings)
        self.linear_combination = linear_combination(self.data, self.time, self.settings)
        try:
            self.objective_value = getattr(self, self.settings.objective)
        except AttributeError:
            self.objective_value = getattr(self, 'batch_productivity')


class OneStageFermentation(object):

    def __init__(self, fluxes, settings):
        self.settings = settings
        self.fluxes = fluxes
        self.initial_concentrations = [self.settings.initial_biomass, self.settings.initial_substrate,
                                       self.settings.initial_product]
        self.time_end = self.settings.time_end
        self.data = []
        self.time = []
        self.batch_yield = None
        self.batch_productivity = None
        self.batch_titer = None
        self.dupont_metric = None
        self.linear_combination = None
        self.objective_value = None
        try:
            self.objective = objective_dict[self.settings.objective]
        except KeyError:
            self.objective = objective_dict['batch_productivity']

        self.calculate_fermentation_data()

    def calculate_fermentation_data(self):
        self.time = np.linspace(0, self.time_end, self.settings.num_timepoints)
        self.data, self.time = one_stage_timecourse(self.initial_concentrations, self.time, self.fluxes)
        self.time_end = self.time[-1]
        self.batch_productivity = batch_productivity(self.data, self.time, self.settings)
        self.batch_yield = batch_yield(self.data, self.time, self.settings)
        self.batch_titer = batch_end_titer(self.data, self.time, self.settings)
        self.dupont_metric = dupont_metric(self.data, self.time, self.settings)
        self.linear_combination = linear_combination(self.data, self.time, self.settings)
        self.objective_value = getattr(self, self.settings.objective)
        try:
            self.objective_value = getattr(self, self.settings.objective)
        except AttributeError:
            self.objective_value = getattr(self, 'batch_productivity')
