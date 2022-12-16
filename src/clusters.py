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


def run_links(cluster_memory):
    links = cluster_memory.claimed_room.links
    if len(links) > 1:
        sorted_links = _.sortBy(links, lambda l: l.energy)
        # if sorted_links[len(sorted_links) - 1].near_source and not sorted_links[0].near_source:
        if sorted_links[0].energy < sorted_links[0].free_capacity:
            if sorted_links[len(sorted_links) - 1].cooldown == 0:
                # if sorted_links[0].free_capacity > 0:
                real_link_out = Game.getObjectById(sorted_links[len(sorted_links) - 1].id)
                real_link_in = Game.getObjectById(sorted_links[0].id)
                energy_amount = round((sorted_links[len(sorted_links) - 1].energy - sorted_links[0].energy) / 2)
                real_link_out.transferEnergy(real_link_in, energy_amount)


def cluster_runner(spawn):
    spawn_memory = spawn.memory
    cluster_memory = generate_cluster_memory(spawn)
    del spawn_memory.reserved_rooms
    define_role_to_spawn(spawn, cluster_memory)
    create_extension(spawn)
    run_links(cluster_memory)
    spawn_memory.cluster_memory = cluster_memory


def print_cluster_status(spawn, cluster_memory):
    creeps_exist = cluster_memory.creeps_exist
    creeps_needed = spawn.memory.creeps_needed
    print(spawn.name + ' - Workers: ' + str(len(creeps_exist.workers)) + '/' + round(creeps_needed.workers, 3) +
          ' - Haulers: ' + str(len(creeps_exist.haulers)) + '/' + round(creeps_needed.haulers, 3) +
          ' - Miners: ' + str(len(creeps_exist.miners)) + '/' + creeps_needed.miners +
          '  ')


def define_role_to_spawn(spawn, cluster_memory):
    my_creeps = _.filter(Game.creeps, lambda c: c.memory != undefined)
    this_cluster_creeps = _.filter(my_creeps, lambda c: c.memory.cluster == spawn.name)

    spawn_memory = spawn.memory

    all_roles = ['hauler', 'miner', 'worker', 'guard']
    cluster_memory.creeps_exist = {}
    for role_name in all_roles:
        creeps_filtered = _.filter(this_cluster_creeps,
                                   lambda c: c.memory.role == role_name)
        if role_name == 'hauler':
            creeps_virtual = define_virtual_creeps(creeps_filtered)
            cluster_memory.creeps_exist.haulers = creeps_virtual
        elif role_name == 'worker':
            creeps_virtual = define_virtual_creeps(creeps_filtered)
            cluster_memory.creeps_exist.workers = creeps_virtual
        elif role_name == 'miner':
            creeps_virtual = define_virtual_creeps(creeps_filtered)
            cluster_memory.creeps_exist.miners = creeps_virtual
        elif role_name == 'guard':
            creeps_virtual = define_virtual_creeps(creeps_filtered)
            cluster_memory.creeps_exist.guards = creeps_virtual

    define_spawning_status(spawn, cluster_memory)
    define_creeps_needed(spawn, cluster_memory)
    spawn_memory.cluster_memory = cluster_memory

    if len(cluster_memory.creeps_exist.workers) < spawn_memory.creeps_needed.workers \
            and cluster_memory.enough_miners and cluster_memory.enough_haulers:
        spawning_creep(spawn, 'worker', cluster_memory)
    if cluster_memory.need_small_workers:
        if len(cluster_memory.creeps_exist.workers) < spawn_memory.creeps_needed.workers:
            spawning_creep(spawn, 'worker', cluster_memory)

    if len(cluster_memory.creeps_exist.miners) < spawn_memory.creeps_needed.miners:
        spawning_creep(spawn, 'miner', cluster_memory)

    if len(cluster_memory.creeps_exist.haulers) < spawn_memory.creeps_needed.haulers:
        spawning_creep(spawn, 'hauler', cluster_memory)

    if len(cluster_memory.creeps_exist.guards) < spawn_memory.creeps_needed.guards and \
            cluster_memory.enough_miners and cluster_memory.enough_haulers:
        spawning_creep(spawn, 'guard', cluster_memory)

    for creep in this_cluster_creeps:
        if not creep.spawning:
            roles.run_creep(creep, cluster_memory)

    tasks.define_tasks_for_not_creeps(spawn, cluster_memory)

    print_cluster_status(spawn, cluster_memory)


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


