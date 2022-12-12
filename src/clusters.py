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
    create_extension(spawn)
    spawn_memory.cluster_memory = cluster_memory


def print_cluster_status(spawn, cluster_memory):
    creeps_exist = cluster_memory.creeps_exist
    creeps_needed = spawn.memory.creeps_needed
    print(spawn.name + ' - Workers: ' + str(len(creeps_exist.workers)) + '/' + round(creeps_needed.workers, 3) +
          '  ')


def define_role_to_spawn(spawn, cluster_memory):
    my_creeps = _.filter(Game.creeps, lambda c: c.memory != undefined)
    this_cluster_creeps = _.filter(my_creeps, lambda c: c.memory.cluster == spawn.name)

    for creep in this_cluster_creeps:
        if not creep.spawning:
            roles.run_creep(creep, cluster_memory)

    define_spawning_status(cluster_memory)
    tasks.define_tasks_for_not_creeps(spawn, cluster_memory)

    spawn_memory = spawn.memory
    define_creeps_needed(spawn, cluster_memory)
    spawn_memory.cluster_memory = cluster_memory

    all_roles = ['hauler', 'miner', 'worker']
    cluster_memory.creeps_exist = {}
    for role_name in all_roles:
        creeps_filtered = _.filter(this_cluster_creeps,
                                   lambda c: c.memory.role == role_name)
        number_of_creeps_filtered = len(creeps_filtered)
        if role_name == 'hauler':
            creeps_virtual = define_virtual_creeps(creeps_filtered)
            cluster_memory.creeps_exist.haulers = creeps_virtual
            if number_of_creeps_filtered < spawn_memory.creeps_needed.haulers:
                spawning_creep(spawn, role_name, cluster_memory)
        if role_name == 'worker':
            creeps_virtual = define_virtual_creeps(creeps_filtered)
            cluster_memory.creeps_exist.workers = creeps_virtual
            if number_of_creeps_filtered < spawn_memory.creeps_needed.workers:
                spawning_creep(spawn, role_name, cluster_memory)
    print_cluster_status(spawn, cluster_memory)


def define_spawning_status(cluster_memory):
    if (len(cluster_memory.creeps_exist.haulers) < 3
        or cluster_memory.claimed_room.total_containers_energy < 500) \
            and len(cluster_memory.creeps_exist.workers) < 3:
        cluster_memory.restart = True
    else:
        cluster_memory.restart = False
    if len(cluster_memory.creeps_exist.workers) >= 3:
        cluster_memory.need_small_workers = True
    else:
        cluster_memory.need_small_workers = False


def define_creeps_needed(spawn, cluster_memory):
    spawn_memory = spawn.memory
    if not spawn_memory.creeps_needed:
        spawn_memory.creeps_needed = {}
    if len(cluster_memory.claimed_room.containers) == 0:
        spawn_memory.creeps_needed.haulers = 0
    if not spawn_memory.creeps_needed.workers:
        spawn_memory.creeps_needed.workers = 1
    if not spawn_memory.creeps_needed.miners:
        spawn_memory.creeps_needed.miners = 0
    if not spawn_memory.creeps_needed.haulers:
        spawn_memory.creeps_needed.haulers = 0
    if cluster_memory.restart:
        sources = cluster_memory.claimed_room.sources
        for source in sources:
            if source.energy_to_ticks_ratio > 10:
                if spawn_memory.creeps_needed.workers < len(sources) * 5:
                    spawn_memory.creeps_needed.workers = spawn_memory.creeps_needed.workers + 0.01
            else:
                if spawn_memory.creeps_needed.workers > 1:
                    spawn_memory.creeps_needed.workers = spawn_memory.creeps_needed.workers - 0.001

    if len(cluster_memory.claimed_room.containers) > 0:
        mines_near_container = 0
        sources = spawn.room.find(FIND_SOURCES)
        for source in sources:
            mine_near_container = _.filter(source.pos.findInRange(FIND_STRUCTURES, 2),
                                           lambda s: (s.structureType == STRUCTURE_CONTAINER
                                                      or s.structureType == STRUCTURE_LINK))

            if len(mine_near_container) == 0:
                create_container(source)
            else:
                mines_near_container = mines_near_container + 1
        spawn_memory.creeps_needed.miners = mines_near_container * 2

        for container in cluster_memory.claimed_room.containers:
            if container.energy_percentage > 80:
                spawn_memory.creeps_needed.haulers = spawn_memory.creeps_needed.haulers + 0.01
            else:
                spawn_memory.creeps_needed.haulers = spawn_memory.creeps_needed.haulers - 0.001

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


