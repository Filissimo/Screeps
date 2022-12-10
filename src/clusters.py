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
    define_role_ro_spawn(spawn, cluster_memory)


def define_role_ro_spawn(spawn, cluster_memory):
    my_creeps = _.filter(Game.creeps, lambda c: c.memory != undefined)
    this_cluster_creeps = _.filter(my_creeps, lambda c: c.memory.cluster == spawn.name)

    all_roles = ['hauler', 'miner']
    for role_name in all_roles:
        creeps_filtered = _.filter(this_cluster_creeps,
                                   lambda c: c.memory.role == role_name and
                                             c.ticksToLive > 50)
        number_of_creeps_filtered = len(creeps_filtered)
        if role_name == 'hauler':
            if number_of_creeps_filtered < 0:
                spawning_creep(spawn, role_name)


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


def generate_cluster_memory(spawn):
    cluster_memory = {}
    cluster_memory.claimed_room = {}
    cluster_memory.reserved_rooms = []
    claimed_room_containers_real = _.filter(spawn.room.find(FIND_STRUCTURES),
                                            lambda s: s.structureType == STRUCTURE_CONTAINER)

    claimed_room_containers_virtual = []
    if claimed_room_containers_real:
        for container_real in claimed_room_containers_real:
            container_virtual = {}
            container_virtual.energy = container_real.store[RESOURCE_ENERGY]
            container_virtual.capacity = container_real.store.getCapacity()
            container_virtual.energy_percentage = round(container_virtual.energy / container_virtual.capacity * 100)
            claimed_room_containers_virtual.append(container_virtual)

    cluster_memory.claimed_room.containers = claimed_room_containers_virtual

    if spawn.memory.reserved_rooms:
        for flag_name in spawn.memory.reserved_rooms:
            flag = Game.flags[flag_name]
            cluster_memory.reserved_rooms.append(flag.memory)

    return cluster_memory