def define_spawning_status(spawn, cluster_memory):
    if (len(cluster_memory.creeps_exist.haulers) < 1
            or cluster_memory.claimed_room.total_containers_energy < 500):
        cluster_memory.restart = True
    else:
        cluster_memory.restart = False
    if len(cluster_memory.creeps_exist.workers) <= 3:
        cluster_memory.need_small_workers = True
    else:
        cluster_memory.need_small_workers = False
    if cluster_memory.creeps_exist and spawn.memory.creeps_needed:
        if len(cluster_memory.creeps_exist.miners) == spawn.memory.creeps_needed.miners:
            cluster_memory.enough_miners = True
        else:
            cluster_memory.enough_miners = False
        if len(cluster_memory.creeps_exist.haulers) >= spawn.memory.creeps_needed.haulers:
            cluster_memory.enough_haulers = True
        else:
            cluster_memory.enough_haulers = False


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
    if not spawn_memory.creeps_needed.guards:
        spawn_memory.creeps_needed.guards = 2
    if cluster_memory.restart:
        sources = cluster_memory.claimed_room.sources
        for source in sources:
            if source.energy_to_ticks_ratio > 10:
                if spawn_memory.creeps_needed.workers < len(sources) * 5:
                    spawn_memory.creeps_needed.workers = spawn_memory.creeps_needed.workers + 0.01
            else:
                if spawn_memory.creeps_needed.workers > 1:
                    spawn_memory.creeps_needed.workers = spawn_memory.creeps_needed.workers - 0.05
    else:
        if cluster_memory.claimed_room.total_containers_percentage > 40:
            spawn_memory.creeps_needed.workers = spawn_memory.creeps_needed.workers + 0.01
        else:
            if spawn_memory.creeps_needed.workers > 1:
                spawn_memory.creeps_needed.workers = spawn_memory.creeps_needed.workers - 0.05

    if len(cluster_memory.claimed_room.containers) > 0:
        sources_near_container = 0
        sources = cluster_memory.claimed_room.sources
        for source in sources:
            if source.near_container:
                sources_near_container = sources_near_container + 1
        spawn_memory.creeps_needed.miners = sources_near_container * 2

        for container in cluster_memory.claimed_room.containers:
            if container.energy_percentage > 80:
                spawn_memory.creeps_needed.haulers = spawn_memory.creeps_needed.haulers + 0.01
            else:
                if spawn_memory.creeps_needed.haulers > 1:
                    spawn_memory.creeps_needed.haulers = spawn_memory.creeps_needed.haulers - 0.01
        for link in cluster_memory.claimed_room.links:
            if link.energy_percentage > 90:
                spawn_memory.creeps_needed.haulers = spawn_memory.creeps_needed.haulers + 0.003

    spawn.memory = spawn_memory


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
                number_of_creep = number_of_creep + 1
                Memory.Number_of_creep = number_of_creep


def define_body(spawn, role_name, cluster_memory):
    desired_body = []
    if role_name == 'hauler':
        for a in range(1, 6):
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
    elif role_name == 'miner':
        if spawn.room.energyCapacityAvailable == 550:
            desired_body.extend([WORK, WORK, WORK, WORK, CARRY, CARRY, MOVE])
        if spawn.room.energyCapacityAvailable >= 600:
            desired_body.extend([WORK, WORK, WORK, WORK, CARRY, CARRY, MOVE, MOVE])
    elif role_name == 'guard':
        for a in range(1, 5):
            if spawn.room.energyCapacityAvailable >= a * 560:
                desired_body.extend([TOUGH])
        for a in range(1, 5):
            if spawn.room.energyCapacityAvailable >= a * 560:
                desired_body.extend([MOVE, MOVE, MOVE])
        for a in range(1, 5):
            if spawn.room.energyCapacityAvailable >= a * 560:
                desired_body.extend([RANGED_ATTACK])
        for a in range(1, 5):
            if spawn.room.energyCapacityAvailable >= a * 560:
                desired_body.extend([HEAL])
    return desired_body


