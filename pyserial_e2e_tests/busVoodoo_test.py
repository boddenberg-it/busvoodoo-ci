#!/usr/bin/python

import itertools
#import junit_xml
import serial
import time
import yaml
from junit_xml import TestSuite, TestCase

# output ruhig mit in JUnit XML
# Mulitplexer fr pintest benutzen..


############## functions ################
def generic_input_test(input, expectation):

    ser.write(b'%s\r' % input)
    output = ser.readlines()
    output_stripped = '.'.join(result)
    result = 0

    for e in expectation:
        if e not in result_stripped:
            result = 1

    return { result, input, output_stripped }

def generic_inputs_test_suite(name, inputs, expectations):

    if len(inputs) != len(outsputs):
        print 'invalid setup, why did not the yaml syntax checker kick in?'
        return

    test_cases = []

    for i in range(len(inputs))
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



# bloody hack, think about contributing

def prot_default_settings_test(protocol):

    ser.write(b'm %s\r' % protocol)
    for i in range(10):
        ser.write(b'\r')
    result = ser.readlines()
    if str.lower(protocol) not in str.lower(result[len(result)-1]):
        print('ERROR WITH PROTOCOL: %s' % protocol)

    ser.write(b'q\r')
    result = ser.readlines()
    print result
    if 'HiZ:' not in result[1]:
        print('ERROR could not quit mode: %s' % protocol)
        return
    print('SUCCESS!')

def prot_settings_test(inputs, check_tags):

    generic_input_test()

    result = ser.readlines()

    print inputs

    if str.lower(protocol) not in str.lower(result[len(result)-1]):
        print('ERROR WITH PROTOCOL: %s' % protocol)
    else:
        print('SUCCESS!')

def selftest():
    ser.write(b's\r')
    ser.write(b' \r')
    result = ser.readlines()
    if 'self-test succeeded' not in '.'.join(result):
        print "ERROR command s"
    else:
        print "SUCCESS command s"
    # broken
    ser.write(b'self-test\r')
    ser.write(b' \r')
    result = ser.readlines()
    if 'self-test succeeded' not in '.'.join(result):
        print "ERROR command self-test"
    else:
        print 'SUCCESS command self-test (s)'

############### actual script ##############

with open("busvoodoo.yml", 'r') as stream:
    data_loaded = yaml.load(stream)

# loop over all protocols and do the default check
print(len(data_loaded["protocols"]))

# loop over all combinations for all protocols
print(len(data_loaded["protocols"][0]))
#print(data_loaded["protocols"][0]["name"])
#print(data_loaded["protocols"][0]["c0"])
#print(data_loaded["protocols"][0]["c1"])
#print(data_loaded["protocols"][0]["c2"])
#print(data_loaded["protocols"][0]["c3"])
#print(data_loaded["protocols"][0]["c4"])
#print(data_loaded["protocols"][0]["c5"])

#    print

print('[INFO] init connection...')
ser = serial.Serial('/dev/ttyACM0', timeout=1)



#input: keine buchstaben als abkuerzungen
# input: bei allen varianten noch checktagsfen.


# put those into yaml file!
generic_input_test('v', ['BusVoodoo flavor', 'hardware version', 'firmware date'])
generic_input_test('version', ['BusVoodoo flavor', 'hardware version', 'firmware date'])
# TODO: fix one string issue!

generic_input_test('h','available commands')
generic_input_test('help','available commands')

selftest()
#generic_input_test()

exit

#print('[INFO] starting all protocols default settings tests...')
for s in ['1-wire', 'uart', 'i2c', 'spi', 'hiz']:
    prot_default_settings_test(s)


# extract it over yml file foo
spi_option_01= 'm spi'
spi_tag_0 = 'duplex mode', 'full-duplex', 'bidirectional'
spi_option_0 = [1,2]
spi_tag_1 = 'frequency', '18000 kHz', '9000 kHz', '4500 kHz', '2250 kHz', '1125 kHz', '562 kHz', '281 kHz', '140 kHz'
spi_option_1 = [1,2,3,4,5,6,7,8,9]
spi_tag_2 = 'data frame width in bits'
spi_option_2 = [8,16]
spi_tag_3 = 'data frame bit order', 'most significant bit first', 'least significant bit first'
spi_option_3 = [1,2]
spi_tag_4 = 'mode', '0', '1', '2', '3', '4'
spi_option_4 = [1,2,3,4]
spi_tag_5 = 'drive mode', 'push', 'external', 'embedded'
spi_option_5 = [1,2,3]
spi_tag_6 = 'SPI' # check_tag load it from yaml

# testing all spi combinations (takes 30 minutes)
t = list(itertools.product(spi_0, spi_1, spi_2, spi_3, spi_4, spi_5))
print(len(t))
for a in t:
    prot_settings_test('spi', a)

# yaml file, protocol, check string, list of lists
