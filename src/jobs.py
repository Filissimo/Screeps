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
    elif job == 'miner':
        run_miner(creep)
    elif job == 'worker':
        run_worker(creep)
    elif job == 'lorry':
        run_lorry(creep)
    elif job == 'defender':
        run_defender(creep)
    elif job == 'reservator':
        run_reservator(creep)
    elif job == 'stealer':
        run_stealer(creep)
    elif job == 'claimer':
        run_claimer(creep)
    elif job == 'spawn_builder':
        run_spawn_builder(creep)


def define_target(creep):
    if creep.memory != undefined:
        del creep.memory.path
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
        elif job == 'reservator':
            define_reservator_targets(creep)
        elif job == 'stealer':
            define_stealer_targets(creep)
        elif job == 'claimer':
            define_claimer_targets(creep)
        elif job == 'spawn_builder':
            define_spawn_builder_target(creep)


def run_starter(creep):
    if not actions.going_home(creep):
        target = creep.memory.target
        duty = creep.memory.duty
        if target and actions.not_fleeing(creep):
            actions.accidentally_delivering_for_spawning(creep)
            if duty == 'picking_up_tombstone':
                actions.pick_up_tombstone(creep)
            elif duty == 'mining':
                actions.creep_mining(creep)
            elif duty == 'withdrawing_from_closest':
                actions.withdraw_from_closest(creep)
                actions.paving_roads(creep)
            elif duty == 'delivering_for_spawn':
                actions.delivering_for_spawning(creep)
                actions.paving_roads(creep)
            elif duty == 'building':
                actions.building(creep)
            elif duty == 'upgrading':
                actions.upgrading(creep)
        else:
            define_starter_target(creep)


def define_starter_target(creep):
    creep.memory.work_place = False
    del creep.memory.duty
    del creep.memory.target
    if not duties_and_targets.define_creep_to_pickup_tombstone(creep):
        if not duties_and_targets.define_closest_to_withdraw(creep):
            if not duties_and_targets.define_mining_target(creep):
                if not duties_and_targets.define_deliver_for_spawn_target(creep):
                    if not duties_and_targets.define_emergency_upgrading_target(creep):
                        if not duties_and_targets.define_building_target(creep):
                            duties_and_targets.define_upgrading_target(creep)
    elif not creep.memory.target:
        home = Game.getObjectById(creep.memory.home)
        need_starters = home.memory.need_starters
        if need_starters > 2:
            home.memory.need_starters = need_starters - 0.05


def run_miner(creep):
    container = creep.memory.container
    source = creep.memory.source
    duty = creep.memory.duty
    if source and container and duty and actions.not_fleeing(creep):
        if duty == 'picking_up_tombstone':
            actions.pick_up_tombstone(creep)
        elif duty == 'mining':
            actions.miner_mines(creep)
        elif duty == 'go_to_workplace':
            actions.going_to_workplace(creep)
    else:
        define_miner_targets(creep)


def verify_miners_place(creep):
    creep_memory = creep.memory
    sources = creep.room.find(FIND_SOURCES)
    for source in sources:
        container = _.filter(source.pos.findInRange(FIND_STRUCTURES, 2),
                             lambda s: s.structureType == STRUCTURE_CONTAINER)[0]

        if container:
            miner = _.filter(creep.room.find(FIND_MY_CREEPS),
                             lambda c: c.memory.job == 'miner' and
                                       c.memory.source == source.id and
                                       c.memory.container == container.id and
                                       c.ticksToLive > 50)
            if len(miner) < 2:
                creep_memory.container = container.id
                creep_memory.source = source.id
    creep.memory = creep_memory


def define_miner_targets(creep):
    creep_memory = creep.memory
    if creep_memory.source and creep_memory.container:
        if not creep_memory.work_place and creep_memory.duty != 'picking_up_tombstone':
            creep_memory.duty = 'go_to_workplace'
            creep_memory.target = 'go_to_workplace'
        elif creep_memory.work_place:
            creep_memory.duty = 'mining'
            creep_memory.target = 'mining'
        else:
            creep_memory.duty = 'mining'
    else:
        verify_miners_place(creep)
    creep.memory = creep_memory


