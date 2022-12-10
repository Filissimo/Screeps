import tasks
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def role_runner(creep):
    task = creep.memory.task
    target = creep.memory.target
    if task and target:
        if task == 'withdraw_by_memory':
            tasks.withdraw_by_memory(creep)
        elif task == 'transfer_by_memory':
            tasks.transfer_by_memory(creep)
    else:
        tasks.define_task(creep)