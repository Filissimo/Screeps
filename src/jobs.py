from defs import *
from src import actions, duties_and_targets

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def job_runner(creep):
    job = creep.memory.job
    if job == 'starter':
        run_starter(creep)
    if job == 'miner':
        run_miner(creep)
    if job == 'worker':
        run_worker(creep)
    if job == 'lorry':
        run_lorry(creep)
    if job == 'defender':
        run_defender(creep)
    if job[:10] == 'reservator':
        run_reservator(creep)
    if job[:7] == 'stealer':
        run_stealer(creep)


def define_target(creep):
    if creep.memory != undefined:
        job = creep.memory.job
        if job == 'starter':
            define_starter_target(creep)
        elif job == 'miner':
            define_miner_targets(creep)
        elif job == 'lorry':
            define_lorry_target(creep)
        elif job == 'worker':
            define_worker_target(creep)
        elif job == 'defender':
            define_defender_targets(creep)
        if job[:10] == 'reservator':
            define_reservator_targets(creep)
        if job[:7] == 'stealer':
            define_stealer_targets(creep)


def run_starter(creep):
    target = creep.memory.target
    duty = creep.memory.duty
    if target and actions.not_fleeing(creep):
        actions.accidentally_delivering_for_spawning(creep)
        if duty == 'mining':
            actions.creep_mining(creep)
        elif duty == 'withdrawing_from_closest':
            actions.withdraw_from_closest(creep)
        elif duty == 'delivering_for_spawn':
            actions.delivering_for_spawning(creep)
        elif duty == 'building':
            actions.building(creep)
        elif duty == 'upgrading':
            actions.upgrading(creep)
    else:
        define_starter_target(creep)


def define_starter_target(creep):
    del creep.memory.duty
    del creep.memory.target
    if not duties_and_targets.define_closest_to_withdraw(creep):
        if not duties_and_targets.define_mining_target(creep):
            if not duties_and_targets.define_deliver_for_spawn_target(creep):
                if not duties_and_targets.define_building_target(creep):
                    duties_and_targets.define_upgrading_target(creep)


def run_miner(creep):
    container = creep.memory.container
    source = creep.memory.source
    duty = creep.memory.duty
    if source and container and duty and actions.not_fleeing(creep):
        if duty == 'mining':
            actions.miner_mines(creep)
        elif duty == 'to_closest_container':
            actions.miner_delivers(creep)
    else:
        define_miner_targets(creep)


def define_miner_targets(creep):
    creep_memory = creep.memory
    if creep_memory.source and creep_memory.container:
        if creep_memory.duty == 'mining' and _.sum(creep.carry) > 42:
            creep_memory.duty = 'to_closest_container'
            creep_memory.target = 'to_closest_container'
        elif _.sum(creep.carry) <= 0:
            creep_memory.duty = 'mining'
            creep_memory.target = 'mining'
    else:
        sources = creep.room.find(FIND_SOURCES)
        for source in sources:
            container_near_mine = _(creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER and
                                   s.pos.inRangeTo(source, 2))) \
                .sample()
            if container_near_mine:
                miners = _.filter(creep.room.find(FIND_MY_CREEPS),
                                  lambda c: c.memory.job == 'miner' and
                                            c.memory.container == container_near_mine.id and
                                            c.ticksToLive > 70)
                if len(miners) < 2:
                    creep_memory.container = container_near_mine.id
                    creep_memory.source = source.id
    creep.memory = creep_memory


def run_worker(creep):
    target = creep.memory.target
    duty = creep.memory.duty
    if target and actions.not_fleeing(creep):
        if duty == 'dismantling_road':
            actions.dismantling_wall_for_stealing(creep)
        elif duty == 'withdrawing_from_closest':
            actions.withdraw_from_closest(creep)
        elif duty == 'mining':
            actions.creep_mining(creep)
        elif duty == 'repairing':
            actions.creep_repairing(creep)
        elif duty == 'building':
            actions.building(creep)
        elif duty == 'upgrading':
            actions.upgrading(creep)
    else:
        define_worker_target(creep)


