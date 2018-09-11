#!/usr/bin/python
# deps: pip install pyserial junit-xml
import itertools
import serial
import time
import yaml
import re

from junitparser import TestCase, TestSuite, JUnitXml, Skipped, Error, IntAttr, Attr

### helper to increase log readability ###
def log(msg):
    print '[INFO] %s' % msg

def err(msg):
    print '[ERROR] %s' % msg

def fail(msg):
    print '[FAILURE] %s' % msg

def success(msg):
    print '[SUCCESS] %s' % msg

def bv_send(msg):
    bv_serial.write(b'%s\r' % msg)

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

### junitparser functions to create JUnit XML report ###
TestCase.duration = IntAttr('duration')
TestCase.input = Attr('input')
TestCase.output = Attr('output')

def create_test_case(name, error=None, duration='', input='', output=''):
	case = TestCase(name)
	case.duration = duration
	if error is not None:
		case.input = input
		case.output = output
		case.result = Error(output, 'error')
    	return case

def create_test_suite(name):
	return TestSuite(name)

def write_xml_report(testsuites):
	xml = JUnitXml()
	for testsuite in testsuites:
		xml.add_testsuite(testsuite)
	xml.write('busvoodoo_%s_testreport.xml' % 'date')

### generic test functions ###
def generic_input(input, expectation):
    bv_serial.write(b'%s\r' % input)
    output = bv_serial.readlines()
    output_stripped = ''.join(output)


    for e in expectation:
        if e not in output_stripped:
            tc.result = Error(output_stripped, 'error')

    return {result, output_stripped, input}

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
    return tc


def generic_inputs_test(inputs, expectations):
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

### test specific functions ###
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
        tc.result = Error('could not open protocol mode', 'error')
        return tc
    #
    bv_serial.write(b'q\r')
    result = bv_serial.readlines()
    #
    if 'HiZ:' not in result[1]:
        tc.result = Error('could not quit protocol mode', 'error')
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
# create list for all testsuites
testsuites = []
# init serial connections
log('...init serial connection to BusVoodoo')
bv_serial = serial.Serial('/dev/ttyACM0', timeout=1)
#log('...init serial connection to testboard...')
#tb_serial = serial.Serial('/dev/ttyACM1', timeout=1)
#

# reset BusVoodoo
bv_serial.write(b'q\r')


log('...opening Busvoodoo configuration YAML file')
with open("BusVoodoo.yml", 'r') as stream:
    yaml = yaml.load(stream)

testsuite = create_test_suite('general commands test')
for command in yaml["commands"]:
    print
    print command
    expectation = yaml["commands"][command]['expectation']
    for input in yaml["commands"][command]['input']:
        print input
        testsuite.add_testcase(generic_input_test(command, input, expectation))
testsuites.insert(len(testsuites), testsuite)

write_xml_report(testsuites)

sys.exit(0)



    #testsuite.add_testcase(prot_default_settings_test(protocol))
#testsuites.insert(len(testsuites), testsuite)

testsuite = create_test_suite('default protocol tests')
for protocol in yaml["protocols"]:
    testsuite.add_testcase(prot_default_settings_test(protocol))
testsuites.insert(len(testsuites), testsuite)


def open_protocol(protocol):
    bv_serial.write(b'm %s\r' % protocol)
    for i in range(10):
        bv_serial.write(b'\r')

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
