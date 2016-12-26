#! /usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

(py-deactivate-env || /usr/bin/true) > /dev/null 2>&1
(deactivate || /usr/bin/true) > /dev/null 2>&1

rm -Rf \
        ./.virtualenv \
        ./.tox \
        ./drawstools.egg-info \
        tags

find ./drawstools/ -name __pycache__ -print -exec rm -Rf \{\} \;
find ./drawstools/ -name '*.pyc' -delete
find ./ -name "*~" -exec rm -f \{\} \;

