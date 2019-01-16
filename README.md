This repository represents the BusVoodoo CI (WIP), which consists of:

- compiling firmware on 4 Linux distros via Docker

- Flashing all firmwares to a BusVoodoo device

- Running E2E tests via busvoodoo_e2e_test.py script,
  which uses pyserial to communicate with the BusVoodoo:

![buusvoodoo_e2e_tests console log](https://boddenberg.it/busvoodoo/busvoodoo_e2e_example.png)


- Additionally a testboard (Arduino based) can also be used to test the
  BusVoodoo's 'self-test' functionality. (a analog multiplexer is
  necessary to run the self-test.)

- Wrapping all above mentions steps in a Jenkins JobDSL Pipeline
  and execute them every night if a code change has been introduced.


Note: https://jenkins.blobb.me is moving, thus currently unavailable.