def define_worker_target(creep):
    del creep.memory.duty
    del creep.memory.target
    if not duties_and_targets.define_closest_to_withdraw(creep):
        if not duties_and_targets.define_mining_target(creep):
            if not duties_and_targets.define_repairing_target(creep):
                if not duties_and_targets.define_building_target(creep):
                    duties_and_targets.define_upgrading_target(creep)


def run_lorry(creep):
    target = creep.memory.target
    duty = creep.memory.duty
    if target and actions.not_fleeing(creep):
        actions.paving_roads(creep)
        actions.accidentally_delivering_for_spawning(creep)
        if duty == 'picking_up_tombstone':
            actions.pick_up_tombstone(creep)
        elif duty == 'withdrawing_from_fullest':
            actions.withdrawing_from_memory(creep)
        elif duty == 'withdrawing_from_storage':
            actions.withdrawing_from_memory(creep)
        elif duty == 'delivering_for_spawn':
            actions.delivering_for_spawning(creep)
        elif duty == 'delivering_to_emptiest':
            actions.delivering_to_from_memory(creep)
        elif duty == 'delivering_to_storage':
            actions.delivering_to_from_memory(creep)
    else:
        define_lorry_target(creep)


def define_lorry_target(creep):
    del creep.memory.duty
    del creep.memory.target
    if not duties_and_targets.define_creep_to_pickup_tombstone(creep):
        if not duties_and_targets.define_fullest(creep):
            if not duties_and_targets.define_storage_to_withdraw(creep):
                if not duties_and_targets.define_deliver_for_spawn_target(creep):
                    if not duties_and_targets.define_emptiest(creep):
                        duties_and_targets.define_storage_to_deliver(creep)


def run_defender(creep):
    duty = creep.memory.duty
    if duty:
        if duty == 'attacking':
            actions.attacking(creep)
        elif duty == 'defending':
            actions.defending(creep)
        elif duty == 'going_to_help':
            actions.going_to_help(creep)
    else:
        define_defender_targets(creep)


def define_defender_targets(creep):
    creep.memory.fleeing_creep = None
    enemy = creep.room.find(FIND_HOSTILE_CREEPS)
    if len(enemy) == 0:
        creep.memory.duty = 'defending'
    else:
        creep.memory.duty = 'attacking'


def run_reservator(creep):
    duty = creep.memory.duty
    if duty:
        if duty == 'go_to_flag':
            actions.going_to_flag(creep)
        elif duty == 'reserving':
            actions.reserving(creep)
    else:
        define_reservator_targets(creep)


def define_reservator_targets(creep):
    del creep.memory.duty
    del creep.memory.flag
    if not duties_and_targets.define_reservators_flag(creep):
        duties_and_targets.define_controller(creep)


def run_stealer(creep):
    target = creep.memory.target
    duty = creep.memory.duty
    if duty and target and actions.not_fleeing(creep):
        actions.paving_roads(creep)
        if duty == 'go_to_flag':
            actions.going_to_flag(creep)
        elif duty == 'picking_up_tombstone':
            actions.pick_up_tombstone(creep)
        elif duty == 'working_with_wall':
            actions.dismantling_wall_for_stealing(creep)
        elif duty == 'mining':
            actions.creep_mining(creep)
            duties_and_targets.define_stealers_needed(creep)
        elif duty == 'repairing':
            actions.creep_repairing(creep)
        elif duty == 'building':
            actions.building(creep)
        elif duty == 'going_home':
            actions.going_home(creep)
        elif duty == 'transferring_to_closest':
            actions.transferring_to_closest(creep)
    else:
        define_stealer_targets(creep)


def define_stealer_targets(creep):
    del creep.memory.duty
    del creep.memory.target
    del creep.memory.flag
    if not duties_and_targets.define_stealers_flag(creep):
        if not duties_and_targets.define_creep_to_pickup_tombstone(creep):
            if not duties_and_targets.define_stealing_target(creep):
                if not duties_and_targets.define_wall(creep):
                    if not duties_and_targets.define_closest_to_transfer(creep):
                        if not duties_and_targets.define_repairing_target(creep):
                            if not duties_and_targets.define_building_target(creep):
                                duties_and_targets.define_going_home(creep)
