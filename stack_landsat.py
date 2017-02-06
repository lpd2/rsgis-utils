#!/usr/bin/env python
# stack_landsat.py
# Lawrence Dudley 4/2/2017

''' This script takes a landsat MTL.txt file as input, along with a list
of desired bands to stack (optional) and creates a geotiff image containing
these image bands.

'''

from osgeo import gdal, gdal_array
import numpy as np
import glob
import argparse
import os

def get_bands(input_mtl, bands_for_stack):

    ''' Returns file path of all bands '''

    # directory of input_mtl
    mtl_basename = os.path.basename(input_mtl)
    img_dir = os.path.abspath(input_mtl).replace(mtl_basename, "")


    band_ids = ["B" + band_no + ".TIF" for band_no in bands_for_stack]

    bands = []

    for band in glob.glob(img_dir + "*.TIF"):
        if any(band_id in band for band_id in band_ids):
            bands.append(band)

    return bands

def gdal2array(image_name):

    ''' Opens, reads into array and closes a gdal image '''

    gdal_ds = gdal.Open(image_name)

    img_as_array = gdal_ds.ReadAsArray()

    gdal_ds = None

    return img_as_array


def stack_bands(bands, output_name):

    ''' Stack bands into 3d numpy array, and save using first band as prototype

    '''

    stack = np.array([gdal2array(band) for band in bands])

    prototype = gdal.Open(bands[0])

    gdal_array.SaveArray(stack, output_name, 'gtiff', prototype)

    prototype = None


def run():

    ''' Parse arguments, get the list of images to stack and call stack_bands()
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("-i",
                        "--input",
                        type=str,
                        help="Input MTL.txt file for landsat image")
    parser.add_argument("-b",
                        "--bands",
                        type=str,
                        default=None,
                        help="Specify which bands to stack. Default is B1 - 8")
    args = parser.parse_args()

    input_mtl = args.input

    bands = args.bands
    if not bands:
        bands = "1 2 3 4 5 6 7 8"
    bands = bands.split()

    bands_for_stack = get_bands(input_mtl, bands)

    output_name = input_mtl.replace("MTL.txt", "stack.tif")

    stack_bands(bands_for_stack, output_name)

if __name__ == "__main__":
    run()
