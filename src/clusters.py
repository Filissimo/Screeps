import operations
import roles
import tasks
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def cluster_runner(spawn):
    spawn_memory = spawn.memory
    cluster_memory = generate_cluster_memory(spawn)
    del spawn_memory.reserved_rooms
    define_role_to_spawn(spawn, cluster_memory)
    spawn_memory.cluster_memory = cluster_memory


def define_role_to_spawn(spawn, cluster_memory):
    my_creeps = _.filter(Game.creeps, lambda c: c.memory != undefined)
    this_cluster_creeps = _.filter(my_creeps, lambda c: c.memory.cluster == spawn.name)

    for creep in this_cluster_creeps:
        task = creep.memory.task
        if task:
            roles.operate_creep(creep, cluster_memory, task)
        else:
            task = tasks.define_task(creep, cluster_memory)
            if task:
                roles.operate_creep(creep, cluster_memory, task)
            else:
                if not operations.move_away_from_creeps(creep):
                    creep.say('?')

    spawn_memory = spawn.memory
    define_creeps_needed(spawn, cluster_memory)
    spawn_memory.cluster_memory = cluster_memory

    all_roles = ['hauler', 'miner']
    for role_name in all_roles:
        creeps_filtered = _.filter(this_cluster_creeps,
                                   lambda c: c.memory.role == role_name)
        number_of_creeps_filtered = len(creeps_filtered)
        if role_name == 'hauler':
            creeps_virtual = define_virtual_creeps(creeps_filtered)
            cluster_memory.creeps_exist.append({'haulers': creeps_virtual})
            if number_of_creeps_filtered < spawn_memory.creeps_needed.haulers:
                spawning_creep(spawn, role_name)


def define_creeps_needed(spawn, cluster_memory):
    spawn_memory = spawn.memory
    if not spawn_memory.creeps_needed:
        spawn_memory.creeps_needed = {}
    spawn_memory.creeps_needed.haulers = 1
    spawn.memory = spawn_memory


def define_virtual_creeps(creeps_filtered):
    creeps_virtual = []
    for creep_filtered in creeps_filtered:
        creep_virtual = {}
        creep_virtual.id = creep_filtered.id
        if creep_filtered.store.getCapacity() > 0:
            creep_virtual.energy = creep_filtered.store[RESOURCE_ENERGY]
            creep_virtual.capacity = creep_filtered.store.getCapacity()
            creeps_virtual.append(creep_virtual)
    return creeps_virtual


def spawning_creep(spawn, role_name):
    if not spawn.spawning:
        if role_name:
            if Memory.Number_of_creep is undefined:
                Memory.Number_of_creep = 0
            number_of_creep = Memory.Number_of_creep
            desired_body = define_body(spawn, role_name)
            result = spawn.spawnCreep(desired_body,
                                      role_name + '-' + str(number_of_creep),
                                      {'memory': {'role': role_name, 'cluster': spawn.name}})
            if result == OK:
                print(str(desired_body) + ' - job: ' + role_name + ' - spawning.       Capacity: '
                      + spawn.room.energyCapacityAvailable)
                number_of_creep = number_of_creep + 1
                Memory.Number_of_creep = number_of_creep


def define_body(spawn, role_name):
    desired_body = []
    if role_name == 'hauler':
        for a in range(1, 2):
            if spawn.room.energyCapacityAvailable >= a * 150:
                desired_body.extend([CARRY, CARRY, MOVE])
    return desired_body


def define_claimed_room_containers(spawn):
    total_containers_info = {}
    claimed_room_containers_virtual = []
    claimed_room_containers_real = _.filter(spawn.room.find(FIND_STRUCTURES),
                                            lambda s: s.structureType == STRUCTURE_CONTAINER)
    if claimed_room_containers_real:
        total_energy = 0
        total_capacity = 0
        for container_real in claimed_room_containers_real:
            container_virtual = {}
            container_virtual.id = container_real.id
            container_virtual.energy = container_real.store[RESOURCE_ENERGY]
            total_energy = total_energy + container_virtual.energy
            container_virtual.capacity = container_real.store.getCapacity()
            total_capacity = total_capacity + container_virtual.capacity
            container_virtual.energy_percentage = round(container_virtual.energy / container_virtual.capacity * 100)
            claimed_room_containers_virtual.append(container_virtual)
        total_energy_percentage = total_energy / total_capacity * 100

        total_containers_info.energy = total_energy
        total_containers_info.capacity = total_capacity
        total_containers_info.energy_percentage = round(total_energy_percentage)
        total_containers_info.containers = claimed_room_containers_virtual

    return total_containers_info


def define_spawning_structures(spawn):
    total_spawning_structures_info = {}
    spawning_structures_virtual = []
    spawning_structures_real = _.filter(spawn.room.find(FIND_STRUCTURES),
                                        lambda s: s.structureType == STRUCTURE_SPAWN
                                        or s.structureType == STRUCTURE_EXTENSION)
    if spawning_structures_real:
        for spawning_structure_real in spawning_structures_real:
            spawning_structure_virtual = {}
            spawning_structure_virtual.id = spawning_structure_real.id
            spawning_structure_virtual.energy = spawning_structure_real.energy
            spawning_structure_virtual.capacity = spawning_structure_real.energyCapacity
            spawning_structure_virtual.pos = spawning_structure_real.pos
            spawning_structures_virtual.append(spawning_structure_virtual)

    total_spawning_structures_info.energy = spawn.room.energyAvailable
    total_spawning_structures_info.capacity = spawn.room.energyCapacityAvailable
    total_spawning_structures_info.energy_percentage = \
        round(spawn.room.energyAvailable / spawn.room.energyCapacityAvailable * 100)
    total_spawning_structures_info.spawning_structures = spawning_structures_virtual

    return total_spawning_structures_info


