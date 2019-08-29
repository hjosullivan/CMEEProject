#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import numpy as np
import pandas as pd
from scipy.stats import truncnorm
from lmfit import Minimizer, minimize, Parameters, report_fit
from tpcfit import *
import matplotlib.pyplot as plt
np.seterr(divide='ignore', invalid='ignore')

def main():
    """ Entry point of main script"""
    # Boltzmann constant
    global k
    k = 8.62e-5
    # Refernce temperature (0 degrees C)
    global Tref
    Tref = 273.15

    # Read data
    data = pd.read_csv(args.input)

    eg = ["MTD4538"]

    data = data.loc[data["originalid"].isin(eg)]

    # Create dictionary of starting parameters
    vals = {"B0": [0.05, 1.2], "E": [0.05, 0.85],
            "Eh": [0.5, 1.2],"El": [0.05, 0.7],
            "Th": [273.15, 330], "Tl": [273.15, 330]}


    # Get temperature and trait values
    temps, traits = np.array(data["interactor1K"]), np.array(data["standardisedtraitvalue"])

    #initialise parameter object
    params = ssf_init()

    # Get randomly sampled params
    new_params = StartParams(params, vals)

    # Fit model
    model = SharpeSchoolfieldFull(temps=temps, traits=traits, fit_pars=new_params)

    # Resample model
    best_mod = resample_ssf(vals=vals, params=params, temps=temps, traits=traits, iter = 5)

    # Collect estimates
    parameter_estimates = dict(best_mod.final_estimates)
    print(type(parameter_estimates))

    # Save results
    results = pd.DataFrame([parameter_estimates])
    results.to_csv(args.output, encoding='utf-8', index=False)

if __name__ == "__main__":
    # Assign a description to help doc
    parser = argparse.ArgumentParser(description="Basic script to fit thermal performance curves using non-linear least-squares")

    # Add arguments
    # Input file
    parser.add_argument("-i", "--input",
                        type=str,
                        help="Input path for folder or single csv",
                        required=False,
                        default="data/eucalyptus.csv")
    # output file
    parser.add_argument("-o", "--output",
                        type=str,
                        help="Output path for folder or single csv",
                        required=False,
                        default="data/fitted_models.csv")

    args = parser.parse_args()
    main()
