from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def define_closest_to_withdraw(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        container = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER or
                               s.structureType == STRUCTURE_STORAGE
                               or s.structureType == STRUCTURE_LINK) and
                              s.store[RESOURCE_ENERGY] >= creep.store.getCapacity()) \
            .sortBy(lambda s: s.pos.getRangeTo(creep)).first()
        if container:
            target = container
            creep.memory.duty = 'withdrawing_from_closest'
            creep.memory.target = target.id
    return target


def define_mining_target_old(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        target = creep.pos.findClosestByPath(FIND_SOURCES_ACTIVE)
        if target:
            creep.memory.duty = 'mining'
            creep.memory.target = target.id
    return target


def define_mining_target(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        sources = creep.room.find(FIND_SOURCES_ACTIVE)
        if sources:
            for source in sources:
                if source:
                    coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                         lambda c: c.memory.duty == 'mining' and
                                                   c.memory.target == source.id)
                    energy_of_source = source.energy
                    energy_on_the_way = 0
                    if coworkers:
                        for coworker in coworkers:
                            if coworker.store.getCapacity() > 0:
                                energy_on_the_way = energy_on_the_way + coworker.store[RESOURCE_ENERGY] \
                                                    - coworker.store.getCapacity()
                        total_energy_of_source = energy_of_source + energy_on_the_way
                        source.total_energy_of_source = total_energy_of_source
                        if source.ticksToRegeneration == undefined:
                            source.ticks = 1
                        else:
                            source.ticks = source.ticksToRegeneration
            fullest_source = _(sources).sortBy(lambda s: s.total_energy_of_source / s.ticks).last()
            if fullest_source:
                if fullest_source.total_energy_of_source > - creep.store.getCapacity():
                    target = fullest_source
                    creep.memory.duty = 'mining'
                    creep.memory.target = target.id
    return target


def define_deliver_for_spawn_target(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        if creep.room.energyCapacityAvailable > creep.room.energyAvailable:
            coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                 lambda c: c.memory.duty == 'delivering_for_spawn')
            energy_of_room = creep.room.energyAvailable
            if coworkers:
                energy_on_the_way = 0
                for coworker in coworkers:
                    if coworker.store.getCapacity() > 0:
                        energy_on_the_way = energy_on_the_way + (coworker.store[RESOURCE_ENERGY])
                energy_of_room = energy_of_room + energy_on_the_way
            if energy_of_room < creep.room.energyCapacityAvailable:
                spawning_structures = _.filter(creep.room.find(FIND_STRUCTURES),
                                               lambda s: (s.structureType == STRUCTURE_SPAWN or
                                                          s.structureType == STRUCTURE_EXTENSION) and
                                                         s.energy < s.energyCapacity)
                if spawning_structures:
                    target = _(spawning_structures).sortBy(lambda s: s.pos.getRangeTo(creep)).last()
                    if target:
                        creep.memory.duty = 'delivering_for_spawn'
                        creep.memory.target = target.id
    return target


def define_building_target(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        target = creep.pos.findClosestByRange(FIND_CONSTRUCTION_SITES)
        if target:
            creep.memory.duty = 'building'
            creep.memory.target = target.id
    return target


def define_upgrading_target(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        target = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.structureType == STRUCTURE_CONTROLLER)) \
            .sample()
        if target:
            creep.memory.duty = 'upgrading'
            creep.memory.target = target.id
    return target


def define_repairing_target(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        target = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.hits < s.hitsMax * 0.05) and
                              s.structureType != STRUCTURE_WALL) \
            .sortBy(lambda s: (s.hitsMax / s.hits)).last()
        if target != undefined:
            do_not_repairs = Memory.deconstructions
            if do_not_repairs:
                for do_not_repair in do_not_repairs:
                    if target:
                        if target.id == do_not_repair:
                            target = undefined
            if target:
                creep.memory.duty = 'repairing'
                creep.memory.target = target.id
    return target


