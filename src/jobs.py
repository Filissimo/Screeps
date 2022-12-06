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
    elif job == 'steaminer':
        run_steaminer(creep)
    elif job == 'worker':
        run_worker(creep)
    elif job == 'lorry':
        run_lorry(creep)
    elif job == 'truck':
        run_truck(creep)
    elif job == 'defender':
        run_defender(creep)
    elif job == 'offender':
        run_offender(creep)
    elif job == 'healer':
        run_healer(creep)
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
        creep.memory.work_place = False
        del creep.memory.path
        job = creep.memory.job
        if job == 'starter':
            define_starter_target(creep)
        elif job == 'miner':
            define_miner_targets(creep)
        elif job == 'steaminer':
            define_steaminer_targets(creep)
        elif job == 'lorry':
            define_lorry_target(creep)
        elif job == 'truck':
            define_truck_target(creep)
        elif job == 'worker':
            define_worker_target(creep)
        elif job == 'defender':
            define_defender_targets(creep)
        elif job == 'offender':
            define_offender_targets(creep)
        elif job == 'healer':
            define_healer_targets(creep)
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
    del creep.memory.duty
    del creep.memory.target
    if not duties_and_targets.define_creep_to_pickup_tombstone(creep):
        if not duties_and_targets.define_closest_to_withdraw(creep):
            if not duties_and_targets.define_mining_target(creep):
                if not duties_and_targets.define_deliver_for_spawn_target(creep):
                    if not duties_and_targets.define_emergency_upgrading_target(creep):
                        if not duties_and_targets.define_building_target(creep):
                            duties_and_targets.define_upgrading_target(creep)
    if not creep.memory.target:
        actions.move_away_from_creeps(creep)
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
                             lambda s: s.structureType == STRUCTURE_CONTAINER
                                       or s.structureType == STRUCTURE_LINK)[0]
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
        if creep.pos.isNearTo(Game.getObjectById(creep_memory.source)) and \
                creep.pos.isNearTo(Game.getObjectById(creep_memory.container)):
            creep_memory.work_place = True
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


def run_steaminer(creep):
    container = creep.memory.container
    source = creep.memory.source
    duty = creep.memory.duty
    flag = creep.memory.flag
    if flag and source and container and duty and actions.not_fleeing(creep):
        if duty == 'picking_up_tombstone':
            actions.pick_up_tombstone(creep)
        elif duty == 'mining':
            actions.miner_mines(creep)
        elif duty == 'go_to_workplace':
            actions.going_to_workplace(creep)
    else:
        define_steaminer_targets(creep)


def verify_steaminers_place(creep):
    creep_memory = creep.memory
    home = Game.getObjectById(creep.memory.home)
    for flag_name in Object.keys(Game.flags):
        if flag_name[:6] == 'Steal' + home.name[5:6]:
            flag = Game.flags[flag_name]
            if flag.room:
                sources = flag.room.find(FIND_SOURCES)
                for source in sources:
                    container = _.filter(source.pos.findInRange(FIND_STRUCTURES, 2),
                                         lambda s: s.structureType == STRUCTURE_CONTAINER)[0]
                    if container:
                        miners_in_flag_room = _.filter(flag.room.find(FIND_MY_CREEPS),
                                                       lambda c: c.memory.job == 'steaminer' and
                                                                 c.memory.source == source.id and
                                                                 c.memory.container == container.id and
                                                                 c.ticksToLive > 50)
                        home = Game.getObjectById(creep.memory.home)
                        miners_in_home_room = _.filter(home.room.find(FIND_MY_CREEPS),
                                                       lambda c: c.memory.job == 'steaminer' and
                                                                 c.memory.source == source.id and
                                                                 c.memory.container == container.id and
                                                                 c.ticksToLive > 50)
                        miners = len(miners_in_flag_room) + len(miners_in_home_room)
                        if miners < 2:
                            creep_memory.flag = flag_name
                            creep_memory.container = container.id
                            creep_memory.source = source.id
    creep.memory = creep_memory