def define_claimed_room_sources(spawn):
    claimed_room_sources_virtual = []
    claimed_room_sources_real = spawn.room.find(FIND_SOURCES)
    if claimed_room_sources_real:
        for source_real in claimed_room_sources_real:
            source_virtual = {}
            source_virtual.id = source_real.id
            source_virtual.energy = source_real.energy
            source_virtual.ticks = source_real.ticksToRegeneration
            source_virtual.energy_to_ticks_ratio = round(source_virtual.energy / source_virtual.ticks, 2)
            claimed_room_sources_virtual.append(source_virtual)

    return claimed_room_sources_virtual


def define_claimed_room_containers_test(spawn):
    total_containers_info = {}
    claimed_room_containers_virtual = []
    claimed_room_containers_real = _.filter(spawn.room.find(FIND_STRUCTURES),
                                            lambda s: s.structureType == STRUCTURE_CONTAINER)
    if claimed_room_containers_real:
        total_energy = 0
        total_capacity = 0
        for container_real in claimed_room_containers_real:
            container_virtual = {}
            container_virtual.id = container_real.id
            container_virtual.energy = container_real.store[RESOURCE_ENERGY]
            total_energy = total_energy + container_virtual.energy
            container_virtual.capacity = container_real.store.getCapacity()
            total_capacity = total_capacity + container_virtual.capacity
            container_virtual.energy_percentage = round(container_virtual.energy / container_virtual.capacity * 100)
            claimed_room_containers_virtual.append(container_virtual)
        total_energy_percentage = total_energy / total_capacity * 100

        total_containers_info.energy = total_energy
        total_containers_info.capacity = total_capacity
        total_containers_info.energy_percentage = round(total_energy_percentage)
        total_containers_info.containers = claimed_room_containers_virtual

    return total_containers_info


def define_spawning_structures_test(spawn):
    total_spawning_structures_info = {}
    spawning_structures_virtual = []
    spawning_structures_real = _.filter(spawn.room.find(FIND_STRUCTURES),
                                        lambda s: s.structureType == STRUCTURE_SPAWN
                                        or s.structureType == STRUCTURE_EXTENSION)
    if spawning_structures_real:
        for spawning_structure_real in spawning_structures_real:
            spawning_structure_virtual = {}
            spawning_structure_virtual.id = spawning_structure_real.id
            spawning_structure_virtual.energy = spawning_structure_real.energy
            spawning_structure_virtual.capacity = spawning_structure_real.energyCapacity
            spawning_structure_virtual.pos = spawning_structure_real.pos
            spawning_structures_virtual.append(spawning_structure_virtual)

    total_spawning_structures_info.energy = spawn.room.energyAvailable
    total_spawning_structures_info.capacity = spawn.room.energyCapacityAvailable
    total_spawning_structures_info.energy_percentage = \
        round(spawn.room.energyAvailable / spawn.room.energyCapacityAvailable * 100)
    total_spawning_structures_info.spawning_structures = spawning_structures_virtual

    return total_spawning_structures_info


def define_claimed_room_sources_test(spawn):
    claimed_room_sources_virtual = []
    claimed_room_sources_real = spawn.room.find(FIND_SOURCES)
    if claimed_room_sources_real:
        for source_real in claimed_room_sources_real:
            source_virtual = {}
            source_virtual.id = source_real.id
            source_virtual.energy = source_real.energy
            source_virtual.ticks = source_real.ticksToRegeneration
            source_virtual.energy_to_ticks_ratio = round(source_virtual.energy / source_virtual.ticks, 2)
            claimed_room_sources_virtual.append(source_virtual)

    return claimed_room_sources_virtual


def generate_cluster_memory(spawn):
    cluster_memory = {}
    cluster_memory.claimed_room = {}
    cluster_memory.reserved_rooms = []

    cluster_memory.claimed_room.sources = define_claimed_room_sources(spawn)

    total_containers_info = define_claimed_room_containers(spawn)
    cluster_memory.claimed_room.total_containers_energy = total_containers_info.energy
    cluster_memory.claimed_room.total_containers_capacity = total_containers_info.capacity
    cluster_memory.claimed_room.total_containers_percentage = total_containers_info.energy_percentage
    cluster_memory.claimed_room.containers = total_containers_info.containers

    total_spawning_structures_info = define_spawning_structures(spawn)
    cluster_memory.claimed_room.energy = total_spawning_structures_info.energy
    cluster_memory.claimed_room.capacity = total_spawning_structures_info.capacity
    cluster_memory.claimed_room.energy_percentage = total_spawning_structures_info.energy_percentage
    cluster_memory.claimed_room.spawning_structures = total_spawning_structures_info.spawning_structures

    # total_sources_info_test = define_claimed_room_sources_test(spawn)
    # total_containers_info_test = define_claimed_room_containers_test(spawn)
    # total_spawning_structures_info_test = define_spawning_structures_test(spawn)
    #
    # claimed_room = [total_sources_info_test, total_containers_info_test, total_spawning_structures_info_test]
    # cluster_memory.claimed_room_test = claimed_room

    if spawn.memory.reserved_rooms:
        for flag_name in spawn.memory.reserved_rooms:
            flag = Game.flags[flag_name]
            cluster_memory.reserved_rooms.append(flag.memory)

    cluster_memory.creeps_exist = []

    return cluster_memory