def define_repairing_target_for_stealers(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        target = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.hits < s.hitsMax * 0.8) and
                              s.structureType != STRUCTURE_WALL) \
            .sortBy(lambda s: (s.hitsMax / s.hits)).last()
        if target != undefined:
            do_not_repairs = Memory.deconstructions
            if do_not_repairs:
                for do_not_repair in do_not_repairs:
                    if target:
                        if target.id == do_not_repair:
                            target = undefined
            if target:
                creep.memory.duty = 'repairing'
                creep.memory.target = target.id
    return target


def define_dismantling_target(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        deconstructions = Memory.deconstructions
        if deconstructions:
            for deconstruction in deconstructions:
                deconstruction_site = Game.getObjectById(deconstruction)
                if deconstruction_site:
                    if deconstruction_site.room == creep.room:
                        target = deconstruction_site
                else:
                    deconstructions.remove(deconstruction)
            if target:
                creep.memory.duty = 'dismantling'
                creep.memory.target = target.id
    return target


def define_creep_to_pickup_tombstone(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] < creep.carryCapacity:
        tombstone = _(creep.room.find(FIND_TOMBSTONES)) \
            .filter(lambda t: (t.store[RESOURCE_ENERGY] > 0 and
                               t.id != creep.memory.target)).first()
        if tombstone != undefined:
            creep_to_pickup = _(creep.room.find(FIND_MY_CREEPS)) \
                .filter(lambda c: (c.store[RESOURCE_ENERGY] < c.store.getCapacity() / 2) and
                                  (c.memory.job == 'lorry' or
                                   c.memory.job == 'stealorry' or
                                   c.memory.job == 'starter' or
                                   c.memory.job == 'stealer' or
                                   ((c.memory.job == 'miner' or
                                     c.memory.job == 'steaminer') and
                                    c.pos.isNearTo(tombstone)))) \
                .sortBy(lambda c: (c.pos.getRangeTo(tombstone))).first()
            if creep_to_pickup:
                if tombstone.store[RESOURCE_ENERGY] > creep_to_pickup.pos.getRangeTo(tombstone) * 5:
                    coworkers = _.sum(creep_to_pickup.room.find(FIND_MY_CREEPS),
                                      lambda c: c.memory.target == tombstone.id)
                    if coworkers < 1:
                        del creep.memory.path
                        target = tombstone
                        creep_to_pickup.memory.duty = 'picking_up_tombstone'
                        creep_to_pickup.memory.target = target.id
    return target


def define_emptiest(creep):
    target = undefined
    emptiest_container = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        containers = _.filter(creep.room.find(FIND_STRUCTURES),
                              lambda s: s.structureType == STRUCTURE_CONTAINER)
        if containers:
            for container in containers:
                if container:
                    coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                         lambda c: (c.memory.duty == 'delivering_to_emptiest' or
                                                    c.memory.duty == 'transferring_to_closest') and
                                                   c.memory.target == container.id)
                    anti_coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                              lambda c: (c.memory.duty == 'withdrawing_from_closest') and
                                                        c.memory.target == container.id)
                    energy_of_container = container.store[RESOURCE_ENERGY]
                    energy_on_the_way = 0
                    if coworkers:
                        for coworker in coworkers:
                            if coworker.store.getCapacity() > 0:
                                energy_on_the_way = energy_on_the_way + (coworker.store[RESOURCE_ENERGY])
                        total_energy_of_container = energy_of_container + energy_on_the_way
                        container.total_energy_of_container = total_energy_of_container
                    if anti_coworkers:
                        for anti_coworker in anti_coworkers:
                            if anti_coworker.store.getCapacity() > 0:
                                energy_on_the_way = energy_on_the_way + anti_coworker.store[RESOURCE_ENERGY] \
                                                    - anti_coworker.store.getCapacity()
                        total_energy_of_container = energy_of_container + energy_on_the_way
                        container.total_energy_of_container = total_energy_of_container
                if container:
                    emptiest_container = _(containers).sortBy(lambda c: c.total_energy_of_container).first()
                    # print(emptiest_container.total_energy_of_container + '  emptiest  ' + emptiest_container.id)
    if emptiest_container:
        if emptiest_container.total_energy_of_container < emptiest_container.store.getCapacity() * 0.4:
            creep.memory.duty = 'delivering_to_emptiest'
            target = emptiest_container
            creep.memory.target = target.id
    return target


