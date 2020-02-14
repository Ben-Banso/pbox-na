#!/bin/bash

BUILD_ROOT=~/rpmbuild
PWD=$(pwd)
VERSION=$(cat version.txt)
NAME="pbox-na"

cp rpm/$NAME.spec $BUILD_ROOT/SPECS/

mkdir /tmp/$NAME-$VERSION/
cp -r * /tmp/$NAME-$VERSION
cd /tmp
tar -zcf $BUILD_ROOT/SOURCES/pbox-na-$VERSION.tar.gz $NAME-$VERSION
rm -rf $NAME-$VERSION

cd $BUILD_ROOT/SPECS/
rpmbuild -bb $NAME.spec
cd $PWD
