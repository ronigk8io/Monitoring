#!/usr/bin/env python2.7
import sys
from evmNodeGetBlock import getEVMBlock

if len(sys.argv) < 2:
    print("Usage:", sys.argv[0], "<node_ip>")
    sys.exit(1)
node_ip = sys.argv[1]

# timeout set in getEVMBlock

getEVMBlock(node_ip+":34567")