def define_fullest(creep):
    target = undefined
    fullest_container = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        containers = _.filter(creep.room.find(FIND_STRUCTURES),
                              lambda s: s.structureType == STRUCTURE_CONTAINER and
                                        s.store[RESOURCE_ENERGY] >= creep.store.getCapacity())
        if containers:
            for container in containers:
                if container:
                    coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                         lambda c: (c.memory.duty == 'withdrawing_from_fullest' or
                                                    c.memory.duty == 'withdrawing_from_closest') and
                                                   c.memory.target == container.id)
                    anti_coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                              lambda c: (c.memory.duty == 'transferring_to_closest') and
                                                        c.memory.target == container.id)
                    energy_of_container = container.store[RESOURCE_ENERGY]
                    energy_on_the_way = 0
                    if coworkers:
                        for coworker in coworkers:
                            if coworker.store.getCapacity() > 0:
                                energy_on_the_way = energy_on_the_way + coworker.store[RESOURCE_ENERGY] \
                                                    - coworker.store.getCapacity()
                        total_energy_of_container = energy_of_container + energy_on_the_way
                        container.total_energy_of_container = total_energy_of_container
                    if anti_coworkers:
                        for anti_coworker in anti_coworkers:
                            if anti_coworker.store.getCapacity() > 0:
                                energy_on_the_way = energy_on_the_way + (anti_coworker.store[RESOURCE_ENERGY])
                        total_energy_of_container = energy_of_container + energy_on_the_way
                        container.total_energy_of_container = total_energy_of_container
                if container:
                    fullest_container = _(containers).sortBy(lambda c: c.total_energy_of_container).last()
                    # print(fullest_container.total_energy_of_container + '  fullest  ' + fullest_container.id)

    if fullest_container:
        if fullest_container.total_energy_of_container > fullest_container.store.getCapacity() * 0.5:
            target = fullest_container
            creep.memory.duty = 'withdrawing_from_fullest'
            creep.memory.target = target.id
    return target