def define_steaminer_targets(creep):
    creep_memory = creep.memory
    if creep_memory.source and creep_memory.container:
        if creep.pos.isNearTo(Game.getObjectById(creep_memory.source)) and \
                creep.pos.isNearTo(Game.getObjectById(creep_memory.container)):
            creep_memory.work_place = True
        if not creep_memory.work_place and creep_memory.duty != 'picking_up_tombstone':
            creep_memory.duty = 'go_to_workplace'
            creep_memory.target = 'go_to_workplace'
        elif creep_memory.work_place:
            creep_memory.duty = 'mining'
            creep_memory.target = 'mining'
        else:
            creep_memory.duty = 'mining'
    else:
        verify_steaminers_place(creep)
    creep.memory = creep_memory

    if not creep.memory.target:
        actions.move_away_from_creeps(creep)


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
                actions.accidentally_delivering_for_spawning(creep)
                actions.upgrading(creep)
        else:
            define_worker_target(creep)


def define_worker_target(creep):
    del creep.memory.duty
    del creep.memory.target
    if not duties_and_targets.define_dismantling_target(creep):
        if not duties_and_targets.define_closest_to_withdraw(creep):
            if not duties_and_targets.define_mining_target(creep):
                if not duties_and_targets.define_repairing_target(creep):
                    if not duties_and_targets.define_emergency_upgrading_target(creep):
                        if not duties_and_targets.define_building_target(creep):
                            duties_and_targets.define_upgrading_target(creep)
    if not creep.memory.target:
        actions.move_away_from_creeps(creep)


def run_lorry(creep):
    duty = creep.memory.duty
    target = creep.memory.target
    if target and actions.not_fleeing(creep):
        if duty == 'picking_up_tombstone':
            actions.pick_up_tombstone(creep)
            actions.pick_up_energy(creep)
            actions.accidentally_delivering_for_spawning(creep)
        elif duty == 'going_home':
            actions.unloading_lorry(creep)
            actions.paving_roads(creep)
        elif duty == 'withdrawing_from_fullest':
            actions.withdrawing_from_memory(creep)
            actions.pick_up_energy(creep)
        elif duty == 'withdrawing_from_link':
            actions.withdrawing_from_memory(creep)
            actions.pick_up_energy(creep)
        elif duty == 'withdrawing_from_stealing':
            actions.withdrawing_from_memory(creep)
            actions.pick_up_energy(creep)
        elif duty == 'withdrawing_from_terminal':
            actions.withdrawing_from_memory(creep)
            actions.pick_up_energy(creep)
        elif duty == 'withdrawing_from_storage':
            actions.withdrawing_from_memory(creep)
            actions.pick_up_energy(creep)
        elif duty == 'delivering_for_spawn':
            actions.delivering_for_spawning(creep)
            actions.pick_up_energy(creep)
            actions.accidentally_delivering_for_spawning(creep)
            actions.paving_roads(creep)
        elif duty == 'delivering_to_tower':
            actions.accidentally_delivering_for_spawning(creep)
            actions.accidentally_delivering_to_worker(creep)
            actions.delivering_to_from_memory(creep)
            actions.paving_roads(creep)
        elif duty == 'delivering_to_emptiest':
            actions.accidentally_delivering_to_worker(creep)
            actions.accidentally_delivering_for_spawning(creep)
            actions.delivering_to_from_memory(creep)
            actions.paving_roads(creep)
        elif duty == 'helping_workers':
            actions.helping_workers(creep)
        elif duty == 'transferring_to_link':
            actions.accidentally_delivering_for_spawning(creep)
            actions.accidentally_delivering_to_worker(creep)
            actions.delivering_to_from_memory(creep)
            actions.paving_roads(creep)
        elif duty == 'delivering_to_terminal':
            actions.accidentally_delivering_for_spawning(creep)
            actions.accidentally_delivering_to_worker(creep)
            actions.delivering_to_from_memory(creep)
            actions.paving_roads(creep)
        elif duty == 'delivering_to_storage':
            actions.accidentally_delivering_for_spawning(creep)
            actions.accidentally_delivering_to_worker(creep)
            actions.delivering_to_from_memory(creep)
            actions.paving_roads(creep)
    else:
        define_lorry_target(creep)


