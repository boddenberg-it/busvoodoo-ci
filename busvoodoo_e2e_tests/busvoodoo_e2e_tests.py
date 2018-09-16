#!/usr/bin/python
"""  is this the doc string"""
# deps: pip install pyserial junit-xml termcolor YAML
import argparse
import datetime
import itertools
import re
import sys
import serial
import yaml

from termcolor import colored
from junitparser import TestCase, TestSuite, JUnitXml, Error

### HELPER TO INCREASE READABILITY ###


def log(msg):
    """tbc..."""
    print colored('[INFO] %s' % msg, 'yellow')


def error(msg):
    """tbc..."""
    print colored('[ERROR] %s' % msg, 'red')


def failure(msg):
    """tbc..."""
    print colored('[FAILURE] %s' % msg, 'red')


def success(msg):
    """tbc..."""
    print colored('[SUCCESS] %s' % msg, 'green')

# JUnit XML report helper


def add_testsuite(passed_testsuite):
    """tbc..."""
    TESTSUITES.insert(len(TESTSUITES), passed_testsuite)


def create_testsuite(passed_name):
    """tbc..."""
    print
    log('executing %s' % passed_name)
    return TestSuite(passed_name)


def get_date():
    """tbc..."""
    return datetime.datetime.now().strftime("%Y-%m-%d_%H:%m")


def write_xml_report(testsuites, test_name=''):
    """tbc..."""
    if test_name == '':
        test_name = 'busvoodoo_e2e_%s_testreport.xml' % get_date()

    xml = JUnitXml()
    for test_suite in testsuites:
        xml.add_testsuite(test_suite)
    xml.write(test_name)

# bv serial commands helper


def bv_send(msg):
    """tbc..."""
    BV_SERIAL.write(b'%s\r' % msg)


def softreset_busvoodoo():
    """tbc..."""
    log('soft-resetting BusVoodoo via \'reset\' command')
    # end potential protocol config sequence
    for _ in range(10):
        bv_send('')
    # quit to HiZ mode
    bv_send('q')


def open_protocol(i_protocol):
    """tbc..."""
    bv_send('m %s' % i_protocol)
    for _ in range(10):
        bv_send('')

### GENERIC TEST FUNCTIONNS###


def generic_input(passed_input, i_expectation):
    """tbc..."""
    # flush buffer before sending command
    BV_SERIAL.readlines()

    bv_send(passed_input)
    output = ''.join(BV_SERIAL.readlines())

    for exp in i_expectation:
        if exp != '' and exp not in output:
            return [1, output]
    return [0, output]


def generic_input_test(i_input, i_expectation, testname):
    """tbc..."""
    i_testcase = TestCase(testname)
    i_result = generic_input(i_input, i_expectation)
    if i_result[0] > 0:
        test_case.result = Error(ANSI_ESCAPE.sub('', i_result[1]), 'error')
        failure(testname)
        return i_testcase
    success(testname)
    return i_testcase


def generic_inputs(i_inputs, i_expectations):
    """tbc..."""
    err_msg = ' generic_inputs(): inputs[] and expectations[] do not have equal length'
    if len(i_inputs) != len(i_expectations):
        error(err_msg)
        return [1, err_msg]

    outputs = ''

    for i_input, i_expectation in i_inputs, i_expectations:
        i_result = generic_input(i_input, i_expectation)
        outputs += i_result[1]
        # fail fast
        if i_result[0] > 0:
            return [1, outputs]
    return [0, outputs]


def get_protocols(i_protocols):
    """tbc..."""
    # only one protocol specified
    if i_protocols != 'all' and ',' not in i_protocols:
        if ARGS.hardware_version in YAML["protocols"][i_protocols]["hardware_version"].split(','):
            return [i_protocols]
        error('protocol not supported for used hardware version')
        return [None]
    # used for default choices
    if i_protocols == 'all':
        i_protocols = YAML["protocols"]
    # comma-separated list of protocols
    elif ',' in i_protocols:
        i_protocols = ARGS.protocol_command_tests.split(',')

    supported_protocols = []
    for i_protocol in i_protocols:
        supported_versions = YAML["protocols"][i_protocols]['hardware_version'].split(
            ',')
        if ARGS.hardware_version in supported_versions:
            supported_protocols.insert(len(supported_protocols), i_protocol)
    return supported_protocols