def define_storage_to_deliver(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        target = _.filter(creep.room.find(FIND_STRUCTURES),
                          lambda s: s.structureType == STRUCTURE_STORAGE
                                    and s.store.getFreeCapacity(RESOURCE_ENERGY) > 0)
        if target[0]:
            creep.memory.duty = 'delivering_to_storage'
            creep.memory.target = target[0].id
            decrease_lorries_needed(creep)
    return target


def define_terminal_to_deliver(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        terminal = creep.room.terminal
        if terminal:
            if terminal.store.getFreeCapacity(RESOURCE_ENERGY) > 0:
                target = terminal
                creep.memory.duty = 'delivering_to_terminal'
                creep.memory.target = target.id
    return target


def define_storage_to_withdraw(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        target = _.filter(creep.room.find(FIND_STRUCTURES),
                          lambda s: s.structureType == STRUCTURE_STORAGE
                                    and s.store[RESOURCE_ENERGY] >= creep.store.getCapacity())
        if target[0]:
            creep.memory.duty = 'withdrawing_from_storage'
            creep.memory.target = target[0].id
    return target


def define_terminal_to_withdraw(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        terminal = creep.room.terminal
        if terminal:
            if terminal.store[RESOURCE_ENERGY] > creep.store.getCapacity():
                target = terminal
                creep.memory.duty = 'withdrawing_from_storage'
                creep.memory.target = target.id
    return target


def define_reservators_flag(creep):
    target = undefined
    flag = Game.flags[creep.memory.flag]
    if flag:
        if creep.pos.inRangeTo(flag, 40):
            target = undefined
            creep.memory.duty = 'reserving'
            creep.memory.controller = creep.room.controller
        else:
            target = flag
            creep.memory.duty = 'go_to_flag'
    else:
        home = Game.getObjectById(creep.memory.home)
        flags = Object.keys(Game.flags)
        for flag_name in flags:
            if flag_name[:6] == 'Steal' + home.name[5:6]:
                flag = Game.flags[flag_name]
                if flag:
                    if flag.memory.need_reservators > flag.memory.reservators:
                        if creep.pos.inRangeTo(flag, 40):
                            target = undefined
                            creep.memory.duty = 'reserving'
                            creep.memory.controller = creep.room.controller
                        else:
                            target = flag
                            creep.memory.flag = flag_name
                            creep.memory.target = flag_name
                            creep.memory.duty = 'go_to_flag'
    return target


def define_controller(creep):
    controller = creep.room.controller
    if controller:
        creep.memory.controller = controller.id
        if creep.memory.job == 'reservator':
            creep.memory.duty = 'reserving'
        if creep.memory.job == 'claimer':
            creep.memory.duty = 'claiming'
    return controller


def define_going_home(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        home = Game.getObjectById(creep.memory.home)
        if home.room != creep.room:
            target = home
            creep.memory.duty = 'going_home'
            creep.memory.target = home.id
    return target


def define_going_to_flag(creep):
    target = undefined
    flag = Game.flags[creep.memory.flag]
    if flag:
        if creep.pos.inRangeTo(flag, 40):
            target = undefined
            del creep.memory.duty
        else:
            target = flag
            creep.memory.target = flag.name
            creep.memory.duty = 'go_to_flag'
    return target


def define_going_to_flag_empty(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        flag = Game.flags[creep.memory.flag]
        if flag:
            if creep.pos.inRangeTo(flag, 40):
                target = undefined
                del creep.memory.duty
            else:
                target = flag
                creep.memory.target = flag.name
                creep.memory.duty = 'go_to_flag'
    return target


def define_closest_to_transfer(creep):
    target = undefined
    home = Game.getObjectById(creep.memory.home)
    if creep.room == home.room:
        if creep.store[RESOURCE_ENERGY] > 0:
            container = _(creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: s.structureType == STRUCTURE_CONTAINER or
                                  s.structureType == STRUCTURE_STORAGE
                                  or s.structureType == STRUCTURE_LINK) \
                .sortBy(lambda s: s.pos.getRangeTo(creep)).first()
            if container:
                target = container
                creep.memory.duty = 'transferring_to_closest'
                creep.memory.target = target.id
    return target


def decrease_stealers_needed(creep):
    flag = Game.flags[creep.memory.flag]
    if flag:
        need_stealers = flag.memory.need_stealers
        if need_stealers >= 2:
            flag.memory.need_stealers = need_stealers - 0.005


def define_claimers_flag(creep):
    home = Game.getObjectById(creep.memory.home)
    flag = Game.flags[Memory.claim]
    if flag:
        if creep.room == home.room:
            creep.memory.flag = flag.name
            creep.memory.duty = 'go_to_flag'
            if creep.pos.inRangeTo(flag, 40):
                flag = undefined
                del creep.memory.duty
        else:
            flag = undefined
    return flag


def define_spawn_builders_needed(creep):
    target = Game.getObjectById(creep.memory.target)
    home = Game.getObjectById(creep.memory.home)
    if target:
        if creep.memory.flag == 'BS':
            need_spawn_builders = home.memory.need_spawn_builders
            spawn_builders = home.memory.spawn_builders
            if target.energy > target.ticksToRegeneration * 12 or target.energy >= 3000:
                if need_spawn_builders <= spawn_builders:
                    need_spawn_builders = need_spawn_builders + 0.01
                    need_workers = home.memory.need_workers
                    need_workers = need_workers + 0.01
                    home.memory.need_workers = need_workers
            if target.energy / target.ticksToRegeneration < 8:
                if need_spawn_builders >= spawn_builders - 1.5:
                    need_spawn_builders = need_spawn_builders - 0.02
            home.memory.need_spawn_builders = round(need_spawn_builders, 2)


def define_emergency_upgrading_target(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        target = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.structureType == STRUCTURE_CONTROLLER)) \
            .sample()
        if target.ticksToDowngrade < 2000:
            creep.memory.duty = 'upgrading'
            creep.memory.target = target.id
        else:
            target = undefined
    return target


def define_room_to_help(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        for flag_name in Object.keys(Game.flags):
            flag = Game.flags[flag_name]
            if flag.memory.give_lorries is True:
                home = Game.getObjectById(creep.memory.home)
                if creep.room == home.room:
                    if flag_name[:6] == 'Steal' + home.name[5:6]:
                        target = flag_name
                        creep.memory.job = 'stealorry'
                        creep.memory.flag = flag_name
                        del creep.memory.duty
                        del creep.memory.target
    return target


def define_stealer_to_help(creep):
    target = undefined
    fullest_stealer = undefined
    if creep.store[RESOURCE_ENERGY] < creep.store.getCapacity():
        flag = Game.flags[creep.memory.flag]
        if flag:
            if creep.room == flag.room:
                stealers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                    lambda s: s.memory.job == 'stealer' and
                                              s.store[RESOURCE_ENERGY] > 0)
                if stealers:
                    for stealer in stealers:
                        if stealer:
                            coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                                 lambda c: (c.memory.duty == 'helping_stealers') and
                                                           c.memory.target == stealer.id)
                            energy_of_stealer = stealer.store[RESOURCE_ENERGY]
                            energy_on_the_way = 0
                            if coworkers:
                                for coworker in coworkers:
                                    if coworker.store.getCapacity() > 0:
                                        energy_on_the_way = energy_on_the_way + coworker.store[RESOURCE_ENERGY] \
                                                            - coworker.store.getCapacity()
                                total_energy_of_stealer = energy_of_stealer + energy_on_the_way
                                stealer.total_energy_of_stealer = total_energy_of_stealer
                            fullest_stealer = _(stealers).sortBy(lambda c: c.total_energy_of_stealer).last()

    if fullest_stealer:
        if fullest_stealer.total_energy_of_stealer > 0:
            target = fullest_stealer
            creep.memory.duty = 'helping_stealers'
            creep.memory.target = target.id
        if not target:
            if len(coworkers) <= 1:
                target = fullest_stealer
                creep.memory.duty = 'helping_stealers'
                creep.memory.target = target.id
            if not target:
                if len(coworkers) <= 2:
                    target = fullest_stealer
                    creep.memory.duty = 'helping_stealers'
                    creep.memory.target = target.id
                if not target:
                    if len(coworkers) <= 3:
                        target = fullest_stealer
                        creep.memory.duty = 'helping_stealers'
                        creep.memory.target = target.id
    return target


def decrease_lorries_needed(creep):
    home = Game.getObjectById(creep.memory.home)
    need_lorries = home.memory.need_lorries
    if need_lorries > 1:
        need_lorries = need_lorries - 0.001
    home.memory.need_lorries = need_lorries


def increase_lorries_needed(creep):
    home = Game.getObjectById(creep.memory.home)
    need_lorries = home.memory.need_lorries
    need_lorries = need_lorries + 0.01
    home.memory.need_lorries = need_lorries


def check_if_repairing_needed(creep):
    target = _(creep.room.find(FIND_STRUCTURES)) \
        .filter(lambda s: (s.hits < s.hitsMax * 0.05) and
                          s.structureType != STRUCTURE_WALL) \
        .sortBy(lambda s: (s.hitsMax / s.hits)).last()
    if target:
        do_not_repairs = Memory.deconstructions
        if do_not_repairs:
            for do_not_repair in do_not_repairs:
                if target:
                    if target.id == do_not_repair:
                        target = undefined
        if target:
            creep.memory.repairing = True
        else:
            creep.memory.repairing = False
    return target


def check_if_building_needed(creep):
    target = undefined
    construction_sites = creep.room.find(FIND_CONSTRUCTION_SITES)
    if len(construction_sites) > 0:
        creep.memory.building = True
        target = construction_sites
    else:
        creep.memory.building = False
    return target


def define_worker_to_help(creep):
    target = undefined
    emptiest_worker = undefined
    workers = _.filter(creep.room.find(FIND_MY_CREEPS),
                       lambda w: w.memory.job == 'worker' and
                                 w.store[RESOURCE_ENERGY] < w.store.getCapacity())
    if workers:
        for worker in workers:
            if worker:
                coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                     lambda c: (c.memory.duty == 'helping_workers') and
                                               c.memory.target == worker.id)
                energy_of_worker = worker.store[RESOURCE_ENERGY]
                energy_on_the_way = 0
                if coworkers:
                    for coworker in coworkers:
                        if coworker.store.getCapacity() > 0:
                            energy_on_the_way = energy_on_the_way + coworker.store[RESOURCE_ENERGY]
                    total_energy_of_worker = energy_of_worker + energy_on_the_way
                    worker.total_energy_of_worker = total_energy_of_worker
                emptiest_worker = _(workers).sortBy(lambda c: c.total_energy_of_worker).first()

    if emptiest_worker:
        if emptiest_worker.total_energy_of_worker < emptiest_worker.store.getCapacity():
            target = emptiest_worker
            creep.memory.duty = 'helping_workers'
            creep.memory.target = target.id
    return target


def define_tower(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        tower = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.structureType == STRUCTURE_TOWER and
                               s.store.getFreeCapacity(RESOURCE_ENERGY) > 0)) \
            .sample()
        if tower:
            target = tower
            creep.memory.duty = 'delivering_to_tower'
            creep.memory.target = target.id
    return target


def define_flag_to_help(creep):
    flag = undefined
    for flag_name in Object.keys(Game.flags):
        if flag_name[:1] == 'A':
            home = Game.getObjectById(creep.memory.home)
            if flag_name[6:7] == home.name[5:6]:
                flag = Game.flags[flag_name]
                if flag:
                    creep.memory.flag = flag_name
                    creep.memory.duty = 'going_to_help'
                    if creep.pos.inRangeTo(flag, 40):
                        flag = undefined
                        del creep.memory.duty
    return flag


def define_truck_stations(creep):
    target = undefined
    home = Game.getObjectById(creep.memory.home)
    for flag_name in Object.keys(Game.flags):
        if flag_name[:7] == 'Energy' + home.name[5:6]:
            if not creep.memory.station2:
                creep.memory.station2 = Game.spawns['Spawn' + flag_name[7:8]].id
                target = creep.memory.station2
                creep.memory.flag = flag_name
    return target


def define_filling_up_truck(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] == 0:
        creep.memory.target = creep.memory.home
        creep.memory.duty = 'filling_up'
    return target


def define_unloading_truck(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] >= creep.store.getCapacity():
        creep.memory.target = creep.memory.station2
        creep.memory.duty = 'unloading'
    return target


def removed_flag(creep):
    target = undefined
    flag = Game.flags[creep.memory.flag]
    if not flag:
        del creep.memory.duty
        del creep.memory.target
        del creep.memory.flag
        del creep.memory.path
        creep.memory.job = 'worker'
        target = '?'
    return target


def define_link_to_withdraw(creep):
    target = undefined
    link_processed = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        link = creep.pos.findClosestByPath(FIND_STRUCTURES, {'filter': lambda s: s.structureType == STRUCTURE_LINK})
        if link:
            if link.store[RESOURCE_ENERGY] >= link.store.getFreeCapacity(RESOURCE_ENERGY) * 1.5 \
                    and (link.cooldown == 0 or link.cooldown > 18):
                coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                     lambda c: (c.memory.duty == 'withdrawing_from_link') and
                                               c.memory.target == link.id)
                anti_coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                          lambda c: (c.memory.duty == 'transferring_to_closest') and
                                                    c.memory.target == link.id)
                energy_of_link = link.store[RESOURCE_ENERGY]
                energy_on_the_way = 0
                if coworkers:
                    for coworker in coworkers:
                        if coworker.store.getCapacity() > 0:
                            energy_on_the_way = energy_on_the_way + coworker.store[RESOURCE_ENERGY] \
                                                - coworker.store.getCapacity()
                    total_energy_of_container = energy_of_link + energy_on_the_way
                    link.total_energy_of_container = total_energy_of_container
                if anti_coworkers:
                    for anti_coworker in anti_coworkers:
                        if anti_coworker.store.getCapacity() > 0:
                            energy_on_the_way = energy_on_the_way + anti_coworker.store[RESOURCE_ENERGY]
                    total_energy_of_container = energy_of_link + energy_on_the_way
                    link.total_energy_of_container = total_energy_of_container
            link_processed = link

    if link_processed:
        if link_processed.total_energy_of_container > creep.store.getCapacity() / 2:
            target = link_processed
            creep.memory.duty = 'withdrawing_from_link'
            creep.memory.target = target.id
    return target


