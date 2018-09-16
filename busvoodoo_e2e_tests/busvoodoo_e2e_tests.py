#!/usr/bin/python
# deps: pip install pyserial junit-xml termcolor yaml
import argparse
import datetime
import itertools
import re
import serial
import sys
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

def write_xml_report(testsuites, name='busvoodoo_e2e_%s_testreport.xml' % datetime.datetime.now().strftime("%Y-%m-%d_%H:%m")):
	xml = JUnitXml()
	for testsuite in testsuites:
		xml.add_testsuite(testsuite)
	xml.write(name)

# bv serial commands helper
def bv_send(msg):
    bv_serial.write(b'%s\r' % msg)

def softreset_busvoodoo():
    log('soft-resetting BusVoodoo via \'reset\' command')
    # end potential protocol config sequence
    for i in range(10):
        bv_send('')
    # quit to HiZ mode
    bv_send('q')

def open_protocol(protocol):
    bv_send('m %s' % protocol)
    for i in range(10):
        bv_send('')

### GENERIC TEST FUNCTIONNS###
def generic_input(input, expectation):
    #flush buffer before sending command
    bv_serial.readlines()

    bv_send(input)
    output = ''.join(bv_serial.readlines())

    for e in expectation:
        if e is not '' and e not in output:
            return [1, output]
    return [0, output]

def generic_input_test(input, expectation, testname):
    tc = TestCase(testname)
    result = generic_input(input, expectation)
    if result[0] > 0:
            tc.result = Error(ansi_escape.sub('', result[1]), 'error')
            failure(testname)
            return tc
    success(testname)
    return tc

def generic_inputs(inputs, expectations):
    err_msg = ' generic_inputs(): inputs[] and expectations[] do not have equal length'
    if len(inputs) != len(expectations):
        error(err_msg)
        return [1, err_msg]

    outputs = ''

    for i in range(len(inputs)):
        result = generic_input(inputs[i], expectations[i])
        outputs += result[1]
        # fail fast
        if result[0] > 0:
            return [1, outputs]
    return [0, outputs]

def get_protocols_based_on_hw_verison(protocols):
    # only one protocol specified
    if protocols != 'all' and ',' not in protocols:
        return [protocols]
    # used for default choices
    if protocols == 'all':
        protocols = yaml["protocols"]
    # comma-separated list of protocols
    elif ',' in protocols:
        protocols = args.protocol_command_tests.split(',')

    supported_protocols = []
    for protocol in protocols:
        supported_versions = yaml["protocols"][protocol]['hardware_version'].split(',')
        if args.hardware_version in supported_versions:
            supported_protocols.insert(len(supported_protocols),protocol)
    return supported_protocols

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
# bv output is ansi colored, so we need to replace
# these colored and XML invalid chars in order to put
# the output in the JUnit XML report for Jenkins.
ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

# ... so all testsuites can add themselves after executing.
testsuites = []

description = 'This is a test program. It demonstrates how to use the argparse module with a program description.'
parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description = description)
parser.add_argument("-W", "--hardware_version", required=True, help="hardware version of BusVoodoo under test (v0,vA)")
# TODO: Ask whether the flavor is important for testing?
#parser.add_argument("-F", "--flavor", required=True, help="flavor of BusVoodoo under test (light,full)")
parser.add_argument("-S", "--serial_address", required=True, help="Path to BusVoodoo serial device e.g. '/dev/ttyACM0'")
parser.add_argument("-t", "--testboard_address", help="Set serial address of BusVoodoo testboard to run all general tests.")
parser.add_argument("-g", "--general_tests", action='store_true', help="Set to execute general tests")
parser.add_argument("-d", "--default_protocols_test", action='store_true', help="Testsuite which opens every protocol mode supported by passed 'hardware_version'")
parser.add_argument("-p", "--protocol_command_tests", help="Execute commands test. Pass 'all' or comma separated string holding protocols 'spi,1-wire,uart'.")
parser.add_argument("-c", "--protocol_combination_tests", help="Execute combination test. Pass 'all' or comma separated string holding protocols 'spi,1-wire,uart'.")
parser.add_argument("-x", "--xml_report", help="Pass 'false' or path to disable report generation or specify absolute path (default is $PWD/busvoodoo_$(date)_test-report.xml)")
args = parser.parse_args()

