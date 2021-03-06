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


def parse_args():
    parser = argparse.ArgumentParser(
        description='Measure rbo between two files.')

    parser.add_argument('-p', type=float, default=0.9)

    parser.add_argument('file1', type=argparse.FileType('r'))

    parser.add_argument('file2', type=argparse.FileType('r'))

    args = parser.parse_args()

    return args


def parse_run(lines):
    qno_list = {}
    for l in lines:
        qno, _, docno, _, _, _ = l.split()
        qno_list.setdefault(qno, []).append(docno)
    return qno_list


def main():
    args = parse_args()
    p = args.p

    lines1 = args.file1.readlines()
    lines2 = args.file2.readlines()

    run1 = parse_run(lines1)
    run2 = parse_run(lines2)

    queries = list(run1.keys() & run2.keys())
    try:
        queries.sort(key=int)
    except ValueError:
        queries.sort()

    results = []
    print('qno,intersection,union,p,min,res,ext')
    for q in queries:
        # print(run1[q])
        # print(run2[q])
        # return
        result = rbo.rbo(run1[q], run2[q], p)
        overlap = len(set(run1[q]) & set(run2[q]))
        total = len(set(run1[q]) | set(run2[q]))
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

    min_mean = np.mean([r['min'] for r in results])
    res_mean = np.mean([r['res'] for r in results])
    ext_mean = np.mean([r['ext'] for r in results])
    overlap_mean = np.mean([r['intersection'] for r in results])
    total_mean = np.mean([r['union'] for r in results])
    print('{},{},{},{},{:f},{:f},{:f}'.format('mean', overlap_mean, total_mean,
                                              p, min_mean, res_mean, ext_mean))
    return results


if __name__ == '__main__':
    main()