def define_lorry_target(creep):
    del creep.memory.duty
    del creep.memory.target
    if creep.name[:5] == 'truck' and creep.ticksToLive > 300:
        creep.memory.job = 'truck'
    if not duties_and_targets.define_creep_to_pickup_tombstone(creep):
        if not duties_and_targets.define_fullest(creep):
            if not duties_and_targets.define_link_to_withdraw(creep):
                if not duties_and_targets.define_stealing_container(creep):
                    if not duties_and_targets.define_creep_to_pickup_tombstone(creep):
                        if not duties_and_targets.define_storage_to_withdraw(creep):
                            if not duties_and_targets.define_terminal_to_withdraw(creep):
                                if not duties_and_targets.define_going_home(creep):
                                    if not duties_and_targets.define_tower(creep):
                                        if not duties_and_targets.define_deliver_for_spawn_target(creep):
                                            if not duties_and_targets.define_emptiest(creep):
                                                if not duties_and_targets.define_link_to_transfer(creep):
                                                    if not duties_and_targets.define_terminal_to_deliver(creep):
                                                        duties_and_targets.define_storage_to_deliver(creep)
    if not creep.memory.target:
        if creep.room != Game.getObjectById(creep.memory.home).room:
            creep.memory.target = 'home'
            creep.memory.duty = 'going_home'
        actions.move_away_from_creeps(creep)
        actions.accidentally_delivering_to_worker(creep)
        duties_and_targets.decrease_lorries_needed(creep)


def run_truck(creep):
    duty = creep.memory.duty
    target = creep.memory.target
    if target and actions.not_fleeing(creep):
        if duty == 'filling_up':
            actions.filling_up(creep)
            actions.paving_roads(creep)
        if duty == 'unloading':
            actions.unloading(creep)
            actions.paving_roads(creep)
    else:
        define_truck_target(creep)


def define_truck_target(creep):
    del creep.memory.duty
    del creep.memory.target
    if not duties_and_targets.define_truck_stations(creep):
        if not duties_and_targets.define_filling_up_truck(creep):
            duties_and_targets.define_unloading_truck(creep)


def run_defender(creep):
    duty = creep.memory.duty
    if duty:
        healer = Game.getObjectById(creep.memory.healer)
        if healer:
            if healer.hits < healer.hitsMax / 4 or healer.memory.target != creep.id:
                del creep.memory.healer
        else:
            del creep.memory.healer
        if duty != 'defending' or actions.move_away_from_creeps(creep):
            creep.memory.start_point = 0
        if duty == 'attacking':
            actions.attacking(creep)
        elif duty == 'defending' and not actions.move_away_from_creeps(creep):
            actions.defending(creep)
        elif duty == 'going_to_help':
            actions.going_to_help(creep)
    else:
        define_defender_targets(creep)


def define_defender_targets(creep):
    enemy = creep.room.find(FIND_HOSTILE_CREEPS, {'filter': lambda e: e.owner.username != 'rep71Le'})
    if len(enemy) == 0:
        if not duties_and_targets.define_flag_to_help(creep):
            if not actions.going_home(creep):
                creep.memory.duty = 'defending'
    else:
        if 5 < creep.pos.x < 45 and 5 < creep.pos.y < 45:
            flag = Game.flags[creep.memory.flag]
            if flag:
                creep.moveTo(flag)
            else:
                home = Game.getObjectById(creep.memory.home)
                creep.moveTo(home)
        else:
            creep.memory.duty = 'attacking'


def run_offender(creep):
    duty = creep.memory.duty
    if duty:
        healer = Game.getObjectById(creep.memory.healer)
        if healer:
            if healer.hits < healer.hitsMax / 4 or healer.memory.target != creep.id:
                del creep.memory.healer
        else:
            del creep.memory.healer
        if duty == 'attacking':
            actions.attacking(creep)
        if duty == 'go_to_flag':
            actions.going_to_flag(creep)
    else:
        define_offender_targets(creep)


