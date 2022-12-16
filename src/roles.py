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
    if creep.memory.role != 'guard':
        if operations.not_fleeing(creep):
            if task and task != 'delivered_for_spawning':
                if task == 'withdraw_by_memory':
                    operations.paving_roads(creep)
                    operations.withdraw_by_memory(creep, cluster_memory)
                elif task == 'transfer_by_memory':
                    operations.paving_roads(creep)
                    operations.transfer_by_memory(creep, cluster_memory)
                    operations.accidentally_delivering_to_worker(creep)
                elif task == 'transfer_to_spawning_structure':
                    operations.paving_roads(creep)
                    operations.transfer_to_spawning_structure(creep, cluster_memory)
                elif task == 'worker_mining':
                    operations.worker_mining(creep, cluster_memory)
                elif task == 'miner_mining':
                    operations.miner_mining(creep)
                elif task == 'going_to_mining_place':
                    operations.paving_roads(creep)
                    operations.going_to_mining_place(creep)
                elif task == 'dismantling':
                    operations.dismantling(creep)
                elif task == 'repairing':
                    operations.paving_roads(creep)
                    operations.repairing(creep)
                elif task == 'building':
                    operations.paving_roads(creep)
                    operations.building(creep)
                elif task == 'upgrading':
                    operations.paving_roads(creep)
                    operations.upgrading(creep)
    else:
        if task:
            if task == 'defending':
                operations.defending(creep)
            elif task == 'attacking':
                operations.attacking(creep)


def run_creep(creep, cluster_memory):
    task = creep.memory.task
    if task:
        operate_creep(creep, cluster_memory, task)
        task_after = creep.memory.task
        if not task_after or task_after == 'defending':
            define_task_and_operate(creep, cluster_memory)
    else:
        define_task_and_operate(creep, cluster_memory)
    if not creep.memory.task:
        if not operations.move_away_from_creeps(creep):
            creep.say('?')
        operations.decrease_creeps_needed(creep)


def define_task_and_operate(creep, cluster_memory):
    tasks.define_task(creep, cluster_memory)
    task = creep.memory.task
    if task:
        operate_creep(creep, cluster_memory, task)
    else:
        if not operations.move_away_from_creeps(creep):
            creep.say('?')
