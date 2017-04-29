#!/usr/bin/env python3
# @Author: Dileep Kishore <dileep>
# @Last modified by:   dileep

from os import path
import csv
from collections import defaultdict, namedtuple
from functools import partial


def write_file(disease_info, data_fol):
    """
        Write disease_info dictionary to file
        Parameters:
        -----------
        disease_info : Dict
            Dictionary containing key: year-Wweek and value: List of Infection tuples
    """
    fname = data_fol('h1n1_data.csv')
    sorted_keys = sorted(disease_info)
    with open(fname, 'w') as fid:
        csvwriter = csv.writer(fid)
        for key in sorted_keys:
            for elem in disease_info[key]:
                row = [key, elem.Country, elem.H1N1, elem.Total]
                csvwriter.writerow(row)
    return None

def main(data_fol, data_file):
    """
        Extract worl-wide H1N1 infection data
        Parameters:
        -----------
        data_fol : partial path.join function
            Partial path function that links to the data directory
        data_file : str
            File name of the input file
    """
    header_list = ['\ufeffCountry', 'Year', 'Week', 'AH1N12009', 'ALL_INF']
    fname = data_fol(data_file)
    Infection = namedtuple('Infection', ['Country', 'H1N1', 'Total'])
    disease_info = defaultdict(set)
    with open(fname, 'r') as fid:
        header = next(fid).split(',')
        header = [d.strip() for d in header]
        header_ind = tuple(filter(lambda x: header[x] in header_list, range(len(header))))
        csvreader = csv.reader(fid, delimiter=',')
        for row in csvreader:
            cty, yr, wk, h1n1, total = [row[i] for i in header_ind]
            key = yr + '-W' + wk.zfill(2)
            value = Infection(Country=cty, H1N1=h1n1, Total=total)
            disease_info[key].add(value)
    write_file(disease_info, data_fol)

if __name__ == '__main__':
    data_dir = partial(path.join, path.abspath('../../data/flu_data'))
    infile = 'FluNetInteractiveReport.csv'
    main(data_dir, infile)
