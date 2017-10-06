#!/usr/bin/env python2.7
""" utility for mocking AWS step functions in local development"""
import sys
import json
import uuid
import subprocess
import os
import re
import shutil
import argparse
from zipfile import ZipFile

import requests
import boto3

from jsonpath_ng import jsonpath, parse


def addFields(fields, data):
    if (len(fields) > 0):
        first = fields[0]
        if (first not in data):
            data[first] = addFields(fields[1:], {})
            return data
        else:
            data[first] = addFields(fields[1:], data[first])
            return data
    else:
        return None

def process_input_path(func):

    def wrapper(_, state, indata):
        data = indata
        if ('InputPath' in state):
            jsonpath_exp = parse(state['InputPath'])
            result = jsonpath_exp.find(data)
            if (len(result) > 0):
                data = result[0].value
        return func(_, state, data)

    return wrapper

def process_result_path(func):

    def wrapper(_, state, indata):
        data = indata
        out = func(_, state, data)

        try:
            if ('ResultPath' in state):
                expr = parse(state['ResultPath'])

                result = expr.find(data)
                if (len(result) > 0):
                    out = expr.update(data, out)
                else:
                    fields = str(expr).split('.')[1:]
                    data = addFields(fields, data)
                    out = expr.update(data, out)
        except TypeError:
            raise BaseException("Invalid ResultPath")

        return out

    return wrapper

def process_output_path(func):

    def wrapper(_, state, indata):
        data = indata
        out = func(_, state, data)
        if ('OutputPath' in state):
            jsonpath_exp = parse(state['OutputPath'])
            result = jsonpath_exp.find(out)
            if (len(result) > 0):
                out = result[0].value
        return out

    return wrapper

    #
    # """ handle InputPath field according to AWS rules """
    # if "InputPath" in state:
    #     input_path = state["InputPath"].replace("$.", "")
    #     if "[" in input_path:
    #         print "indexing InputPath not supported in stepmock"
    #
    #     if input_path is None:
    #         return json.loads("{}")
    #
    #     if input_path == "$":
    #         return input_path
    #
    #     return input_data[input_path]
    #
    # return input_data

class StepMock(object):
    """ main class """
    def __init__(self, state_machine, initial_input_data):

        self.state_machine = state_machine
        self.initial_input_data = initial_input_data

        self.result_re = re.compile(r'(?<=RESULT:\n)(.*)\n(?=^\[)', re.MULTILINE | re.DOTALL)

        self.comparison_operators = {
            'And': lambda x, y: x and y,
            'BooleanEquals': lambda x, y: x == y,
            'Not': lambda x, y: not x == y,
            'NumericEquals': lambda x, y: x == y,
            'NumericGreaterThan': lambda x, y: x > y,
            'NumericGreaterThanEquals': lambda x, y: x >= y,
            'NumericLessThan': lambda x, y: x < y,
            'NumericLessThanEquals': lambda x, y: x <= y,
            'Or': lambda x, y: x or y,
            'StringEquals': lambda x, y: x == y,
            'StringGreaterThan': lambda x, y: x > y,
            'StringGreaterThanEquals': lambda x, y: x >= y,
            'StringLessThan': lambda x, y: x < y,
            'StringLessThanEquals': lambda x, y: x <= y,
            'TimestampEquals': lambda x, y: x == y,
            'TimestampGreaterThan': lambda x, y: x > y,
            'TimestampGreaterThanEquals': lambda x, y: x >= y,
            'TimestampLessThan': lambda x, y: x < y,
            'TimestampLessThanEquals': lambda x, y: x <= y,
        }

    def start(self):
        """ begin execution """
        gen = self.__executor(self.initial_input_data)

        # start first state
        gen.next()
        nxt = gen.send(self.state_machine["StartAt"])

        # if there is a next state, run
        while(nxt):
            gen.next()
            nxt = gen.send(nxt)

    def __executor(self, indata):
        data = indata
        while(True):
            name = yield
            state = self.state_machine['States'][name]
            state_type = state['Type']
            print "Running %s step %s" % (state_type, name)

            choose = None
            if state_type == "Succeed":
                print('Succeed')
            elif state_type == "Fail":
                print('Fail')
            elif state_type == "Pass":
                data = self.run_pass(state, data)
            elif state_type == "Choice":
                choose = self.run_choice(state, data)
                yield choose
            elif state_type == "Task":
                data = self.run_task(state, data)
            else:
                print "Step type %s not yet implemented in stepmock" % state_type

            # Send next state
            if ('Next' in state):
                yield state['Next']
            elif (state_type != 'Choice'):
                yield

    @process_output_path
    @process_result_path
    @process_input_path
    def run_pass(self, state, input_data):
        """ process result & output paths """
        output_data = input_data
        if "Result" in state:
            output_data = state["Result"]

        return output_data

    @process_output_path
    @process_input_path
    def run_choice(self, state, input_data):
        """ evaluate choices, if one is true return it, return default if none are """
        for choice in state["Choices"]:
            if self.choose(choice, input_data):
                return choice["Next"]
        return state["Default"] # potential KeyError desireable for emulating AWS

    def choose(self, choice, input_data):
        """ evaluate a choice to true or false """

        if "Not" in choice:
            return not self.choose(choice["Not"], input_data)

        elif "And" in choice:
            for sub_choice in choice["And"]:
                if not self.choose(sub_choice, input_data):
                    return False
                return True

        elif "Or" in choice:
            for sub_choice in choice["Or"]:
                if self.choose(sub_choice, input_data):
                    return True
                return False

        else:
            expr = parse(choice["Variable"])
            result = expr.find(input_data)
            if (result):
                for field in choice:
                    if field in self.comparison_operators:
                        return self.comparison_operators[field](result[0].value, choice[field])
            else:
                raise BaseException("Choice variable path not valid {}".format(expr))


    @process_output_path
    @process_result_path
    @process_input_path
    def run_task(self, state, input_data):
        """ download and exec labmda func locally """
        resource = state["Resource"]

        payload = '/tmp/%s.json' % uuid.uuid4().hex
        with open(payload, 'w') as f:
            json.dump(input_data, f)

        output_data = self.execute_lambda(resource, payload)

        return output_data


    def execute_lambda(self, lambda_file, event_file):
        """ call python local labmda and forward success / failure """
        try:
            output = subprocess.check_output(
                [
                    "python-lambda-local",
                    '--timeout',
                    '600', # 10 minute timeout
                    lambda_file,
                    event_file
                    ]
                )

        except subprocess.CalledProcessError as err: # catch just for printing
            raise BaseException("Failed to run local lambda. Output: {}".format(err.output))

        return self.get_result(output)

    def get_result(self, output):
        """ extract result from python-lambda-local output """
        match = self.result_re.findall(output)
        if match:
            try:
                return json.loads(match[0])
            except ValueError:
                return match[0]
        return {}


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("state_machine")
    parser.add_argument("input_data")
    args = parser.parse_args()

    if (os.path.isfile(args.state_machine)):
        with open(args.state_machine) as f:
            STATE_MACHINE = json.load(f)
    else:
        STATE_MACHINE = json.loads(args.state_machine)

    if (os.path.isfile(args.input_data)):
        with open(args.input_data) as f:
            INITIAL_INPUT_DATA = json.load(f)
    else:
        INITIAL_INPUT_DATA = json.loads(args.input_data)

    StepMock(state_machine=STATE_MACHINE, initial_input_data=INITIAL_INPUT_DATA).start()
