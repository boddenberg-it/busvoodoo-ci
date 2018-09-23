# Purpose
This testboard is capable of resetting and rebooting the [BusVoodoo](http://busvoodoo.cuvoodoo.info/) into DFU mode in an automated manner.

Resetting ensures that each testjob runs on a freshly booted BusVoodoo. Booting into DFU mode ensures that a firmware can be flashed even when the built-in update functionality of the BusVoodoo is broken.

Additionally, the testboard provides a possibility to test the 'pins-test' routine of the BusVoodoo. In this test one needs to connect one pin of the BusVoodoo to several other pins sequentially on the BusVoodoo itself.

Following hardware is used:

  - 1 x Arduino Nano + USB cable
  - 1 x 16 channel analog multiplexer breakout module (HC4067)
  - 2 x P-MOSFET
  - some wires, soldering iron,...

![busvoodo + testboard executing pins-test routine](https://boddenberg.it/github_pics/busvoodoo-ci/testboard.jpg "BusVoodo + testboard executing pins-test routine")

# How does it work?
The [BusVoodoo E2E tests script](https://github.com/boddenberg-it/busvoodoo-ci/tree/master/busvoodoo_e2e_tests) opens an additional serial port to the testboard and use the following commands:

 - **b** boots the BusVoodoo into DFU mode
 - **s1101** sets multiplexer: bits stand for S0, S1, S2, S3 pins on the mulitplexer board
 - **g** returns the current multiplexer !state and its configuration "ACK: 0-0101"
 - **d** disables the multiplexer
 - **r** resets the BusVoodoo

*Note: **s1001** also enables the multiplexer in case it has been disabled (**d**) before.*

