FROM base/archlinux

MAINTAINER andre@boddenberg.it

RUN pacman -Sy &&\
	pacman -S --noconfirm \
	arm-none-eabi-binutils \
	arm-none-eabi-gcc \
	rake \
	doxygen \
	git \
	binutils \
	python \
	make \
	arm-none-eabi-newlib && \
	pacman -Scc --noconfirm && \
	mkdir /build

VOLUME /build
WORKDIR /build
