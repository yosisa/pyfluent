#!/bin/bash

if [ $# -ne 1 ]; then
    echo "usage: $0 VERSION"
    exit 1
fi

sed -i .bak -e "s/^version = '.*'/version = '$1'/g" setup.py
rm setup.py.bak

sed -i .bak -e "s/^tag_build = dev/;tag_build = dev/g" setup.cfg
rm setup.cfg.bak

echo Files modified successfully, version bumped to $1
exit 0
