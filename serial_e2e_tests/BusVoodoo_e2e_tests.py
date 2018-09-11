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
    print  colored('[FAILURE] %s' % msg, 'red')

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

def create_testsuite(name):
    log('executing %s' % name)
    return TestSuite(name)

### GENERIC TEST FUNCTIONS ###
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
    bv_serial.write(b'%s\r' % input)
    output = (bv_serial.readlines())
    output_stripped = ''.join(output)

    for e in expectation:
        if e not in output_stripped:
            tc.result = Error(ansi_escape.sub('', output_stripped), 'error')
            failure(testname)
            return tc
    success(testname)
    return tc

def reset_busvoodoo():
    for i in range(10):
        bv_send('')
    bv_send('q')


def generic_inputs(inputs, expectations):
    err_msg = ' generic_inputs(): inputs[] and expectations[] do not have equal length'
    if len(inputs) != len(expectations):
        err(err_msg)
        return [1, err_msg]

    reset_busvoodoo()
    outputs = ''

    for i in range(len(inputs)):
        result = generic_input(inputs[i], expectations[i])
        outputs += result[1]
        # fail fast
        if  result[0] > 0:
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

log('opening Busvoodoo configuration YAML file...')
with open("BusVoodoo.yml", 'r') as stream:
    yaml = yaml.load(stream)

log('init serial connection to BusVoodoo...')
bv_serial = serial.Serial('/dev/ttyACM0', timeout=1)

#log('...init serial connection to testboard...')
#tb_serial = serial.Serial('/dev/ttyACM1', timeout=1)

reset_busvoodoo() # quit to HiZ mode
print # to have an empty space before TestSuite run

log('executing: general commands testsuite')
testsuite = TestSuite('general commands tests')
for command in yaml["commands"]:
    expectation = yaml["commands"][command]['expectation']
    for input in yaml["commands"][command]['input']:
        testsuite.add_testcase(
            generic_input_test(input, expectation,
                "{0} [{1}]".format(command, input)))
add_testsuite(testsuite)

log('executing: default protocol tests')
testsuite = TestSuite('desfault protocol tests')
for protocol in yaml["protocols"]:
    testsuite.add_testcase(prot_default_settings_test(protocol))
add_testsuite(testsuite)

log('executing: spi commands tests')
testsuite = TestSuite('spi commands tests')
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
testsuite = TestSuite('%s_configuration_combinations_tests' % protocol)
log('executing spi combinations tests')

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
