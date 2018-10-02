""" custom exceptions """

class TaskException(Exception):
    """ Task exception """
    pass

class InvalidStateMachine(Exception):
    """ Invalid state machine was passed """
    pass
