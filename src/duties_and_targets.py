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
    if _.sum(creep.carry) <= 0:
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
    if _.sum(creep.carry) <= 0:
        target = creep.pos.findClosestByPath(FIND_SOURCES_ACTIVE)
        if target:
            creep.memory.duty = 'mining'
            creep.memory.target = target.id
    return target


def define_stealing_target(creep):
    target = undefined
    if _.sum(creep.carry) <= 0:
        sources = creep.room.find(FIND_SOURCES_ACTIVE)
        for source in sources:
            coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                 lambda c: (c.memory.target == source.id))
            if len(coworkers) < 2:
                target = source
                if target:
                    creep.memory.duty = 'mining'
                    creep.memory.target = target.id
    return target


def define_deliver_for_spawn_target(creep):
    target = undefined
    if _.sum(creep.carry) > 0:
        spawning_structures = _.filter(creep.room.find(FIND_STRUCTURES),
                                       lambda s: (s.structureType == STRUCTURE_SPAWN or
                                       s.structureType == STRUCTURE_EXTENSION) and
                                       s.energy < s.energyCapacity)
        if spawning_structures:
            for spawning_structure in spawning_structures:
                coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                     lambda c: (c.memory.target == spawning_structure.id))
                if len(coworkers) == 0:
                    target = spawning_structure
                    if target:
                        creep.memory.duty = 'delivering_for_spawn'
                        creep.memory.target = target.id
    return target


def define_building_target(creep):
    target = undefined
    if _.sum(creep.carry) > 0:
        target = creep.pos.findClosestByRange(FIND_CONSTRUCTION_SITES)
        if target:
            creep.memory.duty = 'building'
            creep.memory.target = target.id
    return target


def define_upgrading_target(creep):
    target = undefined
    if _.sum(creep.carry) > 0:
        target = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.structureType == STRUCTURE_CONTROLLER)) \
            .sample()
        if target:
            creep.memory.duty = 'upgrading'
            creep.memory.target = target.id
    return target


def define_repairing_target(creep):
    target = undefined
    if _.sum(creep.carry) > 0:
        target = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.hits < s.hitsMax * 0.05)) \
            .sortBy(lambda s: (s.hitsMax / s.hits)).last()
        if target:
            creep.memory.duty = 'repairing'
            creep.memory.target = target.id
    return target


def define_creep_to_pickup_tombstone(creep):
    target = undefined
    if _.sum(creep.carry) < creep.carryCapacity:
        target = _(creep.room.find(FIND_TOMBSTONES)) \
            .filter(lambda t: (t.store[RESOURCE_ENERGY] > 0 and
                               t.id != creep.memory.target)).first()
        if target != undefined:
            creep_to_pickup = _(creep.room.find(FIND_MY_CREEPS)) \
                .filter(lambda c: (c.carryCapacity > _.sum(c.carry)) and
                                  (c.memory.job == 'lorry' or
                                   c.memory.job[:7] == 'stealer')) \
                .sortBy(lambda c: (c.pos.getRangeTo(target))).first()
            if creep_to_pickup:
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
                print(emptiest_container.total_energy_of_container + '  emptiest  ' + emptiest_container.id)
    if emptiest_container:
        if emptiest_container.total_energy_of_container < emptiest_container.store.getCapacity() * 0.5:
            creep.memory.duty = 'delivering_to_emptiest'
            target = emptiest_container
            creep.memory.target = target.id
    return target


def define_fullest(creep):
    target = undefined
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
                target = _(containers).sortBy(lambda c: c.total_energy_of_container).last()
                print(target.total_energy_of_container + '  fullest  ' + target.id)

    if target:
        creep.memory.duty = 'withdrawing_from_fullest'
        creep.memory.target = target.id
    return target


def define_storage_to_deliver(creep):
    target = undefined
    if _.sum(creep.carry) > 0:
        target = _.filter(creep.room.find(FIND_STRUCTURES),
                          lambda s: s.structureType == STRUCTURE_STORAGE)
        if target[0]:
            creep.memory.duty = 'delivering_to_storage'
            creep.memory.target = target[0].id
    return target


def define_storage_to_withdraw(creep):
    target = undefined
    if _.sum(creep.carry) <= 0:
        target = _.filter(creep.room.find(FIND_STRUCTURES),
                          lambda s: s.structureType == STRUCTURE_STORAGE)
        if target[0]:
            creep.memory.duty = 'withdrawing_from_storage'
            creep.memory.target = target[0].id
    return target


def define_reservators_flag(creep):
    home = Game.getObjectById(creep.memory.home)
    flag = Game.flags["Steal" + home.name[5:6] + creep.name[10:11]]
    if flag:
        creep.memory.flag = flag.name
        creep.memory.duty = 'go_to_flag'
        if creep.pos.isNearTo(flag):
            flag = undefined
            del creep.memory.duty
    return flag


def define_controller(creep):
    controller = _(creep.room.find(FIND_STRUCTURES)) \
        .filter(lambda s: s.structureType == STRUCTURE_CONTROLLER).sample()
    if controller:
        creep.memory.controller = controller.id
        creep.memory.duty = 'reserving'
    return controller


def define_going_home(creep):
    home = undefined
    if _.sum(creep.carry) > 0:
        home = Game.getObjectById(creep.memory.home)
        if home.room != creep.room:
            creep.memory.duty = 'going_home'
            creep.memory.target = home.id
    return home


def define_stealers_flag(creep):
    flag = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        home = Game.getObjectById(creep.memory.home)
        flag = Game.flags["Steal" + home.name[5:6] + creep.memory.job[7:8]]
        if flag:
            if creep.room == home.room:
                creep.memory.flag = flag.name
                creep.memory.target = flag.name
                creep.memory.duty = 'go_to_flag'
                if creep.pos.inRangeTo(flag, 5):
                    flag = undefined
                    del creep.memory.duty
            else:
                flag = undefined
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


def define_stealers_needed(creep):
    target = Game.getObjectById(creep.memory.target)
    home = Game.getObjectById(creep.memory.home)
    if target:
        if creep.memory.job[7:8] == '1':
            need_stealer1s = home.memory.need_stealer1s
            stealer1s = home.memory.stealer1s
            if target.energy > target.ticksToRegeneration * 12 or target.energy >= 2000:
                if need_stealer1s <= stealer1s:
                    need_stealer1s = need_stealer1s + 0.01
                    need_additional_workers = home.memory.need_additional_workers
                    need_additional_workers = need_additional_workers + 0.01
                    home.memory.need_additional_workers = need_additional_workers
            if target.energy / target.ticksToRegeneration < 8:
                if need_stealer1s >= stealer1s - 1.5:
                    need_stealer1s = need_stealer1s - 0.01
            home.memory.need_stealer1s = round(need_stealer1s, 2)


def define_wall(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        target = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: s.structureType == STRUCTURE_WALL) \
            .sortBy(lambda s: s.pos.getRangeTo(creep)).first()
        if target:
            creep.memory.duty = 'working_with_wall'
            creep.memory.target = target.id
    return target