def spawning_creep(spawn, role_name, cluster_memory):
    if not spawn.spawning:
        if role_name:
            if Memory.Number_of_creep is undefined:
                Memory.Number_of_creep = 0
            number_of_creep = Memory.Number_of_creep
            desired_body = define_body(spawn, role_name, cluster_memory)
            result = spawn.spawnCreep(desired_body,
                                      role_name + '-' + str(number_of_creep),
                                      {'memory': {'role': role_name, 'cluster': spawn.name}})
            if result == OK:
                # print(str(desired_body) + ' - job: ' + role_name + ' - spawning.       Capacity: '
                #       + spawn.room.energyCapacityAvailable)
                number_of_creep = number_of_creep + 1
                Memory.Number_of_creep = number_of_creep


def define_body(spawn, role_name, cluster_memory):
    desired_body = []
    if role_name == 'hauler':
        for a in range(1, 2):
            if spawn.room.energyCapacityAvailable >= a * 150:
                desired_body.extend([CARRY, CARRY, MOVE])
    elif role_name == 'worker':
        for a in range(1, 11):
            if cluster_memory.need_small_workers:
                if spawn.room.energyAvailable >= a * 200:
                    desired_body.extend([WORK, CARRY, MOVE])
            else:
                if spawn.room.energyCapacityAvailable >= a * 200:
                    desired_body.extend([WORK, CARRY, MOVE])
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
            container_virtual.energy_on_the_way = 0
            total_energy = total_energy + container_virtual.energy
            container_virtual.capacity = container_real.store.getCapacity()
            total_capacity = total_capacity + container_virtual.capacity
            container_virtual.energy_percentage = round(container_virtual.energy / container_virtual.capacity * 100)
            container_virtual.pos = container_real.pos
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
            source_virtual.energy_on_the_way = 0
            if source_real.ticksToRegeneration == undefined:
                source_virtual.ticks = 1
            else:
                source_virtual.ticks = source_real.ticksToRegeneration
            processed_energy_of_source = source_virtual.energy + source_virtual.energy_on_the_way
            source_virtual.processed_energy_of_source = processed_energy_of_source
            source_virtual.processed_energy_to_ticks_ratio = round(processed_energy_of_source / source_virtual.ticks, 2)
            source_virtual.energy_to_ticks_ratio = round(source_virtual.energy / source_virtual.ticks, 2)
            source_virtual.pos = source_real.pos
            claimed_room_sources_virtual.append(source_virtual)

    return claimed_room_sources_virtual


def generate_cluster_memory(spawn):
    cluster_memory = {}
    cluster_memory.claimed_room = {}
    cluster_memory.reserved_rooms = []

    total_spawning_structures_info = define_spawning_structures(spawn)
    cluster_memory.claimed_room.energy = total_spawning_structures_info.energy
    cluster_memory.claimed_room.energy_on_the_way = 0
    cluster_memory.claimed_room.capacity = total_spawning_structures_info.capacity
    cluster_memory.claimed_room.energy_percentage = total_spawning_structures_info.energy_percentage
    cluster_memory.claimed_room.spawning_structures = total_spawning_structures_info.spawning_structures

    cluster_memory.claimed_room.sources = define_claimed_room_sources(spawn)

    total_containers_info = define_claimed_room_containers(spawn)
    cluster_memory.claimed_room.total_containers_energy = total_containers_info.energy
    cluster_memory.claimed_room.total_containers_capacity = total_containers_info.capacity
    cluster_memory.claimed_room.total_containers_percentage = total_containers_info.energy_percentage
    cluster_memory.claimed_room.containers = total_containers_info.containers

    if spawn.memory.reserved_rooms:
        for flag_name in spawn.memory.reserved_rooms:
            flag = Game.flags[flag_name]
            cluster_memory.reserved_rooms.append(flag.memory)

    cluster_memory.creeps_exist = []

    return cluster_memory


