from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def define_worker_task(creep, cluster_memory):
    if not target_dismantling(creep):
        if not target_withdraw_from_closest(creep):
            if not target_worker_mining(creep):
                if not target_spawning_structure(creep, cluster_memory):
                    if not target_repairing(creep):
                        if not target_building(creep):
                            target_upgrading(creep)


def define_hauler_task(creep, cluster_memory):
    if not target_fullest_container(creep, cluster_memory):
        if not target_spawning_structure(creep, cluster_memory):
            target_emptiest_container(creep, cluster_memory)


def define_task(creep, cluster_memory):
    del creep.memory.task
    del creep.memory.target
    role = creep.memory.role
    if role == 'hauler':
        define_hauler_task(creep, cluster_memory)
    if role == 'worker':
        define_worker_task(creep, cluster_memory)


def target_fullest_container(creep, cluster_memory):
    target = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        fullest_container = _(cluster_memory.claimed_room.containers).sortBy(lambda c: c.energy).last()
        if fullest_container:
            if fullest_container.energy_percentage > 50:
                target = fullest_container
                creep.memory.target = target.id
                creep.memory.task = 'withdraw_by_memory'
    return target


def target_emptiest_container(creep, cluster_memory):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        emptiest_container = _(cluster_memory.claimed_room.containers).sortBy(lambda c: c.energy).first()
        if emptiest_container:
            if emptiest_container.energy_percentage < 50:
                target = emptiest_container
                creep.memory.target = target.id
                creep.memory.task = 'transfer_by_memory'
    return target


def target_spawning_structure(creep, cluster_memory):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        spawning_structure = _(cluster_memory.claimed_room.spawning_structures) \
            .filter(lambda s: s.energy < s.capacity) \
            .sortBy(lambda s: s.pos.getRangeTo(creep)).first()
        if spawning_structure:
            target = spawning_structure
            creep.memory.target = target.id
            creep.memory.task = 'transfer_to_spawning_structure'
    return target


def target_dismantling(creep):
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


def target_withdraw_from_closest(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        container = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER or
                               s.structureType == STRUCTURE_STORAGE
                               or s.structureType == STRUCTURE_LINK
                               or s.structureType == STRUCTURE_TERMINAL) and
                              s.store[RESOURCE_ENERGY] >= creep.store.getCapacity()) \
            .sortBy(lambda s: s.pos.getRangeTo(creep)).first()
        if container:
            target = container
            creep.memory.duty = 'withdraw_from_closest'
            creep.memory.target = target.id
    return target
