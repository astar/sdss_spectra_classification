#!/usr/bin/env python
# -*- coding:utf-8 -*-


"""Usage: ./extractor.py [-D ...] [--help] [--output <file>] <spectra_dir> <files> ...

run klaus.py in intervals

Options:
  -h, --help                    Show this screen
  -D,                           Print debug info
  -o, --output <file>           Output file [default: out.csv]
"""
from docopt import docopt
import sys
import os
from clint.textui import progress
import pandas as pd
import re
import pyfits as pf
import numpy as np
import os

from glopt.glopt import Glopt
from glopt.glopt import Timer



def process(cfg):

    Glopt.debug('OPT: ' + ''.join(str(cfg).split('\n')))
    global spectra_dir
    spectra_dir = cfg['dir']
    output = cfg['output']

    pieces = []
    with Timer("Reading csv files"):
        for csv_file in cfg['files']:
            pieces.append(pd.read_csv(csv_file))

    with Timer("Concating files"):
        data = pd.concat(pieces)

    data['fit_name'] = data.spectrum.apply(file_name_from_url)
    data['type'] = data['class'].apply(class_to_type)

    with Timer("Geting data from fits"):
        data['data'] = data.fit_name.apply(get_fit_data)

    with Timer("Writing output to: {}".format(output)):
        data.to_csv(output)



def get_fit_data(fit):
    with Timer("Reading fit file: {}".format(fit)):
        hdulist = pf.open(os.path.join(spectra_dir, fit))
        #c0 = hdulist[0].header['coeff0']
        #c1 = hdulist[0].header['coeff1']
        #npix = hdulist[1].header['naxis2']
        #wave = 10.**(c0 + c1 * np.arange(npix))
        flux = hdulist[1].data['flux']
        #model = hdulist[1].data['model']
        data = ','.join([str(num) for num in flux])
    return data



def class_to_type(x):
    return {
        'STAR': 1,
        'GALAXY': 2,
        'QSO': 3,
        }.get(x, -1)



def file_name_from_url(url):
    return re.match('.*(spec-.*)', url).groups()[0]



def main():

    args = docopt(__doc__)
    prg = os.path.basename(sys.argv[0])
    Glopt(prg, args, args['-D'], None)

    with Timer():

        cfg = {'dir': args['<spectra_dir>'], 'files': args['<files>'], 'output': args['--output']}

        if process(cfg):
            pass



if __name__ == '__main__':
    main()


# vim: set cin et ts=4 sw=4 ft=python :
