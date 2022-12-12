from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def target_repairing(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        need_repairs = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.hits < s.hitsMax * 0.05) and
                              s.structureType != STRUCTURE_WALL) \
            .sortBy(lambda s: (s.hitsMax / s.hits)).last()
        if need_repairs != undefined:
            do_not_repairs = Memory.deconstructions
            if do_not_repairs:
                for do_not_repair in do_not_repairs:
                    if need_repairs:
                        if need_repairs.id == do_not_repair:
                            target = undefined
                        else:
                            target = need_repairs
                            creep.memory.task = 'repairing'
                            creep.memory.target = target.id
    return target


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
                creep.memory.task = 'dismantling'
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


def target_worker_mining(creep, cluster_memory):
    target = undefined
    if creep.store[RESOURCE_ENERGY] <= 0:
        fullest_source = _(cluster_memory.claimed_room.sources) \
            .sortBy(lambda s: s.processed_energy_to_ticks_ratio).last()
        if fullest_source:
            if fullest_source.processed_energy_of_source > - creep.store.getCapacity():
                target = fullest_source
                creep.memory.task = 'worker_mining'
                creep.memory.target = target.id
    return target


def target_building(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        target = creep.pos.findClosestByRange(FIND_CONSTRUCTION_SITES)
        if target:
            creep.memory.task = 'building'
            creep.memory.target = target.id
    return target


def target_upgrading(creep):
    target = undefined
    if creep.store[RESOURCE_ENERGY] > 0:
        home = Game.spawns[creep.memory.cluster]
        controller = home.room.controller
        if controller:
            target = controller
            creep.memory.task = 'upgrading'
            creep.memory.target = target.id
    return target


def define_worker_task(creep, cluster_memory):
    if not target_dismantling(creep):
        if not target_withdraw_from_closest(creep):
            if not target_worker_mining(creep, cluster_memory):
                if not target_repairing(creep):
                    if not target_building(creep):
                        target_upgrading(creep)


def define_hauler_task(creep, cluster_memory):
    if not target_fullest_container(creep, cluster_memory):
        target_emptiest_container(creep, cluster_memory)


def define_task(creep, cluster_memory):
    if creep.memory.task != 'delivered_for_spawning':
        creep.memory.delivered = False
        del creep.memory.task
        del creep.memory.target
        del creep.memory.path
        del creep.memory.move
        role = creep.memory.role
        if role == 'hauler':
            define_hauler_task(creep, cluster_memory)
        if role == 'worker':
            define_worker_task(creep, cluster_memory)
    print(creep.memory.delivered + creep.name)


def define_creep_to_deliver_for_spawning(spawn, cluster_memory):
    if cluster_memory.claimed_room.energy + cluster_memory.claimed_room.energy_on_the_way \
            < cluster_memory.claimed_room.capacity:
        if cluster_memory.restart:
            creep = _(spawn.room.find(FIND_CREEPS)) \
                .filter(lambda c: c.store[RESOURCE_ENERGY] >= 50
                                  and c.memory.task != 'worker_mining'
                                  and c.memory.task != 'miner_mining'
                                  and c.memory.task != 'transfer_to_spawning_structure') \
                .sortBy(lambda c: c.pos.getRangeTo(spawn)) \
                .first()
        else:
            creep = _(spawn.room.find(FIND_CREEPS)) \
                .filter(lambda c: c.store[RESOURCE_ENERGY] >= 50
                                  and c.memory.role == 'hauler'
                                  and c.memory.task != 'transfer_to_spawning_structure') \
                .sortBy(lambda c: c.pos.getRangeTo(spawn)) \
                .first()
        if creep:
            spawning_structure = _(cluster_memory.claimed_room.spawning_structures) \
                .filter(lambda s: s.energy < s.capacity) \
                .sortBy(lambda s: s.pos.getRangeTo(creep)) \
                .last()
            if spawning_structure:
                creep.memory.target = spawning_structure.id
                creep.memory.task = 'transfer_to_spawning_structure'
                del creep.memory.path
                del creep.memory.move


def define_another_spawning_structure(creep, cluster_memory):
    if cluster_memory.claimed_room.energy_percentage < 100:
        spawning_structure = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.structureType == STRUCTURE_SPAWN
                    or s.structureType == STRUCTURE_EXTENSION)
                    and s.energy < s.energyCapacity) \
            .sortBy(lambda s: s.pos.getRangeTo(creep)) \
            .last()
        if spawning_structure:
            creep.memory.target = spawning_structure.id
            creep.memory.task = 'transfer_to_spawning_structure'
            del creep.memory.path
            del creep.memory.move
    else:
        del creep.memory.task


def define_creep_to_pickup_tombstone(spawn):
    tombstones = _.filter(spawn.room.find(FIND_TOMBSTONES), lambda t: t.store[RESOURCE_ENERGY] > 0)
    if tombstones:
        spawn_memory = spawn.memory
        if not spawn_memory.tombstones:
            spawn_memory.tombstones = []
        for tombstone in tombstones:
            tombstone_virtual_exists = False
            for tombstone_virtual in spawn_memory.tombstones:
                tombstone_to_delete = Game.getObjectById(tombstone_virtual.id)
                if not tombstone_to_delete:
                    spawn_memory.tombstones.remove(tombstone_virtual)
                elif tombstone_to_delete.store[RESOURCE_ENERGY] == 0:
                    spawn_memory.tombstones.remove(tombstone_virtual)
                if tombstone_virtual.id == tombstone.id:
                    tombstone_virtual_exists = True
                    if tombstone_virtual.energy + tombstone_virtual.energy_on_the_way > 0:
                        creep = _(tombstone.room.find(FIND_CREEPS)) \
                            .filter(lambda c: (c.store[RESOURCE_ENERGY] <= 0) and
                                              (c.memory.role == 'hauler' or c.memory.role == 'worker' or
                                               (c.memory.role == 'miner' and c.pos.isNearTo(tombstone)))) \
                            .sortBy(lambda c: c.pos.getRangeTo(tombstone)) \
                            .first()
                        if creep:
                            creep.memory.task = 'withdraw_by_memory'
                            creep.memory.target = tombstone.id
                            del creep.memory.path
                            del creep.memory.move
            if not tombstone_virtual_exists:
                tombstone_virtual = {}
                tombstone_virtual.id = tombstone.id
                tombstone_virtual.energy = tombstone.store[RESOURCE_ENERGY]
                tombstone_virtual.energy_on_the_way = 0
                spawn_memory.tombstones.append(tombstone_virtual)


def define_tasks_for_not_creeps(spawn, cluster_memory):
    define_creep_to_deliver_for_spawning(spawn, cluster_memory)
    define_creep_to_pickup_tombstone(spawn)
