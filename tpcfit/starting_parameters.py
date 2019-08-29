#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" starting_parameters.py is a wrapper around lmfit.Parameters, allowing the user to randomise starting parameters for minimization.

The user supplies upper and lower parameter bounds within which parameters will be are randomly sampled via a truncated gaussian distribution."""

import numpy as np
from scipy.stats import truncnorm
from lmfit import Parameter, Parameters
# Probably fix this in the future...
np.seterr(divide='ignore', invalid='ignore')

class StartParamsException(Exception):
    """ General purpose exception generator for StartParams"""

    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return "{}".format(self.msg)

class StartParams(object):
    """ Get random starting parameters for minimization """

    # Set some useful error messages
    _err_nonparam = ("init_params must be a minimizer.Parameters() instance")

    _err_boundmatch = ("init_params keys must be identifical to init_bounds keys. Please supply identical keys.")

    _err_outbounds = ("init_bounds must have the format {param:[low:upp]}. Please ensure that bound lists contain only two values.")

    _err_lowupp = ("The first value in your parameter bound list must be lower than the second value. E.g. {param_E:[0.1:0.9]}")

    # initialise class with parameters and dictionary of bounds
    def __init__(self, init_params=None, init_bounds=None):
        """
        Parameters
        ----------
        init_params: lmfit.parameter.Parameters
            Contains parameters for the model
        init_bounds: dict, optional
            keyword arguments to set bounds for parameter sampling.

        """
        if init_params is not None:
            self.init_params = init_params
        if not isinstance(init_params, Parameters):
            raise StartParamsException(self._err_nonparam)
        elif self.init_params is None:
            raise StartParamsException(self._err_nonparam)
        self.init_bounds = init_bounds
        if self.init_bounds is None:
            self.init_bounds = {}
        self.gauss_params = self.gauss_params(init_params, init_bounds)

    # def __setitem__(self, gauss_params, param):
    #       self._gauss_params[param] = param
    # def __getitem__(self, gauss_params):
    #      return self.gauss_params[param]

    def __getitem__(self, key):
        return self.gauss_params[key]

    def trunc_norm(self, mean=None, sd=None, low=None, upp=None):
        """ Function to caluclate a truncated gaussian distribution

        Parameters
        ----------
        low: None
            upper parameter bound
        upp: None
            upper parameter bound

        Returns
        -------
        func: callable
            function to generate truncated gaussian distribution

        """
        if mean is not None:
            mean=mean
        if sd is not None:
            sd=sd
        if low is not None:
            low=low
        if upp is not None:
            upp=upp

        return truncnorm(
        (low-self.mean) / self.sd, (upp-self.mean) / self.sd, loc=self.mean, scale=self.sd
        )

    def gauss_params(self, init_params, init_bounds):
        """ Generate new starting parameters from a truncated gaussian distrution

        Parameters
        ----------
        init_params: lmfit.parameter.Parameters object
            Parameter object containing names, values and constraints

        init_bounds: keyword arguments
            A dictionary of parameter names as keys with a list of upper and lower bounds as values. E.g. {"E": [0.25, 0.85]}. Keys in params must match keys in init_bounds

        Returns
        -------
        gauss_params: lmfit.parameter.Parameters object
            New parameters object with updated values
        """
        # Check that keys are identical
        if set(self.init_params.keys()) == set(self.init_bounds.keys()):
            next
        else:
            raise StartParamsException(self._err_boundmatch)

        ## Generate random value from truncated gaussian distribution ##

        # Assign empty dictionary for new values
        d = {}
        for key, val in self.init_bounds.items():
            # Ensure param has a list of 2 [low, upp]
            if len(val) is not 2:
                raise StartParamsException(self._err_outbounds)
            # Ensure the first value (low) is less than the second value (upp)
            elif val[0] > val[1]:
                raise StartParamsException(self._err_lowupp)
            else:
                low, upp = val[0], val[1]
                val_array = np.array(val)
                # Calculate mean and standard deviation
                self.mean, self.sd = np.mean(val_array), np.std(val_array)

                # Apply trunc_norm function
                new_val = self.trunc_norm(mean=self.mean, sd=self.sd, low=low, upp=upp)
                val = new_val.rvs()
                d[key] = val

                # Update parameter values with values in d
                for i in self.init_params.items():
                    # Get Parameter object out of Parameters object (confusing I know.)
                    par = (i[1])
                    # Add new value
                    for k, v in d.items():
                        if par.name == k:
                            par.value = v

        self.gauss_params = self.init_params
        return self.gauss_params

    # unambigious representation of the object (for devs)
    # should be able to recreate the object
    def __repr__(self):
        return "StartParams('{}', '{}')".format(self.init_params, self.init_bounds)

    # readable representation of the object (for user)
    def __str__(self):
        return "New Paramaters: '{}', '{}'".format(self.gauss_params.keys(), self.gauss_params.values())