def define_link_to_transfer(creep):
    target = undefined
    link_processed = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        link = creep.pos.findClosestByPath(FIND_STRUCTURES, {'filter': lambda s: s.structureType == STRUCTURE_LINK})
        if link:
            if link.store[RESOURCE_ENERGY] * 2 < link.store.getFreeCapacity(RESOURCE_ENERGY):
                coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                     lambda c: (c.memory.duty == 'transferring_to_link') and
                                               c.memory.target == link.id)
                anti_coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                          lambda c: (c.memory.duty == 'withdrawing_from_closest') and
                                                    c.memory.target == link.id)
                energy_of_link = link.store[RESOURCE_ENERGY]
                energy_on_the_way = 0
                if coworkers:
                    for coworker in coworkers:
                        if coworker.store.getCapacity() > 0:
                            energy_on_the_way = energy_on_the_way + coworker.store[RESOURCE_ENERGY]
                    total_energy_of_container = energy_of_link + energy_on_the_way
                    link.total_energy_of_container = total_energy_of_container
                if anti_coworkers:
                    for anti_coworker in anti_coworkers:
                        if anti_coworker.store.getCapacity() > 0:
                            energy_on_the_way = energy_on_the_way + anti_coworker.store[RESOURCE_ENERGY] \
                                                - anti_coworker.store.getCapacity()
                    total_energy_of_container = energy_of_link + energy_on_the_way
                    link.total_energy_of_container = total_energy_of_container
                link_processed = link

    if link_processed:
        if link_processed.total_energy_of_container \
                <= link_processed.store.getFreeCapacity(RESOURCE_ENERGY) + link_processed.store[RESOURCE_ENERGY]:
            target = link_processed
            creep.memory.duty = 'transferring_to_link'
            creep.memory.target = target.id
    return target


