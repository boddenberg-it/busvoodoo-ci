#!/usr/bin/python
# deps: pip install pyserial junit-xml termcolor yaml
import argparse
import itertools
import re
import serial
import time
import yaml

from junitparser import TestCase, TestSuite, JUnitXml, Skipped, Error, IntAttr, Attr
from termcolor import colored

### HELPER TO INCREASE READABILITY ###
def log(msg):
    print colored('[INFO] %s' % msg, 'yellow')

def error(msg):
    print colored('[ERROR] %s' % msg, 'red')

def failure(msg):
    print colored('[FAILURE] %s' % msg, 'red')

def success(msg):
    print colored('[SUCCESS] %s' % msg, 'green')

# JUnit XML report helper
def add_testsuite(testsuite):
    testsuites.insert(len(testsuites), testsuite)

def create_testsuite(name):
    print
    log('executing %s' % name)
    return TestSuite(name)

def write_xml_report(testsuites):
	xml = JUnitXml()
	for testsuite in testsuites:
		xml.add_testsuite(testsuite)
	xml.write('busvoodoo_%s_testreport.xml' % 'date')

# bv serial commands helper
def bv_send(msg):
    bv_serial.write(b'%s\r' % msg)

def reset_busvoodoo():
    for i in range(10):
        bv_send('')
    bv_send('q')

def open_protocol(protocol):
    bv_send('m %s' % protocol)
    for i in range(10):
        bv_send('')

### GENERIC TEST FUNCTIONNS###
def generic_input(input, expectation):
    #flush buffer befor sending command
    bv_serial.readlines()
    bv_send(input)
    output = (bv_serial.readlines())
    output_stripped = ''.join(output)

    for e in expectation:
        if e is not '' and e not in output_stripped:
            return [ 1, output_stripped ]
    return [ 0, output_stripped ]

def generic_input_test(input, expectation, testname):
    tc = TestCase(testname)
    #flush buffer befor sending command
    bv_serial.readlines()

    bv_send(input)
    output = (bv_serial.readlines())
    output_stripped = ''.join(output)

    for e in expectation:
        if e not in output_stripped:
            tc.result = Error(ansi_escape.sub('', output_stripped), 'error')
            failure(testname)
            return tc
    success(testname)
    return tc

def generic_inputs(inputs, expectations):
    err_msg = ' generic_inputs(): inputs[] and expectations[] do not have equal length'
    if len(inputs) != len(expectations):
        error(err_msg)
        return [1, err_msg]

    reset_busvoodoo()
    outputs = ''

    for i in range(len(inputs)):
        result = generic_input(inputs[i], expectations[i])
        outputs += result[1]
        # fail fast
        if result[0] > 0:
            return [1, outputs]
    return [0, outputs]

### TEST SPECIIC FUNCTIONS
def prot_default_settings_test(protocol):
    #
    tc = TestCase('default protocol test: %s' % protocol)
    open_protocol(protocol)
    result = bv_serial.readlines()
    # add why we are doing this...
    if str.lower(protocol) not in str.lower(result[len(result)-1]):
        tc.result = Error(ansi_escape.sub('',''.join(result)), 'error')
        failure('default protocol %s test' % protocol)
        return tc
    #
    bv_serial.write(b'q\r')
    result = bv_serial.readlines()
    #
    if 'HiZ:' not in result[1]:
        tc.result = Error(ansi_escape.sub('',''.join(result)), 'error')
        failure('default protocol %s test' % protocol)
        return tc
    #
    success('default protocol %s test' % protocol)
    return tc

def selftest():
    str_s = 'self-test [s]'
    str_self_test = 'self-test [self-test]'
    tc_s = TestCase(str_s)
    tc_selftest = TestCase(str_self_test)

    bv_send('s')
    bv_send(' ')
    output = '.'.join(bv_serial.readlines())
    if 'self-test succeeded' not in output:
        error(str_s)
        tc_s.result = Error(ansi_escape.sub('', output), 'error')
    else:
        success(str_s)

    bv_send('self-test')
    bv_send(' ')
    output = '.'.join(bv_serial.readlines())
    if 'self-test succeeded' not in output:
        error(str_self_test)
        tc_selftest.result = Error(ansi_escape.sub('', output), 'error')
    else:
        success(output)
    return [tc_s, tc_selftest]

