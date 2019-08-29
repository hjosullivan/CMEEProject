#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" models.py contains all available mathematical models to be fitted to thermal performance curves.

NOTE: Currently only Sharpe-Schoolfield variants """

import numpy as np
from lmfit import minimize, Minimizer, Parameters

class ThermalModelsException(Exception):
    """ General purpose exception generator for ThermalModels"""

    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return "{}".format(self.msg)

class ThermalModels(object):
    """ Class containing thermal models for fitting """
    # Set some useful class variables
    # Bolzmann's constant
    k = 8.617 * 10 ** (-5)

    # Reference temperature (20 degrees C)
    Tref = 283.15

    # Set some useful error messages
    _err_novals = ("Please supply input data for model fitting.")

    _err_nonparam = ("Supplied parameters must be an instance of lmfit.parameter.Parameter or tpcfit.starting_parameters.StartParams")

    _err_temperror = ("Temperature vector must be of type numpy.ndarray.")

    _err_traiterror = ("Trait vector must be of type numpy.ndarray.")

    _err_zero_neg_vals = ("Zero or negative values not accepted. Please supply positive values only.")


    def __init__(self, temps=None, traits=None, fit_pars=None):
        if temps is not None:
            self.temps = temps
            if not isinstance(temps, np.ndarray):
                raise ThermalModelsException(self._err_temperror)
            if self.temps is None:
                raise ThermalModelsException(self._err_novals)
            elif np.min(self.temps) < 0:
                raise ThermalModelsException(self._err_temperror)

        if traits is not None:
            self.traits = traits
            if not isinstance(traits, np.ndarray):
                raise ThermalModelsException(self._err_traiterror)
            if self.traits is None:
                raise ThermalModelsException(self._err_novals)
            elif np.min(self.traits) < 0:
                raise ThermalModelsException(self._err_traiterror)

        if fit_pars is not None:
            self.fit_pars = fit_pars
        if not isinstance(fit_pars, Parameters):
            self.fit_pars = self.fit_pars.gauss_params
            #raise ThermalModelsException(self._err_nonparam)
        elif self.fit_pars is None:
            raise ThermalModelsException(self._err_novals)

    @classmethod
    def set_Tref(cls, Tref_val):
        """ Allow user to set their own reference temperature """
        cls.Tref = Tref_val

class SharpeSchoolfieldFull(ThermalModels):

    model_name = "sharpeschoolfull"

    def __init__(self, temps, traits, fit_pars):
        super().__init__(temps, traits, fit_pars)
        self.ssf_model = self.fit_ssf(temps, traits, fit_pars)
        if self.ssf_model is not None:
            # Return fitted trait values
            self.ssf_fits = self.ssf_fitted_vals(self.ssf_model)
            # Return parameter estimates from the model
            self.final_estimates = self.ssf_estimates(self.ssf_model)
            # Return initial parameter values supplied to the model
            self.initial_params = self.ssf_init_params(self.ssf_model)
            # Return AIC score
            self.AIC = self.ssf_aic(self.ssf_model)

    def ssf_fcn2min(self, temps, traits, fit_pars):
        """ Function to be minimized

        Parameters
        ----------
        temps: numpy array
            Temperature array in Kelvin
        traits: numpy array
            Trait array
        params: lmfit.parameter.Parameters
            Dictionary of parameters to fit full schoolfield model

        Returns
        -------
        ssf_fcn2min: callable
            Fitting function to be called by the optimizer - producing an array of residuals (difference between model and data)

        """

        # Set parameter values
        B0 = self.fit_pars["B0"].value
        E = self.fit_pars["E"].value
        Eh = self.fit_pars["Eh"].value
        El = self.fit_pars["El"].value
        Th = self.fit_pars["Th"].value
        Tl = self.fit_pars["Tl"].value

        # Eh must be greater than Eh
        if E >= Eh:
            return 1e10

        # TH must be greater than Tl
        if Th < (Tl + 1):
            Th = Tl + 1

        # And Tl must be less than Th
        if Tl > Th - 1:
            Tl = Th - 1

        model = np.log((B0 * np.exp(1)**((-E / self.k) * ((1 / self.temps) - (1 / self.Tref)))) / ((1 + (np.exp(1)**((El / self.k) * ((1 / Tl) - (1 / self.temps))))) + (np.exp(1)**((Eh / self.k) * ((1 / Th) - (1 / self.temps))))))

        # Return residual array
        return np.array(np.exp(model) - self.traits)

    def ssf_fitted_vals(self, ssf_model):
        """ Called by a fit model only: A function to estimate the trait value at a given temperature according
        to the Sharpe-Schoolfield model

        Parameters
        ----------
        ssf_model: lmfit.MinimizerResult
            Minimizer result of a successful fit

        Returns
        -------
        ssf_fits: numpy array
            Fitted trait values

        """

        # Get best-fit model parameters
        B0 = self.ssf_model.params["B0"].value
        E = self.ssf_model.params["E"].value
        Eh = self.ssf_model.params["Eh"].value
        El = self.ssf_model.params["El"].value
        Th = self.ssf_model.params["Th"].value
        Tl = self.ssf_model.params["Tl"].value

        # Define model
        model = np.log((B0 * np.exp(1)**((-E / self.k) * ((1 / self.temps) - (1 / self.Tref)))) / ((1 + (np.exp(1)**((El / self.k) * ((1 / Tl) - (1 / self.temps))))) + (np.exp(1)**((Eh / self.k) * ((1 / Th) - (1 / self.temps))))))

        # Get untransformed fitted values
        self.ssf_fits = np.array(np.exp(model))

        return self.ssf_fits

    def fit_ssf(self, temps, traits, fit_pars):
        """ Fitting function for schoolfield full model

        Parameters
        ----------
        fcn2min: callable
            function to be minimized by the optimizer
        params: Parameter object
            Dictionary of parameters to fit full schoolfield model
        temps: numpy array
            Temperature array in Kelvin
        traits: numpy array
            Trait array

        Returns
        -------
        ssf_model: lmfit.MinimizerResult
            Model result object
        """

        # Log trait values
        self.traits = np.log(self.traits)

        # Minimize model
        try:
            self.ssf_model = minimize(self.ssf_fcn2min, self.fit_pars, args=(self.temps, self.traits), xtol = 1e-12, ftol = 1e-12, maxfev = 100000)
        except Exception:
            return None

        return self.ssf_model

    def ssf_estimates(self, ssf_model):
        """ Get parameter estimtes from the model
        Parameters
        ----------
        ssf_model : lmfit.MinimizerResult
            A successful model result

        Returns
        -------
        final_estimates: dict
            Dictionary of final fitted parameters from the model
        """

        self.final_estimates = self.ssf_model.params.valuesdict()
        return self.final_estimates

    def ssf_init_params(self, ssf_model):
        """ Get parameter estimtes from the model
        Parameters
        ----------
        ssf_model : lmfit.MinimizerResult
            A successful model result

        Returns
        -------
        initial_params: dict
            Dictionary of initial parameters supplied to the model
        """

        self.initial_params = self.ssf_model.init_values
        return self.initial_params

    def ssf_aic(self,ssf_model):
        """ Get model AIC score
        Parameters
        ----------
        ssf_model : lmfit.MinimizerResult
            A successful model result

        Returns
        -------
        AIC: int
            AIC score from fitted model
        """
        self.AIC = self.ssf_model.aic
        return self.AIC

        def __repr__(self):
            pass

        # readable representation of the object (for user)
        def __str__(self):
            pass

class SharpeSchoolfieldHigh(ThermalModels):

    model_name = "sharpeschoolhigh"

    def __init__(self, temps, traits, fit_pars):
        super().__init__(temps, traits, fit_pars)
        self.ssh_model = self.fit_ssh(temps, traits, fit_pars)
        if self.ssh_model is not None:
            # Return fitted trait values
            self.ssh_fits = self.ssh_fitted_vals(self.ssh_model)
            # Return parameter estimates from the model
            self.final_estimates = self.ssh_estimates(self.ssh_model)
            # Return initial parameter values supplied to the model
            self.initial_params = self.ssh_init_params(self.ssh_model)
            # Return AIC score
            self.AIC = self.ssh_aic(self.ssh_model)

    def ssh_fcn2min(self, temps, traits, fit_pars):
        """ Function to be minimized

        Parameters
        ----------
        temps: numpy array
            Temperature array in Kelvin
        traits: numpy array
            Trait array
        params: lmfit.parameter.Parameters
            Dictionary of parameters to fit full schoolfield model

        Returns
        -------
        ssh_fcn2min: callable
            Fitting function to be called by the optimizer - producing an array of residuals (difference between model and data)

        """

        # Set parameter values
        B0 = self.fit_pars["B0"].value
        E = self.fit_pars["E"].value
        Eh = self.fit_pars["Eh"].value
        Th = self.fit_pars["Th"].value

        # Eh must be greater than Eh
        if E >= Eh:
            return 1e10

        model = np.log((B0 * np.exp(1)**((-E / self.k) * ((1 / self.temps) - (1 / self.Tref)))) / (1 + (np.exp(1)**((Eh / self.k) * ((1 / Th) - (1 / self.temps))))))

        # Return residual array
        return np.array(np.exp(model) - self.traits)

    def ssf_fitted_vals(self, ssh_model):
        """ Called by a fit model only: A function to estimate the trait value at a given temperature.
        Parameters
        ----------
        ssf_model: lmfit.MinimizerResult
            Minimizer result of a successful fit

        Returns
        -------
        ssh_fits: numpy array
            Fitted trait values

        """

        # Get best-fit model parameters
        B0 = self.ssh_model.params["B0"].value
        E = self.ssh_model.params["E"].value
        Eh = self.ssh_model.params["Eh"].value
        Th = self.ssh_model.params["Th"].value

        # Define model
        model = np.log((B0 * np.exp(1)**((-E / self.k) * ((1 / self.temps) - (1 / self.Tref)))) / (1 + (np.exp(1)**((Eh / self.k) * ((1 / Th) - (1 / self.temps))))))

        # Get untransformed fitted values
        self.ssh_fits = np.array(np.exp(model))

        return self.ssh_fits

    def fit_ssh(self, temps, traits, fit_pars):
        """ Fitting function for schoolfield full model

        Parameters
        ----------
        fcn2min: callable
            function to be minimized by the optimizer
        params: Parameter object
            Dictionary of parameters to fit full schoolfield model
        temps: numpy array
            Temperature array in Kelvin
        traits: numpy array
            Trait array

        Returns
        -------
        ssf_model: lmfit.MinimizerResult
            Model result object
        """

        # Log trait values
        self.traits = np.log(self.traits)

        # Minimize model
        try:
            self.ssh_model = minimize(self.ssh_fcn2min, self.fit_pars, args=(self.temps, self.traits), xtol = 1e-12, ftol = 1e-12, maxfev = 100000)
        except Exception:
            return None

        return self.ssh_model

    def ssh_estimates(self, ssh_model):
        """ Get parameter estimtes from the model
        Parameters
        ----------
        ssh_model : lmfit.MinimizerResult
            A successful model result

        Returns
        -------
        final_estimates: dict
            Dictionary of final fitted parameters from the model
        """

        self.final_estimates = self.ssh_model.params.valuesdict()
        return self.final_estimates

    def ssf_init_params(self, ssf_model):
        """ Get parameter estimtes from the model
        Parameters
        ----------
        ssf_model : lmfit.MinimizerResult
            A successful model result

        Returns
        -------
        initial_params: dict
            Dictionary of initial parameters supplied to the model
        """

        self.initial_params = self.ssh_model.init_values
        return self.initial_params

    def ssf_aic(self, ssh_model):
        """ Get model AIC score
        Parameters
        ----------
        ssf_model : lmfit.MinimizerResult
            A successful model result

        Returns
        -------
        AIC: int
            AIC score from fitted model
        """
        self.AIC = self.ssh_model.aic
        return self.AIC

        def __repr__(self):
            pass

        # readable representation of the object (for user)
        def __str__(self):
            pass

class SharpeSchoolfieldlow(ThermalModels):

    model_name = "sharpeschoollow"

    def __init__(self, temps, traits, fit_pars):
        super().__init__(temps, traits, fit_pars)
        self.ssl_model = self.fit_ssh(temps, traits, fit_pars)
        if self.ssl_model is not None:
            # Return fitted trait values
            self.ssl_fits = self.ssl_fitted_vals(self.ssl_model)
            # Return parameter estimates from the model
            self.final_estimates = self.ssl_estimates(self.ssl_model)
            # Return initial parameter values supplied to the model
            self.initial_params = self.ssl_init_params(self.ssl_model)
            # Return AIC score
            self.AIC = self.ssh_aic(self.ssl_model)

    def ssl_fcn2min(self, temps, traits, fit_pars):
        """ Function to be minimized

        Parameters
        ----------
        temps: numpy array
            Temperature array in Kelvin
        traits: numpy array
            Trait array
        params: lmfit.parameter.Parameters
            Dictionary of parameters to fit full schoolfield model

        Returns
        -------
        ssl_fcn2min: callable
            Fitting function to be called by the optimizer - producing an array of residuals (difference between model and data)

        """

        # Set parameter values
        B0 = self.fit_pars["B0"].value
        E = self.fit_pars["E"].value
        El = self.fit_pars["Eh"].value
        Tl = self.fit_pars["Th"].value

        model = np.log((B0 * np.exp(1)**((-E / self.k) * ((1 / self.temps) - (1 / self.Tref)))) / (1 + (np.exp(1)**((El / self.k) * ((1 / Tl) - (1 / self.temps))))))

        # Return residual array
        return np.array(np.exp(model) - self.traits)

    def ssf_fitted_vals(self, ssl_model):
        """ Called by a fit model only: A function to estimate the trait value at a given temperature.
        Parameters
        ----------
        ssl_model: lmfit.MinimizerResult
            Minimizer result of a successful fit

        Returns
        -------
        ssl_fits: numpy array
            Fitted trait values

        """

        # Get best-fit model parameters
        B0 = self.ssh_model.params["B0"].value
        E = self.ssh_model.params["E"].value
        El = self.ssh_model.params["Eh"].value
        Tl = self.ssh_model.params["Th"].value

        # Define model
        model = np.log((B0 * np.exp(1)**((-E / self.k) * ((1 / self.temps) - (1 / self.Tref)))) / (1 + (np.exp(1)**((El / self.k) * ((1 / Tl) - (1 / self.temps))))))

        # Get untransformed fitted values
        self.ssh_fits = np.array(np.exp(model))

        return self.ssl_fits

    def fit_ssh(self, temps, traits, fit_pars):
        """ Fitting function for schoolfield full model

        Parameters
        ----------
        fcn2min: callable
            function to be minimized by the optimizer
        params: Parameter object
            Dictionary of parameters to fit full schoolfield model
        temps: numpy array
            Temperature array in Kelvin
        traits: numpy array
            Trait array

        Returns
        -------
        ssl_model: lmfit.MinimizerResult
            Model result object
        """

        # Log trait values
        self.traits = np.log(self.traits)

        # Minimize model
        try:
            self.ssl_model = minimize(self.ssl_fcn2min, self.fit_pars, args=(self.temps, self.traits), xtol = 1e-12, ftol = 1e-12, maxfev = 100000)
        except Exception:
            return None

        return self.ssl_model

    def ssh_estimates(self, ssl_model):
        """ Get parameter estimtes from the model
        Parameters
        ----------
        ssh_model : lmfit.MinimizerResult
            A successful model result

        Returns
        -------
        final_estimates: dict
            Dictionary of final fitted parameters from the model
        """

        self.final_estimates = self.ssl_model.params.valuesdict()
        return self.final_estimates

    def ssf_init_params(self, ssl_model):
        """ Get parameter estimtes from the model
        Parameters
        ----------
        ssl_model : lmfit.MinimizerResult
            A successful model result

        Returns
        -------
        initial_params: dict
            Dictionary of initial parameters supplied to the model
        """

        self.initial_params = self.ssl_model.init_values
        return self.initial_params

    def ssf_aic(self, ssl_model):
        """ Get model AIC score
        Parameters
        ----------
        ssl_model : lmfit.MinimizerResult
            A successful model result

        Returns
        -------
        AIC: int
            AIC score from fitted model
        """
        self.AIC = self.ssl_model.aic
        return self.AIC

        def __repr__(self):
            pass

        # readable representation of the object (for user)
        def __str__(self):
            pass
