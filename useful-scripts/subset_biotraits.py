#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import pandas as pd
import random

__author__ = "Hannah O'Sullivan (h.osullivan18@imperial.ac.uk)"
__appname__ = "subset_biotraits.py"
__version__ = "0.0.1"
__date__ = "April 2019"

"""
Example :
    $ python subset_biotraits.py -i input filepath -tpc number of tpcs to subset -o output filepath
"""

def get_test_data(data, no_tpcs):
    """Generates a random subset of datasets from
    large TPC databases

    Parameters
    ----------
    data : large dataframe to be subsettted
    no_tpcs: number of tpc datasets to extract (int)

    Returns
    -------
    test_data : smaller dataframe for testing
    """

    # Get a list of unique ids for each curve
    curves = pd.unique(data['originalid']).tolist()

    # Select datasets at random
    test_curves = random.sample(curves, no_tpcs)

    # Generate test data
    test_data = data.loc[data['originalid'].isin(test_curves)]

    return test_data

def main():

    # Read in file
    data = pd.read_csv(args.input, low_memory=False)

    # Generate test data
    print("Generating test data...")
    TestData = get_test_data(data, args.no_tpcs)
    print("{} TPC datasets selected...".format(args.no_tpcs))

    # Save to output directory
    TestData.to_csv(args.output, index = False)
    print("Test data saved to {}".format(args.output))

if __name__ == "__main__":
    """ This is executed when run from the command line"""
    # Assign command line interface
    parser = argparse.ArgumentParser(description="Command line script to randomly subset TPCs from biotraits database")

    # Input file
    parser.add_argument("-i", "--input",
                        type=str,
                        help="Input path csv",
                        required=False,
                        default="../data/GlobalDataset_v0.71.csv")

    # Number of TPCs to subset
    parser.add_argument("-tpc", "--no_tpcs",
                        type=int,
                        help="Number of TPC datasets to subset",
                        required=False,
                        default=10)

    # Output file
    parser.add_argument("-o", "--output",
                        type=str,
                        help="Output path for resulting csv file",
                        required=False,
                        default="../data/TestData.csv")

    args = parser.parse_args()
    main()
