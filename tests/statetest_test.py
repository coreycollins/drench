""" test for stepmock module """
import os
from scripts.statetest import StepMock

def test_aws_iop_example_one():
    """ replicate behavior seen on
    http://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-input-output-processing.html """
    input_data = {
        "title": "Numbers to add",
        "numbers": {"val1": 3, "val2": 4}
        }

    state = {
        "InputPath": "$.numbers",
        "ResultPath": "$.sum",
        "OutputPath": "$",
        "Type": "Pass",
        "Result":7
        }

    mocker = StepMock({}, {})

    post_process_data = mocker.run_pass(state, input_data)

    assert post_process_data == {
        "title": "Numbers to add",
        "numbers": {"val1": 3, "val2": 4},
        "sum": 7
    }

def test_aws_iop_example_two():
    """ replicate behavior seen on
    http://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-input-output-processing.html """
    input_data = {
        "title": "Numbers to add",
        "numbers": {"val1": 3, "val2": 4}
        }

    state = {
        "InputPath": "$.numbers",
        "ResultPath": "$.sum",
        "OutputPath": "$.sum",
        "Type": "Pass",
        "Result":7
        }

    mocker = StepMock({}, {})

    post_process_data = mocker.run_pass(state, input_data)

    assert post_process_data == 7

def test_choice():

    state = {
        "Type": "Choice",
        "Choices": [
            {
                "Next": "ThirdState",
                "Not": {
                    "NumericLessThan": 10,
                    "Variable": "$.message"
                }
            },
            {
                "Next": "SecondState",
                "NumericGreaterThan": 0,
                "Variable": "$.message"
            }
        ],
        "Default": "FourthState"
    }

    mocker = StepMock({}, {})
    lol = mocker.run_choice(state, {'message':11})
    assert lol == 'ThirdState'
    not_lol = mocker.run_choice(state, {'message':5})
    assert not_lol == 'SecondState'
    default = mocker.run_choice(state, {'message':-1})
    assert default == 'FourthState'

def test_get_result():
    """ test that output is extracted correctly from stdout """
    term_stdout = """[root - INFO - 2017-09-29 09:16:44,442] Event: {u'message': u'boop'}
[root - INFO - 2017-09-29 09:16:44,442] START RequestId: 069c8333-aca8-4543-8597-069c08543920
[root - INFO - 2017-09-29 09:16:44,442] END RequestId: 069c8333-aca8-4543-8597-069c08543920
[root - INFO - 2017-09-29 09:16:44,442] RESULT:
{"message": "beep boop"}
[root - INFO - 2017-09-29 09:16:44,442] REPORT RequestId: 069c8333-aca8-4543-8597-069c08543920	Duration: 0.14 ms"""

    mocker = StepMock({}, {})
    output_data = mocker.get_result(term_stdout)
    assert output_data == {"message": "beep boop"}

def test_execute():
    machine = {"States": {"Only": {"Type": "Succeed"}}, "StartAt":"Only"}
    mocker = StepMock(machine, {})
    mocker.start() #doesn't throw error

def test_task():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    test_labmda_path = os.path.join(dir_path, 'example_lambda.py')

    mocker = StepMock({}, {})

    state = {'Type':'Task', 'Resource':test_labmda_path}

    out = mocker.run_task(state, 7)

    assert out == 7
