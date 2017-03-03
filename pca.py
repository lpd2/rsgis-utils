#! /usr/bin/env python
# gdal_pca.py
# Lawrence Dudley


''' This script performs the sklearn prinicipal components function
 on one or more gdal images '''

import argparse

import numpy as np
from osgeo import gdal, gdal_array
from sklearn.decomposition import IncrementalPCA


def standardise(array):

    ''' centres and scales array '''

    return (array - np.mean(array)) / np.std(array)

def make_stack(images, std=False):

    ''' Create a single stack of arrays from the bands of all images
    if std is True, each array is standardised first '''

    stack_list = []

    for image in images:

        dataset = gdal.Open(image)

        for i in range(dataset.RasterCount):

            band = dataset.GetRasterBand(i+1)
            array = band.ReadAsArray()

            if std:
                array = standardise(array)

            stack_list.append(array)

        dataset = None

    try:
        stack = np.stack(stack_list)
    except ValueError:
        print("Input images must be registered to same grid")
        raise ValueError

    return stack

def run_pca(stack):

    ''' run pca on stack, and then return the transformed array '''

    n_components = stack.shape[0]

    flat_stack = stack.reshape(n_components, stack.shape[1]*stack.shape[2])
    transpose_stack = np.transpose(flat_stack)

    pca = IncrementalPCA(n_components=n_components)

    pca.fit(transpose_stack)

    covariance = pca.get_covariance()

    explained_variance_ratio = pca.explained_variance_ratio_

    transform_flat = pca.transform(transpose_stack)
    transform_transpose = np.transpose(transform_flat)

    return (transform_transpose.reshape(stack.shape),
            covariance,
            explained_variance_ratio)

def main():

    ''' parse arguments, and call make_stack and run_pca '''

    parser = argparse.ArgumentParser()

    parser.add_argument('-i',
                        '--input',
                        type=str,
                        help='Input images separated by space')
    parser.add_argument('-o',
                        '--output',
                        type=str,
                        help='Output file name')
    parser.add_argument('-of',
                        '--output-format',
                        type=str,
                        default='kea',
                        help='Output gdal format')
    args = parser.parse_args()

    images = args.input.split(" ")
    output = args.output
    output_format = args.output_format
    print("Assembling and standardizing image stack")
    stack = make_stack(images, std=True)

    print("Running principal components analysis")
    pca_array, covariance, explained_variance_ratio = run_pca(stack)

    print("Covariance matrix:")
    print(covariance)

    print("Explained variance ratio:")
    print(explained_variance_ratio)

    prototype_ds = gdal.Open(images[0])

    gdal_array.SaveArray(pca_array, output, output_format, prototype_ds)

if __name__ == '__main__':
    main()
