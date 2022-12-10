from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def define_hauler_task(creep):
    pass


def define_task(creep):
    role = creep.memory.role
    if role == 'hauler':
        define_hauler_task(creep)


def transfer_by_memory(creep):
    return None


def withdraw_by_memory(creep):
    return None