def run_worker(creep):
    if not actions.going_home(creep):
        target = creep.memory.target
        duty = creep.memory.duty
        if target and duty and actions.not_fleeing(creep):
            if duty == 'dismantling':
                actions.dismantling(creep)
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
    creep.memory.work_place = False
    del creep.memory.duty
    del creep.memory.target
    if not duties_and_targets.define_dismantling_target(creep):
        if not duties_and_targets.define_closest_to_withdraw(creep):
            if not duties_and_targets.define_mining_target(creep):
                if not duties_and_targets.define_repairing_target(creep):
                    if not duties_and_targets.define_emergency_upgrading_target(creep):
                        if not duties_and_targets.define_building_target(creep):
                            duties_and_targets.define_upgrading_target(creep)


def run_lorry(creep):
    target = creep.memory.target
    duty = creep.memory.duty
    # if not target:
    #     actions.move_away_from_creeps(creep)
    if target and actions.not_fleeing(creep):
        actions.accidentally_delivering_for_spawning(creep)
        if duty == 'picking_up_tombstone':
            actions.pick_up_tombstone(creep)
        elif duty == 'withdrawing_from_fullest':
            actions.withdrawing_from_memory(creep)
        elif duty == 'withdrawing_from_storage':
            actions.withdrawing_from_memory(creep)
        elif duty == 'delivering_for_spawn':
            actions.delivering_for_spawning(creep)
            actions.paving_roads(creep)
        elif duty == 'delivering_to_emptiest':
            actions.accidentally_delivering_to_worker(creep)
            actions.delivering_to_from_memory(creep)
            actions.paving_roads(creep)
        elif duty == 'delivering_to_storage':
            actions.delivering_to_from_memory(creep)
            actions.paving_roads(creep)
    else:
        define_lorry_target(creep)


def define_lorry_target(creep):
    creep.memory.work_place = False
    del creep.memory.duty
    del creep.memory.target
    if not duties_and_targets.define_creep_to_pickup_tombstone(creep):
        if not duties_and_targets.define_fullest(creep):
            if not duties_and_targets.define_storage_to_withdraw(creep):
                if not duties_and_targets.define_deliver_for_spawn_target(creep):
                    if not duties_and_targets.define_emptiest(creep):
                        duties_and_targets.define_storage_to_deliver(creep)
    if not creep.memory.target:
        actions.accidentally_delivering_to_worker(creep)
        actions.move_away_from_creeps(creep)


def run_defender(creep):
    duty = creep.memory.duty
    if duty:
        if duty == 'attacking':
            actions.attacking(creep)
        elif duty == 'defending' and not actions.move_away_from_creeps(creep):
            actions.defending(creep)
        elif duty == 'going_to_help':
            actions.going_to_help(creep)
    else:
        define_defender_targets(creep)


def define_defender_targets(creep):
    creep.memory.fleeing_creep = None
    enemy = creep.room.find(FIND_HOSTILE_CREEPS, {'filter': lambda e: e.owner.username != 'rep71Le'})
    if len(enemy) == 0:
        creep.memory.duty = 'defending'
    else:
        creep.memory.duty = 'attacking'


def run_reservator(creep):
    duty = creep.memory.duty
    if duty:
        if duty == 'go_to_flag':
            actions.going_to_flag(creep)
            actions.paving_roads(creep)
        elif duty == 'reserving':
            actions.reserving(creep)
            actions.paving_roads(creep)
    else:
        define_reservator_targets(creep)


def define_reservator_targets(creep):
    creep.memory.work_place = False
    del creep.memory.duty
    if not duties_and_targets.define_reservators_flag(creep):
        duties_and_targets.define_controller(creep)