# INIT & SANITY
log('opening Busvoodoo configuration YAML file...')
with open("busvoodoo_e2e_tests.yml", 'r') as stream:
    yaml = yaml.load(stream)

try:
    log('init serial connection to BusVoodoo...')
    bv_serial = serial.Serial(args.serial_address, timeout=1)
    softreset_busvoodoo() # clean start
except:
    error("serial connection to busvoodoo could NOT been established!")
    sys.exit(1)

log('verifying passed HW_VERSION with device HW_VERSION')
if generic_input('v', ['hardware version: %s' % args.hardware_version])[0] > 0:
    error("passed HW_VERSION does NOT match device HW_VERSION!")
    sys.exit(1)

if args.testboard_address:
    try:
        log('init serial connection to testboard...')
        tb_serial = serial.Serial('/dev/ttyACM1', timeout=1)
    except:
        error("serial connection to testboard could NOT been established!")
        sys.exit(1)
    # TODO: introduce check that it's the testboard

# GENERAL COMMANDS TESTS
if args.general_tests:
    # test cases which lives in yaml
    testsuite = create_testsuite('general commands tests')
    for command in yaml["commands"]:
        expectation = yaml["commands"][command]['expectation']
        for input in yaml["commands"][command]['input']:
            testsuite.add_testcase(
                generic_input_test(input, expectation,
                    # passing a testname for XML report readability
                    "{0} [{1}]".format(command, input)))

    # special test cases (too 'complex' for YAML config)
    for testcase in selftest():
        testsuite.add_testcase(testcase)

    # special test cases which needs testboard
    if args.testboard_address:
        print 'tbc'
        #for testcase in pinstest():
        #testsuite.add_testcase(testcase)
    add_testsuite(testsuite)

# DEFAULT PROTOCOLS TESTS
if args.default_protocols_test:
    testsuite = create_testsuite('default protocols tests')
    for protocol in get_protocols_based_on_hw_verison('all'):
            testsuite.add_testcase(prot_default_settings_test(protocol))
    add_testsuite(testsuite)

# DEFAULT PROTOCOLS COMMANDS TESTS
if args.protocol_command_tests:
    for protocol in get_protocols_based_on_hw_verison(args.protocol_command_tests):
        testsuite = create_testsuite('%s commands tests' % protocol)
        open_protocol(protocol)
        for command in yaml["protocols"][protocol]["commands"]:
            expectation = yaml["protocols"][protocol]["commands"][command]
            testsuite.add_testcase(generic_input_test('a %s' % command, expectation,
                '{0} command test: a {1}'.format(protocol, command)))
        add_testsuite(testsuite)
    softreset_busvoodoo()

# PROTOCOL COMBINATION TESTS
if args.protocol_combination_tests:
    for protocol in get_protocols_based_on_hw_verison(args.protocol_combination_tests):
        inputs = yaml["protocols"][protocol]["combinations"]["inputs"]
        expectations = yaml["protocols"][protocol]["combinations"]["expectations"]
        testsuite = create_testsuite('%s_configuration_combinations_tests' % protocol)

        for permutation in list(itertools.product(*inputs)):
            name = '{0}_combination-test_{1}'.format(protocol, '-'.join(permutation))
            tc = TestCase(name)
            result = generic_inputs(permutation, expectations)
            if result[0] > 0:
                tc.Result = Error(result[1], 'error')
                failure(name)
            else:
                success(name)
            testsuite.add_testcase(tc)

        add_testsuite(testsuite)

log('writing xml report to file...')
if args.xml_report:
    write_xml_report(testsuites, args.xml_report)
else:
    write_xml_report(testsuites)
