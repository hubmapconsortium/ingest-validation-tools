#!/usr/bin/env bash
set -o errexit

ls tests/* | parallel --halt now,fail=1 bash
