""" main handler """
from os import sys, path
sys.path.append(path.dirname(path.abspath(__file__)))

from lambdas.routes import (run_task, check_task, stop_task) #pylint:disable=E0401,C0413
from lambdas.exceptions import InvalidStateMachine #pylint:disable=E0401,C0413

def main(event, context):
    """ Handle the step function state call """
    # Get RPC call
    rpc = context.invoked_function_arn.split(':')[-1]

    if not 'next' in event:
        raise InvalidStateMachine("The machine does not contain a next state.")

    # Router
    router = {
        'run_task': run_task,
        'check_task': check_task,
        'stop_task': stop_task,
    }

    return router[rpc](event)
