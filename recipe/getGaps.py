#!/usr/local/bin/python

'''
Scripts for deriving the gaps from orthologs.
'''

import PyFBA

import argparse
import os
import sys

import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prokkaOrthologs', dest='orth',
                        help='Orthologs file')
    parser.add_argument('--gapsOutput', dest='outfile', default='missingFunctions.csv',
                        help='Output file for storing missing enzymes')
    opts = parser.parse_args()

    infile = opts.orth

    df = pd


if __name__ == '__main__':
    main()


parser = argparse.ArgumentParser(
    description='Convert an assigned_functions file to a list of roles')
parser.add_argument('-a', help='assigned functions file')
parser.add_argument('-r', help='roles file (one per line')
parser.add_argument('-v', help='verbose', action='store_true')
args = parser.parse_args()

if args.a:
    af = PyFBA.parse.read_assigned_functions(args.a)
    # roles = set(af.values())
    roles = set()
    [roles.update(i) for i in af.values()]
elif args.r:
    roles = set()
    with open(args.r, 'r') as f:
        for l in f:
            roles.update(PyFBA.parse.roles_of_function(l.strip()))
else:
    sys.exit('Either -a or -r must be specified')

rc = PyFBA.filters.roles_to_reactions(roles)
reactions = set()
for r in rc:
    reactions.update(rc[r])
print("\n".join(reactions))