def create_extension(spawn):
    if len(spawn.room.find(FIND_CONSTRUCTION_SITES)) == 0:
        deconstructions = Memory.deconstructions
        have_to_dismantle_in_the_room = False
        if deconstructions:
            for deconstruction in deconstructions:
                deconstruction_site = Game.getObjectById(deconstruction)
                if deconstruction_site:
                    if deconstruction_site.room == spawn.room:
                        have_to_dismantle_in_the_room = True
        if not have_to_dismantle_in_the_room:
            controller_lvl = spawn.room.controller.level
            extensions = _.filter(spawn.room.find(FIND_STRUCTURES), lambda s: s.structureType == STRUCTURE_EXTENSION)
            if controller_lvl == 2:
                if len(extensions) < 5:
                    if verify_square_and_place_extension(spawn.pos):
                        return
                    for extension in extensions:
                        if verify_square_and_place_extension(extension.pos):
                            return
            elif controller_lvl > 2:
                if len(extensions) < (controller_lvl - 2) * 10:
                    if verify_square_and_place_extension(spawn.pos):
                        return
                    for extension in extensions:
                        if verify_square_and_place_extension(extension.pos):
                            return


def verify_square_and_place_extension(position):
    semicircles = 1.3
    for circle in range(1, 3):
        for direction in range(1, 5):
            semicircles = semicircles + 0.5
            for semicircle in range(1, round(semicircles)):
                if direction == 1:
                    position.x = position.x + 1
                    position.y = position.y - 1
                    extension_placed = place_extension(position)
                    if extension_placed:
                        return extension_placed
                if direction == 2:
                    position.x = position.x + 1
                    position.y = position.y + 1
                    extension_placed = place_extension(position)
                    if extension_placed:
                        return extension_placed
                if direction == 3:
                    position.x = position.x - 1
                    position.y = position.y + 1
                    extension_placed = place_extension(position)
                    if extension_placed:
                        return extension_placed
                if direction == 4:
                    position.x = position.x - 1
                    position.y = position.y - 1
                    extension_placed = place_extension(position)
                    if extension_placed:
                        return extension_placed


def place_extension(position):
    if 4 < position.x < 45 and 4 < position.y < 45:
        terrain = position.lookFor(LOOK_TERRAIN)
        structures = position.lookFor(LOOK_STRUCTURES)
        roads = _.filter(position.lookFor(LOOK_STRUCTURES), lambda s: s.structureType == STRUCTURE_ROAD)
        if terrain != 'wall' and len(roads) > 0:
            position.createFlag('dc' + roads[0].id)
            extension_placed = True
            return extension_placed
        elif terrain != 'wall' and len(structures) == 0:
            extensions = _.sum(position.findInRange(FIND_STRUCTURES, 1),
                               lambda s: s.structureType == STRUCTURE_EXTENSION or
                                         s.structureType == STRUCTURE_SPAWN)
            if extensions > 0:
                position.createConstructionSite(STRUCTURE_EXTENSION)
                extension_placed = True
                return extension_placed


def create_container(source):
    if source.room.energyCapacityAvailable >= 550:
        if len(source.room.find(FIND_CONSTRUCTION_SITES)) == 0:
            flag = _(source.pos.findInRange(FIND_FLAGS, 2)).filter(lambda f: f.name[:3] == 'con').sample()
            if flag:
                flag.pos.createConstructionSite(STRUCTURE_CONTAINER)
                flag.remove()