# TEST SPECIIC FUNCTIONS


def prot_default_settings_test(i_protocol):
    """tbc..."""
    i_testcase = TestCase('default protocol test: %s' % i_protocol)
    open_protocol(i_protocol)
    i_result = BV_SERIAL.readlines()
    # add why we are doing this...
    if str.lower(i_protocol) not in str.lower(i_result[len(i_result)-1]):
        i_testcase.result = Error(
            ANSI_ESCAPE.sub('', ''.join(i_result)), 'error')
        failure('default protocol %s test' % i_protocol)
        return i_testcase
    #
    BV_SERIAL.write(b'q\r')
    i_result = BV_SERIAL.readlines()
    #
    if 'HiZ:' not in i_result[1]:
        i_testcase.result = Error(
            ANSI_ESCAPE.sub('', ''.join(i_result)), 'error')
        failure('default protocol %s test' % i_protocol)
        return i_testcase
    #
    success('default protocol %s test' % i_protocol)
    return i_testcase


def selftest():
    """tbc..."""
    str_s = 'self-test [s]'
    str_self_test = 'self-test [self-test]'
    test_case_s = TestCase(str_s)
    test_case_selftest = TestCase(str_self_test)

    bv_send('s')
    bv_send(' ')
    output = '.'.join(BV_SERIAL.readlines())
    if 'self-test succeeded' not in output:
        error(str_s)
        test_case_s.result = Error(ANSI_ESCAPE.sub('', output), 'error')
    else:
        success(str_s)

    bv_send('self-test')
    bv_send(' ')
    output = '.'.join(BV_SERIAL.readlines())
    if 'self-test succeeded' not in output:
        error(str_self_test)
        test_case_selftest.result = Error(ANSI_ESCAPE.sub('', output), 'error')
    else:
        success(output)
    return [test_case_s, test_case_selftest]


def pinstest():
    """Runs the pins-test BV command via analog multiplexer on testboard"""
    print "TBC..."


############### actual script #####################
# bv output is ansi colored, so we need to replace
# these colored and XML invalid chars in order to put
# the output in the JUnit XML report for Jenkins.
ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

# ... so all testsuites can add themselves after executing.
TESTSUITES = []

DESCRIPTION = """This is a test program. It demonstrates how to use the
    argparse module with a program description."""

PARSER = argparse.ArgumentParser()
PARSER = argparse.ArgumentParser(description=DESCRIPTION)
PARSER.add_argument("-W", "--hardware_version", required=True,
                    help="hardware version of BusVoodoo under test (v0,vA)")
# TD: Ask whether the flavor is important for testing?
#PARSER.add_argument("-F", "--flavor", required=True, help="""flavor of
#    BusVoodoo under test (light,full)""")
PARSER.add_argument("-S", "--serial_address", required=True, help="""Path to
    BusVoodoo serial device e.g. '/dev/ttyACM0'""")
PARSER.add_argument("-t", "--testboard_address", help="""Set serial address of
    BusVoodoo testboard to run all general tests.""")
PARSER.add_argument("-g", "--general_tests",
                    action='store_true', help="Set to execute general tests")
PARSER.add_argument("-d", "--default_protocols_test", action='store_true',
                    help="""Testsuite which opens every protocol mode
                    supported by passed 'hardware_version""")
PARSER.add_argument("-p", "--protocol_command_tests", help="""Execute commands
    test. Pass 'all' or comma separated string holding protocols
    'spi,1-wire,uart'.""")
PARSER.add_argument("-c", "--protocol_combination_tests", help="""Execute
    combination test. Pass 'all' or comma separated string holding protocols
    'spi,1-wire,uart'.""")
PARSER.add_argument("-x", "--xml_report", help="""Pass 'false' or path to
    disable report generation or specify absolute path
    (default is $PWD/busvoodoo_$(date)_test-report.xml)""")
