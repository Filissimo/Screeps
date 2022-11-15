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
        if creep.memory.job == 'starter':
            define_starter_target(creep)
        elif creep.memory.job == 'miner':
            define_miner_targets(creep)
        elif creep.memory.job == 'lorry':
            define_lorry_target(creep)
        elif creep.memory.job == 'worker':
            define_worker_target(creep)
        elif creep.memory.job == 'defender':
            define_defender_targets(creep)
        if creep.memory.job[:10] == 'reservator':
            define_reservator_targets(creep)
        if creep.memory.job[:7] == 'stealer':
            define_stealer_targets(creep)


def run_starter(creep):
    if creep.memory.target:
        if creep.memory.duty == 'mining':
            actions.creep_mining(creep)
        elif creep.memory.duty == 'withdrawing_from_closest':
            actions.withdraw_from_closest(creep)
        elif creep.memory.duty == 'delivering_for_spawn':
            actions.delivering_for_spawning(creep)
        elif creep.memory.duty == 'building':
            actions.building(creep)
        elif creep.memory.duty == 'upgrading':
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
    if creep.memory.source and creep.memory.container and creep.memory.duty:
        if creep.memory.duty == 'mining':
            actions.miner_mines(creep)
        elif creep.memory.duty == 'to_closest_container':
            actions.miner_delivers(creep)
    else:
        define_miner_targets(creep)


def define_miner_targets(creep):
    if creep.memory.source and creep.memory.container:
        if creep.memory.duty == 'mining' and _.sum(creep.carry) > 42:
            creep.memory.duty = 'to_closest_container'
            creep.memory.target = 'to_closest_container'
        elif _.sum(creep.carry) <= 0:
            creep.memory.duty = 'mining'
            creep.memory.target = 'mining'
    else:
        sources = creep.room.find(FIND_SOURCES)
        for source in sources:
            container_near_mine = _(creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER and
                                   s.pos.inRangeTo(source, 2))) \
                .sample()
            if container_near_mine:
                miners = _.filter(creep.room.find(FIND_CREEPS),
                                  lambda c: c.memory.job == 'miner' and
                                            c.memory.container == container_near_mine.id and
                                            c.ticksToLive > 70)
                if len(miners) < 2:
                    creep.memory.container = container_near_mine.id
                    creep.memory.source = source.id


def run_worker(creep):
    if creep.memory.target:
        actions.paving_roads(creep)
        if creep.memory.duty == 'dismantling_road':
            actions.dismantling_road(creep)
        elif creep.memory.duty == 'withdrawing_from_closest':
            actions.withdraw_from_closest(creep)
        elif creep.memory.duty == 'mining':
            actions.creep_mining(creep)
        elif creep.memory.duty == 'repairing':
            actions.creep_repairing(creep)
        elif creep.memory.duty == 'building':
            actions.building(creep)
        elif creep.memory.duty == 'upgrading':
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
    if creep.memory.target:
        actions.paving_roads(creep)
        if creep.memory.duty == 'picking_up_tombstone':
            actions.pick_up_tombstone(creep)
        elif creep.memory.duty == 'withdrawing_from_fullest':
            actions.withdrawing_from_fullest(creep)
        elif creep.memory.duty == 'delivering_for_spawn':
            actions.delivering_for_spawning(creep)
        elif creep.memory.duty == 'delivering_to_emptiest':
            actions.delivering_to_from_memory(creep)
        elif creep.memory.duty == 'delivering_to_storage':
            actions.delivering_to_from_memory(creep)
    else:
        define_lorry_target(creep)


def define_lorry_target(creep):
    del creep.memory.duty
    del creep.memory.target
    if not duties_and_targets.define_lorry_to_pickup_tombstone(creep):
        if not duties_and_targets.define_fullest(creep):
            if not duties_and_targets.define_deliver_for_spawn_target(creep):
                if not duties_and_targets.define_emptiest(creep):
                    duties_and_targets.define_storage(creep)


def run_defender(creep):
    if creep.memory.duty:
        if creep.memory.duty == 'attacking':
            actions.attacking(creep)
        elif creep.memory.duty == 'defending':
            actions.defending(creep)
    else:
        define_defender_targets(creep)


def define_defender_targets(creep):
    if creep.memory.enemy and creep.memory.base:
        if creep.memory.duty == 'attacking':
            creep.memory.target = 'attacking'
        elif creep.memory.duty == 'defending':
            creep.memory.target = 'defending'
    else:
        enemy = creep.pos.findClosestByRange(FIND_HOSTILE_CREEPS)
        if enemy:
            creep.memory.duty = 'attacking'
            creep.memory.enemy = enemy.id
        else:
            creep.memory.duty = 'defending'
            creep.memory.base = creep.memory.home
            del creep.memory.enemy


def run_reservator(creep):
    if creep.memory.duty:
        if creep.memory.duty == 'go_to_flag':
            actions.going_to_flag(creep)
        elif creep.memory.duty == 'reserving':
            actions.reserving(creep)
    else:
        define_reservator_targets(creep)


def define_reservator_targets(creep):
    del creep.memory.duty
    del creep.memory.flag
    if not duties_and_targets.define_reservators_flag(creep):
        duties_and_targets.define_controller(creep)


def run_stealer(creep):
    actions.paving_roads(creep)
    if creep.memory.duty:
        if creep.memory.duty == 'go_to_flag':
            actions.going_to_flag(creep)
        elif creep.memory.duty == 'mining':
            actions.creep_mining(creep)
        elif creep.memory.duty == 'repairing':
            actions.creep_repairing(creep)
        elif creep.memory.duty == 'building':
            actions.building(creep)
        elif creep.memory.duty == 'going_home':
            actions.going_home(creep)
        elif creep.memory.duty == 'transferring_to_closest':
            actions.transferring_to_closest(creep)
    else:
        define_stealer_targets(creep)


def define_stealer_targets(creep):
    del creep.memory.duty
    del creep.memory.target
    del creep.memory.flag
    if not duties_and_targets.define_stealers_flag(creep):
        if not duties_and_targets.define_mining_target(creep):
            if not duties_and_targets.define_closest_to_transfer(creep):
                if not duties_and_targets.define_repairing_target(creep):
                    if not duties_and_targets.define_building_target(creep):
                        duties_and_targets.define_going_home(creep)
