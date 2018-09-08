#!/bin/bash -ex

TIMEOUT_FOR_BV_REBOOT=3

function move_artifacts() {
	mv application.bin ../../"$1_application.bin"
	mv application.elf ../../"$1_application.elf"
	mv bootloader.bin ../../"$1_application.bin"
	mv bootloader.elf ../../"$1_application.elf"
}

# create folder for each distro and copy repo
if [ "$1" = "prepare" ]; then
	mkdir xenial bionic stretch archlinux
	echo xenial bionic stretch archlinux | xargs -n 1 cp -ar source
	exit 0
fi

# flash firmware version and verify successful boot
if [[ "$1" = "flash" && ! -z "$2" ]]; then
	dfu-util --device "${DEVICE_ID}" --download "$2_${DEVICE_VERSION}_application.bin"
	sleep $TIMEOUT_FOR_BV_REBOOT
	if [ $(lsusb | grep "${DEVICE_ID} InterBiometrics" | wc -l) = 1 ]; then
		exit 0
	else
		exit 1
	fi
fi

# build firmware V{0,A}
if [[ "$1" = "build" && ! -z "$2" ]]; then
	BUSVOODOO_HARDWARE_VERSION=0 rake
	move_artifacts "$2_v0"
	rake clean
	BUSVOODOO_HARDWARE_VERSION=1 rake
	move_artifacts "$2_vA"
fi

