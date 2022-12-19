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


def operate_creep(creep_real, cluster_memory, task, creep_virtual):
    if creep_virtual.role != 'guard':
        if operations.not_fleeing(creep_real):
            if task and task != 'delivered_for_spawning':
                if task == 'withdraw_by_memory':
                    operations.paving_roads(creep_real)
                    operations.withdraw_by_memory(creep_real, cluster_memory)
                elif task == 'transfer_by_memory':
                    operations.paving_roads(creep_real)
                    operations.transfer_by_memory(creep_real, cluster_memory)
                    operations.accidentally_delivering_to_worker(creep_real)
                elif task == 'transfer_to_spawning_structure':
                    operations.paving_roads(creep_real)
                    operations.transfer_to_spawning_structure(creep_real, cluster_memory)
                elif task == 'worker_mining':
                    operations.worker_mining(creep_real, cluster_memory)
                elif task == 'miner_mining':
                    operations.miner_mining(creep_real, creep_virtual)
                elif task == 'going_to_mining_place':
                    operations.paving_roads(creep_real)
                    operations.going_to_mining_place(creep_real, creep_virtual)
                elif task == 'dismantling':
                    operations.dismantling(creep_real)
                elif task == 'repairing':
                    operations.paving_roads(creep_real)
                    operations.repairing(creep_real)
                elif task == 'building':
                    operations.paving_roads(creep_real)
                    operations.building(creep_real)
                elif task == 'upgrading':
                    operations.paving_roads(creep_real)
                    operations.upgrading(creep_real)
                elif task == 'reserving':
                    operations.paving_roads(creep_real)
                    operations.reserving(creep_real)
    else:
        if task:
            if task == 'defending':
                operations.defending(creep_real)
            elif task == 'attacking':
                operations.attacking(creep_real)


def run_creep(creep_real, creep_virtual, cluster_memory):
    task = creep_virtual.task
    if task:
        operate_creep(creep_real, cluster_memory, task, creep_virtual)
        task_after = creep_real.memory.task
        if not task_after or task_after == 'defending':
            define_task_and_operate(creep_real, creep_virtual, cluster_memory)
    else:
        define_task_and_operate(creep_real, creep_virtual, cluster_memory)
    if not creep_virtual.task:
        if not operations.move_away_from_creeps(creep_real):
            creep_real.say('?')
        operations.decrease_creeps_needed(creep_virtual)


def define_task_and_operate(creep_real, creep_virtual, cluster_memory):
    tasks.define_task(creep_real, cluster_memory, creep_virtual)
    task = creep_real.memory.task
    if task:
        operate_creep(creep_real, cluster_memory, task, creep_virtual)
    else:
        if not operations.move_away_from_creeps(creep_real):
            creep_real.say('?')
