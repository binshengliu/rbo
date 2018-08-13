#!/usr/bin/env python3
"""Rank-biased overlap, a ragged sorted list similarity measure.

See http://doi.acm.org/10.1145/1852102.1852106 for details. All functions
directly taken from the paper are named so that they can be clearly
cross-identified.

The definition of overlap has been modified to account for ties. Without this,
results for lists with tied items were being inflated. The modification itself
is not mentioned in the paper but seems to be reasonable, see function
``overlap()``. Places in the code which diverge from the spec in the paper
because of this are highlighted with comments.

"""

import sys
import rbo
import argparse
import numpy as np
import lxml.etree as ET


def parse_args():
    parser = argparse.ArgumentParser(
        description='Measure rbo between two files.')

    parser.add_argument('-p', type=float, default=0.9)

    parser.add_argument('file1')

    parser.add_argument('file2')

    args = parser.parse_args()

    return args


def parse_rmodel(xml):
    d = {}
    root = ET.parse(xml).getroot()
    for model in root.findall('model'):
        qno = model.get('query')
        rm = [line.split() for line in model.text.strip().splitlines()]
        rm = dict((term, float(prob)) for prob, term in rm)
        d[qno] = rm
    return d


def rbo_rmodel_xml(xml1, xml2, p):
    rm1 = parse_rmodel(xml1)
    rm2 = parse_rmodel(xml2)

    queries = list(rm1.keys() & rm2.keys())
    try:
        queries.sort(key=int)
    except ValueError:
        queries.sort()

    results = []
    print('qno,intersection,union,p,min,res,ext')
    for q in queries:
        # print(rm1[q])
        # print(rm2[q])
        # return
        if not rm1[q] or not rm2[q]:
            continue
        result = rbo.rbo_dict(rm1[q], rm2[q], p)
        overlap = len(set(rm1[q]) & set(rm2[q]))
        total = len(set(rm1[q]) | set(rm2[q]))
        current = {
            'qno': q,
            'intersection': overlap,
            'union': total,
            'p': p,
            'min': result['min'],
            'res': result['res'],
            'ext': result['ext']
        }
        results.append(current)
        print('{},{},{},{},{:f},{:f},{:f}'.format(
            q, overlap, total, p, result['min'], result['res'], result['ext']))

    # min_mean = np.mean([r['min'] for r in results])
    # res_mean = np.mean([r['res'] for r in results])
    # ext_mean = np.mean([r['ext'] for r in results])
    # overlap_mean = np.mean([r['intersection'] for r in results])
    # total_mean = np.mean([r['union'] for r in results])
    # print('{},{},{},{},{:f},{:f},{:f}'.format('mean', overlap_mean, total_mean,
    #                                           p, min_mean, res_mean, ext_mean))
    return results


def main():
    args = parse_args()

    rbo_rmodel_xml(args.file1, args.file2, args.p)


if __name__ == '__main__':
    main()
