#!/bin/sh
#
# Script will re-build all BusVoodoo docker images used
# for build pipelines on https://jenkins.blobb.me.
#
# This script is also used to re-build latest
# images on jenkins slaves themselves weekly.
#
# Morover, one can use these images to build locally
# with a different distro. This can be achieved by
# following invokation after desired image is build:
#
# docker run -it --rm=true \
#	-v "$BUSVOODOO_REPO":/build \
#	"$BUSVOODOO_IMAGE" \
#	BUSVOODOO_HARDWARE_VERSION="$HARDWARE_VERSION" rake
#
# HARDWARE_VERSION = {0,1}
# BUSVOODOO_IMAGE = {busvoodoo:archlinux_build,...}
# BUSVOODOO_REPO = path to checked out busvoodoo repo/branch

cd arch/
docker build -t "busvoodoo:archlinux_build" .
echo

cd ../debian/stretch/
docker build -t "busvoodoo:stretch_build" .
echo

cd ../../ubuntu/bionic
docker build -t "busvoodoo:bionic_build" .
echo

cd ../xenial
docker build -t "busvoodoo:xenial_build" .
cd ../..