def define_offender_targets(creep):
    if not creep.memory.flag:
        for flag_name in Object.keys(Game.flags):
            if flag_name[:1] == 'o':
                creep.memory.flag = flag_name
    if not duties_and_targets.define_going_to_flag(creep):
        if 2 < creep.pos.x < 47 and 2 < creep.pos.y < 47:
            flag = Game.flags[creep.memory.flag]
            if flag:
                creep.moveTo(flag)
            else:
                home = Game.getObjectById(creep.memory.home)
                home.memory.need_offenders = 0
                creep.moveTo(home)
                creep.memory.job = 'defender'
                del creep.memory.duty
        else:
            creep.memory.duty = 'attacking'

    if not creep.memory.target:
        creep.say('?')
        actions.move_away_from_creeps(creep)


def run_healer(creep):
    duty = creep.memory.duty
    if duty:
        if duty == 'nursing':
            actions.nursing(creep)
    else:
        define_healer_targets(creep)


def define_healer_targets(creep):
    del creep.memory.target
    del creep.memory.duty
    for creep_name in Object.keys(Game.creeps):
        any_creep = Game.creeps[creep_name]
        if (any_creep.memory.job == 'defender' or any_creep.memory.job == 'offender') \
                and any_creep.memory.home == creep.memory.home:
            if not any_creep.memory.healer:
                any_creep.memory.healer = creep.id
                creep.memory.target = any_creep.id
                creep.memory.duty = 'nursing'
                return
    if not creep.memory.target:
        if not actions.just_heal_anything(creep):
            creep.say('?')
            actions.move_away_from_creeps(creep)


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
    del creep.memory.controller
    del creep.memory.duty
    del creep.memory.target
    if not duties_and_targets.define_reservators_flag(creep):
        duties_and_targets.define_controller(creep)
    if not creep.memory.duty:
        creep.say('?')
        actions.move_away_from_creeps(creep)


def run_stealer(creep):
    target = creep.memory.target
    duty = creep.memory.duty
    if duty and target and actions.not_fleeing(creep):
        if duty == 'go_to_flag':
            actions.going_to_flag(creep)
            actions.paving_roads(creep)
            actions.pick_up_energy(creep)
        elif duty == 'picking_up_tombstone':
            actions.pick_up_tombstone(creep)
            actions.pick_up_energy(creep)
        elif duty == 'dismantling':
            actions.dismantling(creep)
        elif duty == 'mining':
            actions.creep_mining(creep)
            actions.pick_up_energy(creep)
        elif duty == 'withdrawing_from_closest':
            actions.withdraw_from_closest(creep)
            actions.pick_up_energy(creep)
        elif duty == 'repairing':
            actions.creep_repairing(creep)
            actions.paving_roads(creep)
        elif duty == 'building':
            actions.building(creep)
            actions.paving_roads(creep)
        elif duty == 'going_home':
            actions.paving_roads(creep)
            if not actions.going_home(creep):
                define_target(creep)
        elif duty == 'transferring_to_closest':
            if not actions.going_home(creep):
                if actions.transferring_to_closest(creep) == -8:
                    duties_and_targets.decrease_stealers_needed(creep)
            actions.paving_roads(creep)
    else:
        define_stealer_targets(creep)


def define_stealer_targets(creep):
    del creep.memory.duty
    del creep.memory.target
    if not duties_and_targets.define_going_to_flag_empty(creep):
        if not duties_and_targets.removed_flag(creep):
            if not duties_and_targets.define_creep_to_pickup_tombstone(creep):
                if not duties_and_targets.define_closest_to_withdraw(creep):
                    duties_and_targets.decrease_stealers_needed(creep)
                    if not duties_and_targets.define_mining_target(creep):
                        if not duties_and_targets.define_dismantling_target(creep):
                            if not duties_and_targets.define_repairing_target_for_stealers(creep):
                                if not duties_and_targets.define_building_target(creep):
                                    if not duties_and_targets.define_closest_to_transfer(creep):
                                        duties_and_targets.define_going_home(creep)
    if not creep.memory.target:
        creep.say('?')
        actions.move_away_from_creeps(creep)
        duties_and_targets.decrease_stealers_needed(creep)


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
    del creep.memory.flag
    del creep.memory.path
    del creep.memory.controller
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
