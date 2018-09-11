#!/usr/bin/python
# deps: pip install pyserial junit-xml termcolor
import itertools
import serial
import time
import yaml
import re

from junitparser import TestCase, TestSuite, JUnitXml, Skipped, Error, IntAttr, Attr
from termcolor import colored

# bv output is ansi colored, so we need to replace
# these colored and XML invalid chars in order to put
# the output in the JUnit XML report for Jenkins.
ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

testsuites = []

### HELPER TO INCREASE READABILITY ###
def log(msg):
    print colored('[INFO] %s' % msg, 'yellow')

def err(msg):
    print  colored('[ERROR] %s' % msg, 'red')

def failure(msg):
    print  colored('[FAILURE] %s' % msg, 'orange')

def success(msg):
    print  colored('[SUCCESS] %s' % msg, 'green')

def bv_send(msg):
    bv_serial.write(b'%s\r' % msg)

def add_testsuite(testsuite):
    testsuites.insert(len(testsuites), testsuite)

def write_xml_report(testsuites):
	xml = JUnitXml()
	for testsuite in testsuites:
		xml.add_testsuite(testsuite)
	xml.write('busvoodoo_%s_testreport.xml' % 'date')

def open_protocol(protocol):
    bv_serial.write(b'm %s\r' % protocol)
    for i in range(10):
        bv_serial.write(b'\r')

### GENERIC TEST FUNCTIONS ###
def generic_input(input, expectation):
    #flush buffer befor sending command
    bv_serial.readlines()
    bv_serial.write(b'%s\r' % input)
    output = (bv_serial.readlines())
    output_stripped = ''.join(output)

    for e in expectation:
        if e not in output_stripped:
            return 1
    return 0

def generic_input_test(testname, input, expectation):
    tc = TestCase(testname)
    #flush buffer befor sending command
    bv_serial.readlines()
    bv_serial.write(b'%s\r' % input)
    output = (bv_serial.readlines())
    output_stripped = ''.join(output)

    for e in expectation:
        if e not in output_stripped:
            print output_stripped
            tc.result = Error(ansi_escape.sub('', output_stripped), 'error')
            failure(testname)
            return tc
    success(testname)
    return tc

def generic_inputs_test(testname, inputs, expectations):
    tc = TestCase(testname)
    if len(inputs) != len(expectations):
        err('invalid')
        tc.result = skipped()
        return

    exit_codes = 0
    outputs = ''
    inputs = ''

    for i in range(len(inputs)):
        result = generic_input_test(inputs[i], expectations[i])
        exit_codes += result.pop()
        outputs += result.pop()
        inputs += result.pop()

    return {exit_codes, outputs, inputs}

### TEST SPECIIC FUNCTIONS
def prot_default_settings_test(protocol):
    #
    tc = TestCase('default protocol test: %s' % protocol)
    open_protocol(protocol)
    # Note: will not work anymore if more than 15 options available
    for i in range(15):
        bv_send('\r')
    #
    result = bv_serial.readlines()
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
    bv_serial.write(b's\r')
    bv_serial.write(b' \r')
    result = bv_serial.readlines()
    if 'self-test succeeded' not in '.'.join(result):
        print "ERROR command s"
    else:
        print "SUCCESS command s"
    # broken
    bv_serial.write(b'self-test\r')
    bv_serial.write(b' \r')
    result = bv_serial.readlines()
    if 'self-test succeeded' not in '.'.join(result):
        print "ERROR command self-test"
    else:
        print 'SUCCESS command self-test (s)'

def pinstest():
    print "TBC..."

############### actual script #####################
# init serial connections
log('...init serial connection to BusVoodoo')
bv_serial = serial.Serial('/dev/ttyACM0', timeout=1)
#log('...init serial connection to testboard...')
#tb_serial = serial.Serial('/dev/ttyACM1', timeout=1)

log('...opening Busvoodoo configuration YAML file')
with open("BusVoodoo.yml", 'r') as stream:
    yaml = yaml.load(stream)

bv_serial.write(b'q\r') # quit to HiZ mode
print # to have an empty space before TestSuite run

log('executing: general commands testsuite')
testsuite = TestSuite('general commands tests')
for command in yaml["commands"]:
    expectation = yaml["commands"][command]['expectation']
    for input in yaml["commands"][command]['input']:
        testsuite.add_testcase(
            generic_input_test("{0} [{1}]".format(command, input),
                input, expectation))
add_testsuite(testsuite)

log('executing: default protocol tests')
testsuite = TestSuite('default protocol tests')
for protocol in yaml["protocols"]:
    testsuite.add_testcase(prot_default_settings_test(protocol))
add_testsuite(testsuite)


write_xml_report(testsuites)
sys.exit(0)



bv_serial.write(b'q\r')
testsuite = create_test_suite('spi commands tests')
commands = yaml["protocols"]["spi"]["commands"]
open_protocol('spi')
for command in commands:
    tc = create_test_case('spi command: %s' % command)
    expectation = yaml["protocols"]["spi"]["commands"][command]
    result = generic_input_test('a %s' % command, expectation)
    if result.pop() > 0:
        tc.result = Error(result.pop(), 'error')
    testsuite.add_testcase(tc)
testsuites.insert(len(testsuites), testsuite)

# run all combinations of choices for each protocol
#for protocol in yaml["protocols"]:

protocol = 'spi'

inputs = yaml["protocols"][protocol]["combinations"]["inputs"]
expectations = yaml["protocols"][protocol]["combinations"]["expectations"]

testsuite = create_test_suite('%s_configuration_combinations_tests' % protocol)
permutations = list(itertools.product(*inputs))

for permutation in permutations:
    tc = create_test_case('spi_combination-test_%s' % '-'.join(permutation))
    result = generic_inputs_test(permutation, expectations)
    if result.pop() > 0:
        tc.Result = Error(result.pop(), 'error')
    testsuite.add_testcase(tc)
testsuites.insert(len(testsuites), testsuite)

write_xml_report(testsuites)

sys.exit(0)
