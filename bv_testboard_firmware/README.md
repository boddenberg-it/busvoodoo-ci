# Purpose
The BusVoodoo Testboard gives the [BusVoodoo E2E tests](https://git.boddenberg.it/busvoodoo-ci/tree/master/bv_e2e_tests) a possibility to test the pintest routine of the BusVoodoo. In this test one needs to connect one pin of the BusVoodoo to several other pins sequentially on the BusVoodoo itself. In order to do so the following hardware is use:

  - 1 x Arduino Nano + USB cable
  - 1 x 16 channel analog multiplexer (HC4067)
  - 1 x 4 port USB hub (with power switches per port)
  - 3 x MOSFETs
  - some wires,...

The MOSFETs are used to reset (power off/on) each port of the USB hub, which is the host of all BusVoodoo test environment devices (BusVoodoo, Flasher, Testboard).
Additionally, the Testboard can boot the BusVoodoo into DFU mode to flash the firmware. This shall be helpful when a broken firmware corrupted the BusVoodoo's built-in update functionality.

# How does it work?
The [BusVoodoo E2E tests script](https://github.com/boddenberg-it/busvoodoo-ci/tree/master/bv_e2e_tests) opens an additional serial port to the Testboard and use the following commands:

 - **p** pings Testboard
 - **b** boots the BusVoodoo into DFU mode
 - **d** disables the multiplexer (power down)
 - **s1101** sets multiplexer: bits stand for S0, S1, S2, S3 pins on the mulitplexer board
 - **g** returns the current multiplexer configuration "ACK: 0101"
 - **r{b,f,t}** resets the **B**usVoodoo, **F**lashboard, **T**estboard
 - **a** reset all devices

*Note: **s1001** also enables the multiplexer in case it has been disabled (**d**) before.*

# "Schematics"

tbc...
