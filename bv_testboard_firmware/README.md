# Purpose
The BusVoodoo Testboard gives the [BusVoodoo E2E tests](https://github.com/boddenberg-it/busvoodoo-ci/tree/master/bv_e2e_tests) a possibility to test the pintest. In this test one needs to connect one pin to several other pins sequentially on the BusVoodoo itself. In order to do so the following hardware is used.

  - 1 x Arduino Nano
  - 1 x 16-Channel-Analog-Multiplexer
  - 1 x 4 port USB hub
  - 3 X MOSFETs
  - some wires,...

The MOSFETs are used to reset (power off/on) each port of the USB hub, which is the host of all BusVoodoo test environment devices (BusVoodoo, Flasher, Testboard).
Additionally, the Testboard can boot the BusVoodoo into DFU mode to flash the firmware. This shall be helpful when a broken firmware corrupted the BusVoodoo's built-in update functionality.

# How does it work?
The [BusVoodoo E2E tests](https://github.com/boddenberg-it/busvoodoo-ci/tree/master/bv_e2e_tests) open an additional serial port to the Testboard and use the following commands:

 - **p** (pings Testboard)
 - **b** (boots the BusVoodoo into DFU mode)
 - **d** (powers down the multiplexer)
 - **g** (returns the current multiplexer configuration as "4 bit String" )
 - **r{b,f,t}** (resets (power off/on) the **B**usVoodoo, **F**lashboard, **T**estboard)
 - **a** (reset all devices)
 - **s[0,15]** (sets multiplexer by integer between 0 and 15. Integer will be converted into 4 bits, e.g. 9 = 1001. Those bits are standing for S0,S1,S2,S3 pins on the mulitplexer board.)

*Note: **s[0,15]** also enables the multiplexer in case it has been disabled (**d**) before.*

# "Schematics"
tbc...
