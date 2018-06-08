#!/bin/bash
CWD=$(pwd)

rm -rf $CWD/.build
mkdir -p $CWD/.build

# save dependencies
pip install -r requirements.txt -t $CWD/.build
cd $CWD/.build && zip -r $CWD/lib/dependencies.zip * -x **\*.pyc -x pip*/**\* -x pkg_resources*/**\* -x boto*/**\* -x setuptools*/**\* -x wheel*/**\*
