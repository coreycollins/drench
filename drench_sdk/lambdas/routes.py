""" rpc routes """
import re
import jsonpath_ng
from .tasks import (GlueTask, BatchTask)
from .exceptions import InvalidStateMachine

def _find_subs(dic, base):
    ''' Substitute params from the event dict '''
    for key, val in dic.items(): #pylint:disable=R1702
        if isinstance(val, dict):
            dic[key] = _find_subs(dic[key], base)
        else:
            try:
                if isinstance(val, str):
                    new_val = val
                    for match in re.finditer(r'\{\{(\$[a-zA-Z_.]*)\}\}', val):

                        if val == match[0]:
                            expr = jsonpath_ng.parse(match[1])
                            new_val = expr.find(base)[0].value
                        else:
                            expr = jsonpath_ng.parse(match[1])
                            repl = expr.find(base)[0].value
                            new_val = new_val.replace(match[0], str(repl))

                    dic[key] = str(new_val)
            except: #pylint:disable=bare-except
                pass
    return dic

def _get_task_class(task_type):
    default = {
        'glue': GlueTask,
        'batch': BatchTask
    }

    # TODO: Allow for plugins
    tasks = default

    if task_type and task_type in tasks:
        return tasks[task_type]
    else:
        raise InvalidStateMachine('No type found for the task.')

def run_task(event):
    """ Run a asynchronous task on AWS """
    if not 'next' in event:
        raise InvalidStateMachine("The machine does not contain a next state.")

    klass = _get_task_class(event['next'].get('type', None))

    params = _find_subs(event['next'].get('params', {}), event)

    return klass().start(params)

def check_task(event):
    """ Check the status of an asynchronous taks on AWS """
    klass = _get_task_class(event['next'].get('type', None))

    if 'identifiers' not in event['result']:
        raise InvalidStateMachine('No identifiers found for the task.')

    identifiers = event['result']['identifiers']
    return klass().check(identifiers)

def stop_task(event):
    """ Stop a task on AWS """
    klass = _get_task_class(event['next'].get('type', None))

    if 'identifiers' not in event['result']:
        raise InvalidStateMachine('No identifiers found for the task.')

    identifiers = event['result']['identifiers']
    return klass().stop(identifiers)
