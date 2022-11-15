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


def define_deliver_for_spawn_target(creep):
    target = undefined
    if _.sum(creep.carry) > 0:
        target = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION)
                               and s.energy < s.energyCapacity)) \
            .sample()
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
            .filter(lambda t: (t.store[RESOURCE_ENERGY] > 0)).first()
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


def define_fullest(creep):
    target = undefined
    if _.sum(creep.carry) <= 0:
        target = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER or
                               s.structureType == STRUCTURE_STORAGE) and
                              s.store[RESOURCE_ENERGY] > s.store.getCapacity() * 0.2) \
            .sortBy(lambda s: s.store[RESOURCE_ENERGY]).last()
        if target:
            creep.memory.duty = 'withdrawing_from_fullest'
            creep.memory.target = target.id
    return target


def define_emptiest(creep):
    target = undefined
    if _.sum(creep.carry) > 0:
        target = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: s.structureType == STRUCTURE_CONTAINER and
                              s.store[RESOURCE_ENERGY] < s.store.getCapacity() * 0.5) \
            .sortBy(lambda s: s.store[RESOURCE_ENERGY]).first()
        if target:
            creep.memory.duty = 'delivering_to_emptiest'
            creep.memory.target = target.id
    return target


def define_storage(creep):
    target = undefined
    if _.sum(creep.carry) > 0:
        target = _.filter(creep.room.find(FIND_STRUCTURES),
                          lambda s: s.structureType == STRUCTURE_STORAGE)
        if target:
            creep.memory.duty = 'delivering_to_storage'
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
                creep.memory.duty = 'go_to_flag'
                if creep.pos.isNearTo(flag):
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
    if creep.memory.job[7:8] == '1':
        need_stealer1s = home.memory.need_stealer1s
        if target.energy > target.ticksToRegeneration * 11:
            need_stealer1s = need_stealer1s + 0.01
        if target.energy < target.ticksToRegeneration * 9:
            need_stealer1s = need_stealer1s - 0.01
        home.memory.need_stealer1s = round(need_stealer1s, 2)