def define_claimed_room_containers(spawn, cluster_memory):
    total_containers_info = {}
    claimed_room_containers_virtual = []
    claimed_room_links_virtual = []
    claimed_room_containers_real = _.filter(spawn.room.find(FIND_STRUCTURES),
                                            lambda s: s.structureType == STRUCTURE_CONTAINER)
    claimed_room_links_real = _.filter(spawn.room.find(FIND_STRUCTURES),
                                       lambda s: s.structureType == STRUCTURE_LINK)
    total_energy = 0
    total_capacity = 0
    if claimed_room_links_real:
        for link_real in claimed_room_links_real:
            link_virtual = {}
            link_virtual.id = link_real.id
            link_virtual.energy = link_real.store[RESOURCE_ENERGY]
            link_virtual.energy_on_the_way = 0
            total_energy = total_energy + link_virtual.energy
            link_virtual.free_capacity = link_real.store.getFreeCapacity(RESOURCE_ENERGY)
            link_capacity = link_virtual.energy + link_virtual.free_capacity
            total_capacity = total_capacity + link_capacity
            link_virtual.energy_percentage = round(link_virtual.energy / link_capacity * 100)
            link_virtual.cooldown = link_real.cooldown
            link_virtual.pos = link_real.pos
            sources_virtual = cluster_memory.claimed_room.sources
            source_real = _(link_real.pos.findInRange(FIND_SOURCES, 2)).sample()
            if source_real:
                for source_virtual in sources_virtual:
                    if source_virtual.id == source_real.id:
                        source_virtual.near_container = True
                        link_virtual.near_source = True
            else:
                link_virtual.near_source = False
            claimed_room_links_virtual.append(link_virtual)

    if claimed_room_containers_real:
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
            sources_virtual = cluster_memory.claimed_room.sources
            source_real = _(container_virtual.pos.findInRange(FIND_SOURCES, 2)).sample()
            if source_real:
                for source_virtual in sources_virtual:
                    if source_virtual.id == source_real.id:
                        source_virtual.near_container = True
                        container_virtual.near_source = True
            else:
                container_virtual.near_source = False
            claimed_room_containers_virtual.append(container_virtual)

    total_energy_percentage = total_energy / total_capacity * 100
    total_containers_info.energy = total_energy
    total_containers_info.capacity = total_capacity
    total_containers_info.energy_percentage = round(total_energy_percentage)
    total_containers_info.containers = claimed_room_containers_virtual
    total_containers_info.links = claimed_room_links_virtual

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


def define_claimed_room_storage(spawn):
    claimed_room_storage_virtual = {}
    claimed_room_storage_real = spawn.room.storage
    if claimed_room_storage_real:
        claimed_room_storage_virtual.id = claimed_room_storage_real.id
        claimed_room_storage_virtual.energy = claimed_room_storage_real.store[RESOURCE_ENERGY]
        claimed_room_storage_virtual.energy_on_the_way = 0
        claimed_room_storage_virtual.capacity = claimed_room_storage_real.store.getCapacity()
        claimed_room_storage_virtual.pos = claimed_room_storage_real.pos

    return claimed_room_storage_virtual


def define_claimed_room_towers(spawn):
    towers_virtual = []
    towers_real = _.filter(spawn.room.find(FIND_STRUCTURES), lambda s: s.structureType == STRUCTURE_TOWER)
    if towers_real:
        for tower_real in towers_real:
            tower_virtual = {}
            tower_virtual.id = tower_real.id
            tower_virtual.energy = tower_real.store[RESOURCE_ENERGY]
            tower_virtual.energy_on_the_way = 0
            tower_virtual.free_capacity = tower_real.store.getFreeCapacity(RESOURCE_ENERGY)
            tower_virtual.capacity = tower_virtual.energy + tower_virtual.free_capacity
            tower_virtual.pos = tower_real.pos
            towers_virtual.append(tower_virtual)

    return towers_virtual


def define_claimed_room_controller(spawn):
    controller_virtual = {}
    controller_real = spawn.room.controller
    controller_virtual.id = controller_real.id
    return controller_virtual


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

    total_containers_info = define_claimed_room_containers(spawn, cluster_memory)
    cluster_memory.claimed_room.total_containers_energy = total_containers_info.energy
    cluster_memory.claimed_room.total_containers_capacity = total_containers_info.capacity
    cluster_memory.claimed_room.total_containers_percentage = total_containers_info.energy_percentage
    cluster_memory.claimed_room.containers = total_containers_info.containers
    cluster_memory.claimed_room.links = total_containers_info.links

    cluster_memory.claimed_room.towers = define_claimed_room_towers(spawn)

    cluster_memory.claimed_room.storage = define_claimed_room_storage(spawn, cluster_memory)

    cluster_memory.claimed_room.controller = define_claimed_room_controller(spawn, cluster_memory)

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
