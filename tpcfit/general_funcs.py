#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" general_funcs.py contains a number of useful functions for fitting thermal performance curves. Functions related to data cleaning can be found in the directory 'useful scripts'

NOTE: Resampling methods are included here to avoid multiple inheritance for now. This will be updated as soon as my sanity has returned.

"""

import numpy as np
from lmfit import minimize, Minimizer, Parameters
from tpcfit import *


def resample_ssf(params = None, vals = None, temps=None, traits=None, fit_pars=None, iter = 5):
    """ Function to resample ssf model
    Parameters
    ----------
    params: lmfit.parameter.Paramerers
        Can be form of Parameters object
    vals: dict
        dictionary of sampling bounds
    temps: np array
        Temperature values in Kelvin
    traits: np array
        Trait values
    fat_pars: lmfit.parameter.Parameters
        Parameters for re-fitting
    iter: int
        Number of times to re-fit model """
    if params is not None:
        params = params
    if vals is not None:
        vals = vals
    if temps is not None:
        temps = temps
    if traits is not None:
        traits = traits
    if fit_pars is not None:
        fit_pars = fit_pars
    iter=iter

    models = []
    aics = []
    for i in range(iter):
        new_params = StartParams(params, vals)
        model = SharpeSchoolfieldFull(temps=temps, traits=traits, fit_pars=new_params)
        if model is not None:
            models.append(model)
            aics.append(model.AIC)

    best_aic = min(aics)

    for j in models:
        if j.AIC == best_aic:
            best_model = j

    return best_model

def resample_ssh(params = None, vals = None, temps=None, traits=None, fit_pars=None, iter = 5):
    """ Function to resample ssf model
    Parameters
    ----------
    params: lmfit.parameter.Paramerers
        Can be form of Parameters object
    vals: dict
        dictionary of sampling bounds
    temps: np array
        Temperature values in Kelvin
    traits: np array
        Trait values
    fat_pars: lmfit.parameter.Parameters
        Parameters for re-fitting
    iter: int
        Number of times to re-fit model """
    if params is not None:
        params = params
    if vals is not None:
        vals = vals
    if temps is not None:
        temps = temps
    if traits is not None:
        traits = traits
    if fit_pars is not None:
        fit_pars = fit_pars
    iter=iter

    models = []
    aics = []
    for i in range(iter):
        new_params = StartParams(params, vals)
        model = SharpeSchoolfieldHigh(temps=temps, traits=traits, fit_pars=new_params)
        models.append(model)
        aics.append(model.AIC)

    best_aic = min(aics)

    for j in models:
        if j.AIC == best_aic:
            best_model = j

    return best_model

def resample_ssl(params = None, vals = None, temps=None, traits=None, fit_pars=None, iter = 5):
    """ Function to resample ssl model
    Parameters
    ----------
    params: lmfit.parameter.Paramerers
        Can be form of Parameters object
    vals: dict
        dictionary of sampling bounds
    temps: np array
        Temperature values in Kelvin
    traits: np array
        Trait values
    fat_pars: lmfit.parameter.Parameters
        Parameters for re-fitting
    iter: int
        Number of times to re-fit model """
    if params is not None:
        params = params
    if vals is not None:
        vals = vals
    if temps is not None:
        temps = temps
    if traits is not None:
        traits = traits
    if fit_pars is not None:
        fit_pars = fit_pars
    iter=iter

    models = []
    aics = []
    for i in range(iter):
        new_params = StartParams(params, vals)
        model = SharpeSchoolfieldLow(temps=temps, traits=traits, fit_pars=new_params)
        models.append(model)
        aics.append(model.AIC)

    best_aic = min(aics)

    for j in models:
        if j.AIC == best_aic:
            best_model = j

    return best_model

def ssf_init(B0=None, E=None, Eh=None, El=None, Th=None, Tl=None, randomise=True):
    """ Initialise full schoolfield parameters

    Parameters
    ----------
    B0: int
        Normalisation constant
    E: int
        Activation energy
    Eh: int
        High temperatre deactivtion energy
    El: int
        Low temperature deactivation energy
    Th: int
        Temperature of high temperature deactivation
    Tl: int
        Temperature of low temperatre deactivation

    Returns
    -------
    params: lmfit.Parameter.Parameters object
        parameter object with parameter constraints

    """

    if B0 is not None:
        B0=B0
    if E is not None:
        E=E
    if Eh is not None:
        Eh=Eh
    if El is not None:
        El=El
    if Th is not None:
        Th=Th
    if Tl is not None:
        Tl=Tl

    params = Parameters()
    params.add("B0", value=B0, vary=True, min=-np.inf, max=np.inf)
    params.add("E", value=E, vary=True, min = 10E-3, max=np.inf)
    params.add("Eh", value=Eh, vary=True, min = 10E-3, max=np.inf)
    params.add("El", value=El, vary=True, min = 10E-3, max=np.inf)
    params.add("Th", value=Th, vary=True, min = 273.15, max=np.inf)
    params.add("Tl", value=Tl, vary=True, min = 273.15, max=np.inf)

    if randomise:
        for i in params.keys():
            params[i].value = np.random.normal()

    return params

def ssh_init(B0=None, E=None, Eh=None, Th=None, randomise=True):
    """ Initialise full schoolfield parameters

    Parameters
    ----------
    B0: int
        Normalisation constant
    E: int
        Activation energy
    Eh: int
        High temperatre deactivtion energy
    Th: int
        Temperature of high temperature deactivation

    Returns
    -------
    params: lmfit.Parameter.Parameters object
        parameter object with parameter constraints

    """

    if B0 is not None:
        B0=B0
    if E is not None:
        E=E
    if Eh is not None:
        Eh=Eh
    if Th is not None:
        Th=Th

    params = Parameters()
    params.add("B0", value=B0, vary=True, min=-np.inf, max=np.inf)
    params.add("E", value=E, vary=True, min = 10E-3, max=np.inf)
    params.add("Eh", value=Eh, vary=True, min = 10E-3, max=np.inf)
    params.add("Th", value=Th, vary=True, min = 273.15, max=np.inf)

    if randomise:
        for i in params.keys():
            params[i].value = np.random.normal()

    return params

def ssl_init(B0=None, E=None, El=None, Tl=None, randomise=True):
    """ Initialise full schoolfield parameters

    Parameters
    ----------
    B0: int
        Normalisation constant
    E: int
        Activation energy
    El: int
        low temperatre deactivtion energy
    Tl: int
        Temperature of low temperature deactivation

    Returns
    -------
    params: lmfit.Parameter.Parameters object
        parameter object with parameter constraints

    """

    if B0 is not None:
        B0=B0
    if E is not None:
        E=E
    if Eh is not None:
        Eh=Eh
    if Tl is not None:
        Tl=Tl

    params = Parameters()
    params.add("B0", value=B0, vary=True, min=-np.inf, max=np.inf)
    params.add("E", value=E, vary=True, min = 10E-3, max=np.inf)
    params.add("El", value=El, vary=True, min = 10E-3, max=np.inf)
    params.add("Tl", value=Tl, vary=True, min = 273.15, max=np.inf)

    if randomise:
        for i in params.keys():
            params[i].value = np.random.normal()

    return params


def get_datasets(data):
    """ Split unique datasets by originalid

    Parameters
    ----------
    data: full dataframe

    Returns
    -------
    datasets: A dictionary of curves with originalid as keys
    """

    # Get a list of curves
    curves = pd.unique(data["originalid"]).tolist()

    # Create a dictionary of datasets with "FinalID" as keys
    datasets = {}
    for i in curves:
        id = data.loc[data["originalid"] == i]
        id = id.sort_values("interactor1temp").reset_index()
        datasets[i] = id

    return datasets