def run_stealer(creep):
    target = creep.memory.target
    duty = creep.memory.duty
    if duty and target and actions.not_fleeing(creep):
        if duty == 'go_to_flag':
            actions.going_to_flag(creep)
            actions.paving_roads(creep)
        elif duty == 'picking_up_tombstone':
            actions.pick_up_tombstone(creep)
        elif duty == 'dismantling':
            actions.dismantling(creep)
        elif duty == 'mining':
            actions.creep_mining(creep)
            actions.paving_roads(creep)
        elif duty == 'repairing':
            actions.creep_repairing(creep)
            actions.paving_roads(creep)
        elif duty == 'building':
            actions.building(creep)
            actions.paving_roads(creep)
        elif duty == 'going_home':
            if not actions.going_home(creep):
                define_stealer_targets(creep)
        elif duty == 'transferring_to_closest':
            if not actions.going_home(creep):
                actions.transferring_to_closest(creep)
            actions.paving_roads(creep)
    else:
        define_stealer_targets(creep)


def define_stealer_targets(creep):
    creep.memory.work_place = False
    del creep.memory.duty
    del creep.memory.target
    if not duties_and_targets.define_closest_to_transfer(creep):
        if not duties_and_targets.define_going_to_flag(creep):
            if not duties_and_targets.define_creep_to_pickup_tombstone(creep):
                if not duties_and_targets.define_stealing_target(creep):
                    if not duties_and_targets.define_dismantling_target(creep):
                        if not duties_and_targets.define_repairing_target(creep):
                            if not duties_and_targets.define_building_target(creep):
                                duties_and_targets.define_going_home(creep)


def run_claimer(creep):
    duty = creep.memory.duty
    if duty:
        if duty == 'go_to_flag':
            actions.going_to_flag(creep)
        elif duty == 'claiming':
            actions.claiming(creep)
    else:
        define_claimer_targets(creep)


def define_claimer_targets(creep):
    del creep.memory.duty
    if not duties_and_targets.define_claimers_flag(creep):
        duties_and_targets.define_controller(creep)


def run_spawn_builder(creep):
    if actions.not_going_to_bs(creep):
        target = creep.memory.target
        duty = creep.memory.duty
        if target and duty and actions.not_fleeing(creep):
            if duty == 'picking_up_tombstone':
                actions.pick_up_tombstone(creep)
            elif duty == 'mining':
                actions.creep_mining(creep)
                actions.paving_roads(creep)
            elif duty == 'building':
                actions.building(creep)
                actions.paving_roads(creep)
            elif duty == 'upgrading':
                actions.upgrading(creep)
        else:
            define_spawn_builder_target(creep)


def define_spawn_builder_target(creep):
    creep.memory.work_place = False
    del creep.memory.duty
    del creep.memory.target
    if not duties_and_targets.define_creep_to_pickup_tombstone(creep):
        if not duties_and_targets.define_mining_target(creep):
            if not duties_and_targets.define_emergency_upgrading_target(creep):
                duties_and_targets.define_building_target(creep)
    if not creep.memory.target:
        flag = Game.flags['BS']
        if flag:
            need_spawn_builders = flag.memory.need_spawn_builders
            if need_spawn_builders > 2:
                flag.memory.need_spawn_builders = need_spawn_builders - 0.05
        else:
            creep.memory.job = 'starter'
            spawn = _(creep.room.find(FIND_STRUCTURES)).filter(lambda s: s.structureType == STRUCTURE_SPAWN).sample()
            if spawn:
                creep.memory.home = spawn.id
            del creep.memory.target
            del creep.memory.duty
    # if creep.room.energyCapacityAvailable > 0:
    #     creep.memory.job = 'starter'
    #     spawn = _(creep.room.find(FIND_STRUCTURES)).filter(lambda s: s.structureType == STRUCTURE_SPAWN).sample()
    #     creep.memory.home = spawn.id
    #     del creep.memory.target
    #     del creep.memory.duty