def define_stealing_container(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        home = Game.getObjectById(creep.memory.home)
        for flag_name in Object.keys(Game.flags):
            if flag_name[:6] == 'Steal' + home.name[5:6]:
                flag = Game.flags[flag_name]
                if flag.room:
                    container = _(flag.room.find(FIND_STRUCTURES)) \
                        .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER) and
                                          s.store[RESOURCE_ENERGY] >= creep.store.getCapacity()) \
                        .sortBy(lambda s: s.store[RESOURCE_ENERGY]).last()
                    if container:
                        coworkers_in_flag_room = _.filter(flag.room.find(FIND_MY_CREEPS),
                                                          lambda c: (c.memory.duty == 'withdrawing_from_stealing') and
                                                                    c.memory.target == container.id)
                        energy_of_container = container.store[RESOURCE_ENERGY]
                        energy_on_the_way = 0
                        if coworkers_in_flag_room:
                            for coworker in coworkers_in_flag_room:
                                if coworker.store.getCapacity() > 0:
                                    energy_on_the_way = energy_on_the_way + coworker.store[RESOURCE_ENERGY] \
                                                        - coworker.store.getCapacity()
                            energy_of_container = energy_of_container + energy_on_the_way
                        home = Game.getObjectById(creep.memory.home)
                        coworkers_in_home_room = _.filter(home.room.find(FIND_MY_CREEPS),
                                                          lambda c: (c.memory.duty == 'withdrawing_from_stealing') and
                                                                    c.memory.target == container.id)
                        if coworkers_in_home_room:
                            for coworker in coworkers_in_home_room:
                                if coworker.store.getCapacity() > 0:
                                    energy_on_the_way = energy_on_the_way + coworker.store[RESOURCE_ENERGY] \
                                                        - coworker.store.getCapacity()
                            energy_of_container = energy_of_container + energy_on_the_way
                        container.total_energy_of_container = energy_of_container
                        if container.total_energy_of_container >= creep.store.getCapacity():
                            target = container
                            creep.memory.flag = flag_name
                            creep.memory.duty = 'withdrawing_from_stealing'
                            creep.memory.target = target.id
    return target
