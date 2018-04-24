#!/usr/bin/env python

import argparse
from sys import argv
from os.path import ismount, exists, join
from runpy import run_path
from lib.types import StandardParser

# Parse arguments
parser = argparse.ArgumentParser(prog=argv[0],
                                 description='Inspect protobuf files.')
parser.add_argument('input', help='the file to inspect')
parser.add_argument('-t', '--type', default='root', help='set root type')
parser.add_argument('-c', '--config', help='provide config file')
args = parser.parse_args(argv[1:])

# Load the config
config = run_path(args.config) if args.config else {}

# Create and initialize parser with config
parser = StandardParser()
if "types" in config:
    for type, value in config["types"].items():
        type = unicode(type)
        assert(type not in parser.types)
        parser.types[type] = value
if "native_types" in config:
    for type, value in config["native_types"].items():
        parser.native_types[unicode(type)] = value

# Make sure root type is defined and not compactable
if args.type not in parser.types: parser.types[args.type] = {}
parser.types[args.type]["compact"] = False

# PARSE!
print(parser.safe_call(parser.match_handler("message"), open(args.input, 'rb'), args.type) + "\n")
exit(1 if len(parser.errors_produced) else 0)
