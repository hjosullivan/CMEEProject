#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import numpy as np
import pandas as pd
import warnings

__author__ = "Hannah O'Sullivan (h.osullivan18@imperial.ac.uk)"
__appname__ = "subset_biotraits.py"
__version__ = "0.0.1"
__date__ = "April 2019"

"""
Example :
    $ python Data_clean.py -i input filepath -o output filepath
"""

def get_datasets(data):
    """ Split unique datasets by originalid

    Parameters
    ----------
    data: full dataframe

    Returns
    -------
    datasets: A dictionary with FinalID as keys
    """

    # Get a list of curves
    curves = pd.unique(data["originalid"]).tolist()

    # Create a dictionary of datasets with "FinalID" as keys
    datasets = {}
    for i in curves:
        id = data.loc[data["originalid"] == i]
        id = id.sort_values("temps").reset_index()
        datasets[i] = id

    return datasets

def celcius2kelvin(dataset, is_celcius = True):
    """Replaces temperature units in celcius to Kelvin

    Parameters
    ----------
    dataset: pandas core dataframe
        single TPC to be cleaned
    is_celcius: boolean, default True

    Returns
    -------
    dataset: new dataframe with converted units in Kelvin
    """

    if is_celcius:
        dataset["temps"] = dataset["temps"] + 273.15
    else:
        dataset["temps"] = dataset["temps"]

    return dataset

def rm_negative_vals(dataset):
    """Removes 0 or negative values

    Parameters
    ----------
    dataset: dataframe to be cleaned

    Returns
    -------
    dataset: new dataframe without negative temperature or trait values
    """

    # Find minimum temperature value
    min_temp_val = dataset["temps"].min()

    # Find minimum trait value
    min_trait_val = dataset["traits"].min()

    # Get rid of 0s for temps and traits columns
    if min_trait_val <= 0:
        dataset["traits"] -= min_trait_val - 10E-10

    if min_temp_val <= 0:
        dataset["temps"] -= min_temp_val - 10E-10

    return dataset

def unique_temps(dataset):
    """Gets the number of unique temperatures for a given dataset

    (Will be useful when checking model parameters)

    Parameters
    ----------
    dataset: pandas core dataframe
        dataframe to be cleaned

    Returns
    -------
    dataset: new dataframe with unique_temps column
    """

    dataset["unique_temps"] = dataset["temps"].nunique()

    return dataset

def main():

    print("Preparing data for NLLS fitting...")

    # Read in data
    data = pd.read_csv(args.input, low_memory=False)

    # Rename columns so things are less annoying to type
    data.rename(columns={"interactor1temp":"temps",         "standardisedtraitvalue":"traits"}, inplace=True)

    # Create dictionary of TPCs
    datasets = get_datasets(data)

    for i in datasets.keys():
        dataset = datasets[i]
        # Convert temperature in celcius to kelvin
        dataset = celcius2kelvin(dataset)
        # Remove negative values
        dataset = rm_negative_vals(dataset)
        # Get number of unique temps
        dataset = unique_temps(dataset)

    # Export clean data to results folder
    data = pd.concat(datasets)
    data.to_csv(args.output, index=False)
    print("NLLS data saved to {}".format(args.output))

if __name__ == "__main__":
    """ This is executed when run from the command line"""

    # Assign command line interface
    parser = argparse.ArgumentParser(description="Command line script to prepare data for nlls fitting")

    # Input file
    parser.add_argument("-i", "--input",
                        type=str,
                        help="Input path csv",
                        required=False,
                        default="../data/TestData.csv")

    # Output file
    parser.add_argument("-o", "--output",
                        type=str,
                        help="Output path for resulting csv file",
                        required=False,
                        default="../data/NLLSData.csv")

    args = parser.parse_args()
    main()
