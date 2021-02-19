#!/bin/sh

GIT_DIR=`git rev-parse --show-toplevel`
RETURN_TOTAL=0
# Make sure we're at the top level dir
cd $GIT_DIR

echo "python-black"
black ./ --check
RETURN_TOTAL=`expr $RETURN_TOTAL + $?`

echo "flake8"
flake8 --exclude "*.ve"
RETURN_TOTAL=`expr $RETURN_TOTAL + $?`

echo "$RETURN_TOTAL checks failed!"

if [ $RETURN_TOTAL > 1 ]; then
  return 1
fi
