#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import sys

"""
Example :
    $ python Data_clean.py file2clean.csv
"""

def celcius2kelvin(data, temps_col, is_celcius):
    """Replaces temperature units in celcius to Kelvin

    Parameters
    ----------
    data : dataframe to be cleaned
    temps_col: column of tempearture values
    is_celcius: boolean

    Returns
    -------
    data : new dataframe with converted units in Kelvin
    """
    if is_celcius:
        data["temps"] = data[temps_col] + 273.15
    else:
        data["temps"] = data[temps_col]

    return data

def convert_traits(data, traits_col, temp_conversion):
    """Converts s^-1 trait values to d^-1

    Parameters
    ----------
    data : dataframe to be cleaned
    traits_col: column of trait values
    temp_conversion: 60 * 60 * 24

    Returns
    -------
    data : new dataframe with converted values in new "traits" column
    """
    # Convert corrected value from s^-1 to d^-1
    data['traits'] = data[traits_col] * temp_conversion

    return data

def rm_negative_vals(data):
    """Removes 0 or negative values

    Parameters
    ----------
    data : dataframe to be cleaned

    Returns
    -------
    data : new dataframe with converted units in Kelvin
    """
    min_temp_val  = data['temps'].min()
    min_trait_val  = data['traits'].min()

    # Get rid of 0s for temps and traits columns
    if min_trait_val <= 0:
        data['traits'] -= min_trait_val - 10E-10

    if min_temp_val <= 0:
        data['temps'] -= min_temp_val - 10E-10

    return data

def main():

    # Check whether an input file has been provided
    if len(sys.argv) == 1:
        file = "Data/BioTraits.csv"
        print("No arguments provided, using BioTraits data")
    elif len(sys.argv) == 2:
        file = sys.argv[1]
        print("Using input data")

    # Assign relevant columns
    trait_name_col = 'StandardisedTraitName'
    temps_col = 'ConTemp' # i.e.x values
    traits_col = 'StandardisedTraitValue' # i.e. y values

    # Is the temperature in kelvin or celcius?
    is_celcius = True

    # Temperature conversion
    temp_conversion = 60 * 60 * 24

    # Read in data
    data = pd.read_csv(file, low_memory=False)

    # Convert temperature in celcius to kelvin
    data = celcius2kelvin(data, temps_col, is_celcius)
    print("Converting temperatures...")

    # Convert traits in s^-1 to d^-1
    data = convert_traits(data, traits_col, temp_conversion)
    print("Converting traits...")

    # Remove any negative values
    data = rm_negative_vals(data)
    print("Removing negative values...")

    # Export clean data to results folder
    data.to_csv("Results/CleanData.csv", index = False)
    print("Done!")

if __name__ == "__main__":
     main()