ARGS = PARSER.parse_args()

# INIT & SANITY
log('opening Busvoodoo configuration YAML file...')
with open("busvoodoo_e2e_tests.yml", 'r') as stream:
    YAML = yaml.load(stream)

try:
    log('init serial connection to BusVoodoo...')
    BV_SERIAL = serial.Serial(ARGS.serial_address, timeout=1)
    softreset_busvoodoo()  # clean start
except serial.serialutil.SerialException:
    error("serial connection to busvoodoo could NOT been established!")
    sys.exit(1)

log('verifying passed HW_VERSION with device HW_VERSION')
if generic_input('v', ['hardware version: %s' % ARGS.hardware_version])[0] > 0:
    error("passed HW_VERSION does NOT matest_caseh device HW_VERSION!")
    sys.exit(1)

if ARGS.testboard_address:
    try:
        log('init serial connection to testboard...')
        TB_SERIAL = serial.Serial('/dev/ttyACM1', timeout=1)
    except serial.serialutil.SerialException:
        error("serial connection to testboard could NOT been established!")
        sys.exit(1)
    # TD: introduce check that it's the testboard

# GENERAL COMMANDS TESTS
if ARGS.general_tests:
    # test cases which lives in YAML
    TESTSUITE = create_testsuite('general commands tests')
    for command in YAML["commands"]:
        expectation = YAML["commands"][command]['expectation']
        for inner_input in YAML["commands"][command]['input']:
            name = '{0} [{1}]'.format(command, inner_input)
            TESTSUITE.add_testcase(
                generic_input_test(inner_input, expectation, name))

    # special test cases (too 'complex' for YAML config)
    for testest_casease in selftest():
        TESTSUITE.add_testcase(testest_casease)

    # special test cases which needs testboard
    if ARGS.testboard_address:
        print 'tbc'
        # for testest_casease in pinstest():
        # testsuite.add_testest_casease(testest_casease)
    add_testsuite(TESTSUITE)

# DEFAULT PROTOCOLS TESTS
if ARGS.default_protocols_test:
    TESTSUITE = create_testsuite('default protocols tests')
    for protocol in get_protocols('all'):
        TESTSUITE.add_testcase(prot_default_settings_test(protocol))
    add_testsuite(TESTSUITE)

# DEFAULT PROTOCOLS COMMANDS TESTS
if ARGS.protocol_command_tests:
    PROTOCOLS = get_protocols(ARGS.protocol_command_tests)
    if PROTOCOLS and PROTOCOLS[0] != None:
        for protocol in PROTOCOLS:
            testsuite = create_testsuite('%s commands tests' % protocol)
            open_protocol(protocol)
            for command in YAML["protocols"][protocol]["commands"]:
                expectation = YAML["protocols"][protocol]["commands"][command]
                name = '{0} command test: {1}'.format(protocol, command)
                testsuite.add_testcase(
                    generic_input_test(command, expectation, name))
                add_testsuite(testsuite)
        softreset_busvoodoo()

# PROTOCOL COMBINATION TESTS
if ARGS.protocol_combination_tests:
    for protocol in get_protocols(ARGS.protocol_combination_tests):
        inputs = YAML["protocols"][protocol]["combinations"]["inputs"]
        expectations = YAML["protocols"][protocol]["combinations"]["expectations"]
        testsuite = create_testsuite(
            '%s_configuration_combinations_tests' % protocol)

        for permutation in list(itertools.product(*inputs)):
            name = '{0}_combination-test_{1}'.format(
                protocol, '-'.join(permutation))
            test_case = TestCase(name)
            result = generic_inputs(permutation, expectations)
            if result[0] > 0:
                test_case.Result = Error(result[1], 'error')
                failure(name)
            else:
                success(name)
            testsuite.add_testest_casease(test_case)

        add_testsuite(testsuite)

if TESTSUITES:
    log('writing xml report to file...')
    if ARGS.xml_report:
        write_xml_report(TESTSUITES, ARGS.xml_report)
    else:
        write_xml_report(TESTSUITES)
else:
    log('no testsuites found to be reported to XML')
