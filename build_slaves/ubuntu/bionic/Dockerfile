FROM ubuntu:bionic

MAINTAINER andre@boddenberg.it

RUN apt-get update && \
	apt-get -y install --no-install-recommends \
	gcc-arm-none-eabi \
	rake \
	doxygen \
	git \
	make \
	python \
	binutils \
	libnewlib-arm-none-eabi && \
	apt-get clean; apt-get autoclean && \
	mkdir /build

VOLUME /build
WORKDIR /build
