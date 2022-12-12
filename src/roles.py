import operations
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


def operate_creep(creep, cluster_memory, task):
    if task and task != 'delivered_for_spawning':
        operations.paving_roads(creep)
        if task == 'withdraw_by_memory':
            operations.withdraw_by_memory(creep, cluster_memory)
        elif task == 'transfer_by_memory':
            operations.transfer_by_memory(creep, cluster_memory)
        elif task == 'transfer_to_spawning_structure':
            operations.transfer_to_spawning_structure(creep, cluster_memory)
        elif task == 'withdraw_from_closest':
            operations.withdraw_from_closest(creep)
        elif task == 'worker_mining':
            operations.worker_mining(creep, cluster_memory)
        elif task == 'dismantling':
            operations.dismantling(creep)
        elif task == 'repairing':
            operations.repairing(creep)
        elif task == 'building':
            operations.building(creep)
        elif task == 'upgrading':
            operations.upgrading(creep)


def run_creep(creep, cluster_memory):
    task = creep.memory.task
    # creep_tasks = creep.name + ' - Task in memory: ' + task + '. '
    if task:
        operate_creep(creep, cluster_memory, task)
        task_after = creep.memory.task
        # creep_tasks = creep_tasks + 'Task in memory after operating: ' + task_after + '. '
        # if task != task_after:
        # creep_tasks = '   !!!  ' + creep_tasks
        if not task_after:
            tasks.define_task(creep, cluster_memory)
            new_task = creep.memory.task
            # creep_tasks = creep_tasks + 'New task after operating: ' + new_task + '. '
            if new_task:
                operate_creep(creep, cluster_memory, new_task)
            else:
                if not operations.move_away_from_creeps(creep):
                    creep.say('?')
    else:
        tasks.define_task(creep, cluster_memory)
        brand_new_task = creep.memory.task
        # creep_tasks = '                !!!    ' + creep_tasks + \
        #               'New task because there was no task in memory: ' + brand_new_task + '. '
        if brand_new_task:
            operate_creep(creep, cluster_memory, brand_new_task)
        else:
            if not operations.move_away_from_creeps(creep):
                creep.say('?')

    # print(creep_tasks)
