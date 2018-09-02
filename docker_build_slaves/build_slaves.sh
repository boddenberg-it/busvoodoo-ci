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

docker build -t "busvoodoo:archlinux_build" -f bv_archlinux_build.dckr .
docker build -t "busvoodoo:xenial_build" -f bv_xenial_build.dckr .
docker build -t "busvoodoo:bionic_build" -f bv_bionic_build.dckr .
docker build -t "busvoodoo:stretch_build" -f bv_stretch_build.dckr .
