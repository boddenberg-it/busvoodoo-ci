#!/usr/bin/python
#
# deps: pip install pyserial junit-xml
import itertools
import serial
import time
import yaml
from junit_xml import TestSuite, TestCase

def log(msg):
    print '[INFO] %s' % msg

def err(msg):
    print '[ERROR] %s' % msg

def generic_input_test(input, expectation):

    bv_serial.write(b'%s\r' % input)
    output = bv_serial.readlines()
    output_stripped = '.'.join(output)
    result = 0

    for e in expectation:
        if e not in output_stripped:
            result = 1

    return { result, input, output_stripped }

def generic_inputs_test_suite(name, inputs, expectations):

    if len(inputs) != len(outsputs):
        print 'invalid setup, why did not the yaml syntax checker kick in?'
        return

    test_cases = []

    for i in range(len(inputs)):
#       TODO: move timing to generic_input_test
        start = timeit.timeit()
        result = generic_input_test(inputs[i], outputs[i])
        end = timeit.timeit()

        # TODO: move to own def
        tc = TestCase('step %d' % i, 'busvodoo', end - start, result[1], result[2])
        if result[0] == 1:
            tc.failure_message = 'Please see stdout for the input and stderr for the resulting output.'
            tc.failure_output = 'failure'
            tc.failure_type = 'failure'
        # so the following can be called
        test_cases.append(generate_test_case_from_generic_input_test(result))
    return TestSuite(name, test_cases)


def prot_default_settings_test(protocol):

    bv_serial.write(b'm %s\r' % protocol)
    for i in range(10):
        bv_serial.write(b'\r')
    result = bv_serial.readlines()
    if str.lower(protocol) not in str.lower(result[len(result)-1]):
        print('ERROR WITH PROTOCOL: %s' % protocol)

    bv_serial.write(b'q\r')
    result = bv_serial.readlines()
    if 'HiZ:' not in result[1]:
        print('ERROR could not quit mode: %s' % protocol)
        return
    print('%s SUCCESS!' % protocol)

def prot_settings_test(inputs, expectations):
    for i in xrange(1,len(inputs)):
        print(inputs[i])
        print generic_input_test(inputs[i], expectations[i])
        print("")

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

############### actual script ##############

log('opening Busvoodoo configuration YAML file...')
with open("BusVoodoo.yml", 'r') as stream:
    data_loaded = yaml.load(stream)
# loop over all protocols and do the default check
#print(len(data_loaded["protocols"]))
# loop over all combinations for all protocols
#print(len(data_loaded["protocols"][0]))
#print(data_loaded["protocols"][0]["name"])
#print(data_loaded["protocols"][0]["c0"])
#print(data_loaded["protocols"][0]["c1"])
#print(data_loaded["protocols"][0]["c2"])
#print(data_loaded["protocols"][0]["c3"])
#print(data_loaded["protocols"][0]["c4"])
#print(data_loaded["protocols"][0]["c5"])
#    print
log('init serial connection to BusVoodoo...')
bv_serial = serial.Serial('/dev/ttyACM0', timeout=1)
#log('[INFO] init serial connection to BusVoodoo...')
#tb_serial = serial.Serial('/dev/ttyACM1', timeout=1)



#input: keine buchstaben als abkuerzungen
# input: bei allen varianten noch checktagsfen.

generic_input_test('v', ['BusVoodoo flavor', 'hardware version', 'firmware date'])
generic_input_test('version', ['BusVoodoo flavor', 'hardware version', 'firmware date'])
# TODO: fix one string issue!

generic_input_test('h','available commands')
generic_input_test('help','available commands')

selftest()

log('starting all protocols default settings tests...')
for s in ['1-wire', 'uart', 'i2c', 'spi', 'hiz']:
    prot_default_settings_test(s)


# extract it over yml file foo
spi_option_0 = 'm spi'
spi_tag_0 = 'duplex mode', 'full-duplex', 'bidirectional'
spi_option_1 = [1,2]
spi_tag_1 = 'frequency', '18000 kHz', '9000 kHz', '4500 kHz', '2250 kHz', '1125 kHz', '562 kHz', '281 kHz', '140 kHz'
spi_option_2 = [1,2,3,4,5,6,7,8,9]
spi_tag_2 = 'data frame width in bits'
spi_option_3 = [8,16]
spi_tag_3 = 'data frame bit order', 'most significant bit first', 'least significant bit first'
spi_option_4 = [1,2]
spi_tag_4 = 'mode', '0', '1', '2', '3', '4'
spi_option_5 = [1,2,3,4]
spi_tag_5 = 'drive mode', 'push', 'external', 'embedded'
spi_option_6 = [1,2,3]
spi_tag_6 = 'SPI' # check_tag load it from yaml

# testing all spi combinations (takes 30 minutes)
t = list(itertools.product(spi_option_0, spi_option_1, spi_option_2, spi_option_3, spi_option_4, spi_option_5, spi_option_6))
print(len(t))
expectations = [spi_tag_0, spi_tag_1, spi_tag_2, spi_tag_3, spi_tag_4, spi_tag_5, spi_tag_6]

#for inputs in t:
#    prot_settings_test(inputs, expectations)

# yaml file, protocol, check string, list of lists
