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
        target = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER or
                               s.structureType == STRUCTURE_STORAGE) and
                              s.store[RESOURCE_ENERGY] >= creep.carryCapacity).sample()
        if target:
            creep.memory.duty = 'withdrawing_from_closest'
            creep.memory.target = target.id
    return target


def define_mining_target(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        target = creep.pos.findClosestByPath(FIND_SOURCES_ACTIVE)
        if target:
            creep.memory.duty = 'mining'
            creep.memory.target = target.id
    return target


def verify_target(sources, creep, amount):
    target = undefined
    for source in sources:
        coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                             lambda c: (c.memory.target == source.id))
        if len(coworkers) < 300 / creep.store.getCapacity() * amount:
            target = source
            if target:
                creep.memory.duty = 'mining'
                creep.memory.target = target.id
    return target


def define_stealing_target(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        sources = _.sortBy(creep.room.find(FIND_SOURCES_ACTIVE),
                           lambda s: s.energy)
        amount = 1
        target = verify_target(sources, creep, amount)
        # if not target:
        #     amount = 2
        #     target = verify_target(sources, creep, amount)
    return target


def define_deliver_for_spawn_target(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        spawning_structures = _.filter(creep.room.find(FIND_STRUCTURES),
                                       lambda s: (s.structureType == STRUCTURE_SPAWN or
                                                  s.structureType == STRUCTURE_EXTENSION) and
                                                 s.energy < s.energyCapacity)
        if spawning_structures:
            for spawning_structure in spawning_structures:
                coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                     lambda c: (c.memory.target == spawning_structure.id and
                                                c.store[RESOURCE_ENERGY]) >=
                                               spawning_structure.energyCapacity - spawning_structure.energy)
                if len(coworkers) == 0:
                    target = spawning_structure
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
        target = _(creep.room.find(FIND_TOMBSTONES)) \
            .filter(lambda t: (t.store[RESOURCE_ENERGY] > 0 and
                               t.id != creep.memory.target)).first()
        if target != undefined:
            creep_to_pickup = _(creep.room.find(FIND_MY_CREEPS)) \
                .filter(lambda c: (c.store[RESOURCE_ENERGY] < c.store.getCapacity()) and
                                  (c.memory.job == 'lorry' or
                                   c.memory.job == 'stealorry' or
                                   c.memory.job == 'starter' or
                                   ((c.memory.job == 'stealer' or
                                     c.memory.job == 'miner') and
                                    c.pos.isNearTo(target)))) \
                .sortBy(lambda c: (c.pos.getRangeTo(target))).first()
            if creep_to_pickup:
                creep_to_pickup.memory.duty = 'picking_up_tombstone'
                creep_to_pickup.memory.target = target.id
                del creep.memory.path
                if creep_to_pickup.id != creep.id:
                    target = undefined
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
                                energy_on_the_way = energy_on_the_way + coworker.store[RESOURCE_ENERGY]
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
        if emptiest_container.total_energy_of_container < emptiest_container.store.getCapacity() * 0.7:
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
                                energy_on_the_way = energy_on_the_way + anti_coworker.store[RESOURCE_ENERGY]
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
                          lambda s: s.structureType == STRUCTURE_STORAGE)
        if target[0]:
            creep.memory.duty = 'delivering_to_storage'
            creep.memory.target = target[0].id
    return target


def define_storage_to_withdraw(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        target = _.filter(creep.room.find(FIND_STRUCTURES),
                          lambda s: s.structureType == STRUCTURE_STORAGE)
        if target[0]:
            creep.memory.duty = 'withdrawing_from_storage'
            creep.memory.target = target[0].id
    return target


def define_reservators_flag(creep):
    flag = undefined
    home = Game.getObjectById(creep.memory.home)
    flags = Object.keys(Game.flags)
    for flag_name in flags:
        if flag_name[:6] == 'Steal' + home.name[5:6]:
            flag = Game.flags[flag_name]
            if flag:
                if flag.memory.need_reservators >= flag.memory.reservators:
                    if creep.pos.inRangeTo(flag, 40):
                        flag = undefined
                        del creep.memory.duty
                        del creep.memory.target
                    else:
                        creep.memory.flag = flag_name
                        creep.memory.target = flag_name
                        creep.memory.duty = 'go_to_flag'
    return flag


def define_controller(creep):
    controller = _(creep.room.find(FIND_STRUCTURES)) \
        .filter(lambda s: s.structureType == STRUCTURE_CONTROLLER).sample()
    if controller:
        creep.memory.controller = controller.id
        if creep.memory.job == 'reservator':
            creep.memory.duty = 'reserving'
        if creep.memory.job == 'claimer':
            creep.memory.duty = 'claiming'
    return controller


def define_going_home(creep):
    home = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        home = Game.getObjectById(creep.memory.home)
        if home.room != creep.room:
            creep.memory.duty = 'going_home'
            creep.memory.target = home.id
    return home


def define_going_to_flag(creep):
    flag = Game.flags[creep.memory.flag]
    if flag:
        home = Game.getObjectById(creep.memory.home)
        if creep.pos.inRangeTo(flag, 40):
            flag = undefined
            del creep.memory.duty
        else:
            creep.memory.target = flag.name
            creep.memory.duty = 'go_to_flag'
        # if creep.room == home.room:
        #     creep.memory.target = flag.name
        #     creep.memory.duty = 'go_to_flag'
        #     if creep.pos.inRangeTo(flag, 40):
        #         flag = undefined
        #         del creep.memory.duty
        # else:
        #     flag = undefined
    return flag


def define_closest_to_transfer(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        target = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: s.structureType == STRUCTURE_CONTAINER or
                              s.structureType == STRUCTURE_STORAGE) \
            .sortBy(lambda s: s.pos.getRangeTo(creep)).first()
        if target:
            creep.memory.duty = 'transferring_to_closest'
            creep.memory.target = target.id
    return target


def decrease_stealers_needed(creep):
    flag = Game.flags[creep.memory.flag]
    need_stealers = flag.memory.need_stealers
    stealers = flag.memory.stealers
    if need_stealers >= stealers:
        need_stealers = need_stealers - 0.01
    flag.memory.need_stealers = round(need_stealers, 2)


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
                    need_additional_workers = home.memory.need_additional_workers
                    need_additional_workers = need_additional_workers + 0.01
                    home.memory.need_additional_workers = need_additional_workers
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
    if creep.store[RESOURCE_ENERGY] < creep.store.getCapacity():
        target = undefined
        fullest_stealer = undefined
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
    return target


def decrease_lorries_needed(creep):
    home = Game.getObjectById(creep.memory.home)
    need_additional_lorries = home.memory.need_additional_lorries
    need_lorries = home.memory.need_lorries
    lorries = home.memory.lorries
    if need_lorries >= lorries + 1:
        need_additional_lorries = need_additional_lorries - 0.01
    home.memory.need_additional_lorries = round(need_additional_lorries, 2)


def check_if_repairing_needed(creep):
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
            creep.memory.repairing = True
    return target


def check_if_building_needed(creep):
    target = creep.pos.findClosestByRange(FIND_CONSTRUCTION_SITES)
    if target:
        creep.memory.building = True
    return target
