import operations
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def operate_creep(creep, cluster_memory, task):
    if task == 'withdraw_by_memory':
        operations.withdraw_by_memory(creep, cluster_memory)
    elif task == 'transfer_by_memory':
        operations.transfer_by_memory(creep, cluster_memory)
    elif task == 'transfer_to_spawning_structure':
        operations.transfer_to_spawning_structure(creep)
    elif task == 'withdraw_from_closest':
        operations.withdraw_from_closest(creep)
    elif task == 'worker_mining':
        operations.worker_mining(creep)
    elif task == 'dismantling':
        operations.dismantling(creep)
    elif task == 'repairing':
        operations.repairing(creep)
    elif task == 'building':
        operations.building(creep)
    elif task == 'upgrading':
        operations.upgrading(creep)