def pinstest():
    print "TBC..."

############### actual script #####################
# argparse
# so it could look like: BusVoodoo_e2e_tests.py --general_tests true --default_protocols_tests true --protocols_commands_test true
description = 'This is a test program. It demonstrates how to use the argparse module with a program description.'
parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description = description)
parser.add_argument("-g", "--general_tests", action='store_true', help="Set to execute general tests")
parser.add_argument("-p", "--protocol_command_tests", help="Execute commands test. Pass 'all' or comma separated string holding protocols 'spi,1-wire,uart'.")
parser.add_argument("-c", "--protocol_combination_tests", help="Execute combination test. Pass 'all' or comma separated string holding protocols 'spi,1-wire,uart'.")
parser.add_argument("-x", "--xml_report", help="Pass 'false' or path to disable report generation or specify absolute path (default is $PWD/busvoodoo_$(date)_test-report.xml)")
parser.add_argument("-f", "--flavor", required=True, help="flavor of BusVoodoo under test (light,full)")
parser.add_argument("-w", "--hardware_version", required=True, help="hardware version of BusVoodoo under test (v0,vA)")
parser.add_argument("-s", "--serial_address", required=True, help="Path to BusVoodoo serial device e.g. '/dev/ttyACM0'")
args = parser.parse_args()
# ./BusVoodoo_e2e_tests.py -w v0 -f light -s /dev/ttyACM0 -g -p all -c all

# bv output is ansi colored, so we need to replace
# these colored and XML invalid chars in order to put
# the output in the JUnit XML report for Jenkins.
ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

print args.general_tests
print args.protocol_command_tests
print args.flavor
print args.hardware_version

sys.exit(2)

# ... so all testsuites can add themselves after executing.
testsuites = []


# TODO: write help

log('opening Busvoodoo configuration YAML file...')
with open("BusVoodoo.yml", 'r') as stream:
    yaml = yaml.load(stream)

log('init serial connection to BusVoodoo...')
bv_serial = serial.Serial('/dev/ttyACM0', timeout=1)

#log('...init serial connection to testboard...')
#tb_serial = serial.Serial('/dev/ttyACM1', timeout=1)

reset_busvoodoo() # quit to HiZ mode

# GENERAL COMMANDS TESTS
testsuite = create_testsuite('general commands tests')
for command in yaml["commands"]:
    expectation = yaml["commands"][command]['expectation']
    for input in yaml["commands"][command]['input']:
        testsuite.add_testcase(
            generic_input_test(input, expectation,
                # testname
                "{0} [{1}]".format(command, input)))
# special test cases of "general commands tests"
for testcase in selftest():
    testsuite.add_testcase(testcase)
#for testcase in pinstest():it
#   testsuite.add_testcase(testcase)
add_testsuite(testsuite)

# DEFAULT PROTOCOL TESTS
testsuite = create_testsuite('default protocol tests')
for protocol in yaml["protocols"]:
    testsuite.add_testcase(prot_default_settings_test(protocol))
add_testsuite(testsuite)

# DEFAULT PROTOCOL COMMANDS TESTS
testsuite = create_testsuite('spi commands tests')
commands = yaml["protocols"]["spi"]["commands"]
open_protocol('spi')
for command in commands:
    expectation = yaml["protocols"]["spi"]["commands"][command]
    testsuite.add_testcase(generic_input_test('a %s' % command, expectation,
        'spi command test: a %s' % command))
add_testsuite(testsuite)


log('writing xml report to file...')
write_xml_report(testsuites)

# run all combinations of choices for each protocol
#for protocol in yaml["protocols"]:
protocol = 'spi'

inputs = yaml["protocols"][protocol]["combinations"]["inputs"]
expectations = yaml["protocols"][protocol]["combinations"]["expectations"]
permutations = list(itertools.product(*inputs))
testsuite = create_testsuite('%s_configuration_combinations_tests' % protocol)

for permutation in permutations:
    name = 'spi_combination-test_%s' % '-'.join(permutation)
    tc = TestCase(name)
    result = generic_inputs(permutation, expectations)
    if result[0] > 0:
        error = result[1]
        tc.Result = Error(error, 'error')
        failure(name)
    else:
        success(name)
    testsuite.add_testcase(tc)
add_testsuite(testsuite)
write_xml_report(testsuites)
