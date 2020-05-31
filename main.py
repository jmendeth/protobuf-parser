#!/usr/bin/env python3

from sys import stdin, argv
from os.path import ismount, exists, join
from runpy import run_path
from lib.types import StandardParser
import lib.toJSON

# Parse arguments
root_type = "root"
write_json = False
if len(argv) >= 2:
    if len(argv) == 2 and argv[1] == "-JSON":
        write_json = True
    elif len(argv) == 3 and argv[2] == "-JSON":
        root_type = argv[1]
        write_json = True
    else:
        root_type = argv[1]


# Load the config
config = {}
directory = "."
while not ismount(directory):
    filename = join(directory, "protobuf_config.py")
    if exists(filename):
        config = run_path(filename)
        break
    directory = join(directory, "..")

# Create and initialize parser with config
parser = StandardParser()
if "types" in config:
    for type, value in config["types"].items():
        assert(type not in parser.types)
        parser.types[type] = value
if "native_types" in config:
    for type, value in config["native_types"].items():
        parser.native_types[type] = value

# Make sure root type is defined and not compactable
if root_type not in parser.types: parser.types[root_type] = {}
parser.types[root_type]["compact"] = False

# PARSE!
parsed = parser.safe_call(parser.match_handler("message"), stdin.buffer, root_type) + "\n"
print(parsed)
if write_json:
    parsedJSON = lib.toJSON.run(parsed, write_json=write_json, print_json=False)
exit(1 if len(parser.errors_produced) else 0)
