#!/usr/bin/env sh
set -eu

speculative-bench run --out reports --repeats 3 --warmups 1
