from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def define_deconstructions(flag):
    if not Memory.deconstructions:
        Memory.deconstructions = []
    deconstructions = Memory.deconstructions
    structures = flag.pos.lookFor(LOOK_STRUCTURES)
    if len(structures) == 0:
        flag.remove()
    else:
        for s in structures:
            deconstructions.append(s.id)
        flag.remove()
        Memory.deconstructions = deconstructions


def define_res_room_containers(flag):
    reserved_room_containers_virtual = []
    reserved_room_containers_real = _.filter(flag.room.find(FIND_STRUCTURES),
                                             lambda s: s.structureType == STRUCTURE_CONTAINER)
    if reserved_room_containers_real:
        for container_real in reserved_room_containers_real:
            container_virtual = {}
            container_virtual.id = container_real.id
            container_virtual.energy = container_real.store[RESOURCE_ENERGY]
            container_virtual.energy_on_the_way = 0
            container_virtual.capacity = container_real.store.getCapacity()
            container_virtual.energy_percentage = round(
                container_virtual.energy / container_virtual.capacity * 100)
            container_virtual.pos = container_real.pos
            sources_virtual = flag.memory.sources
            source_real = _(container_virtual.pos.findInRange(FIND_SOURCES, 2)).sample()
            if source_real:
                for source_virtual in sources_virtual:
                    if source_virtual.id == source_real.id:
                        source_virtual.near_container = True
                        source_virtual.container_id = container_virtual.id
                        container_virtual.near_source = True
            else:
                container_virtual.near_source = False

            container_virtual.hits = container_real.hits
            container_virtual.hitsMax = container_real.hitsMax
            container_virtual.hits_percentage = round(
                container_virtual.hits / container_virtual.hitsMax * 100)

            reserved_room_containers_virtual.append(container_virtual)

    return reserved_room_containers_virtual


def define_res_room_sources(flag):
    reserved_room_sources_virtual = []
    reserved_room_sources_real = flag.room.find(FIND_SOURCES)
    if reserved_room_sources_real:
        for source_real in reserved_room_sources_real:
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
            reserved_room_sources_virtual.append(source_virtual)

    return reserved_room_sources_virtual


def define_res_room_controller(flag):
    controller_real = flag.room.controller
    controller_virtual = {}
    controller_virtual.id = controller_real.id
    if controller_real.reservaton:
        controller_virtual.reservation = controller_real.reservaton
    else:
        controller_virtual.reservation = 0
    return controller_virtual


def flag_runner(flag):
    if flag.name[:3] == 'res':
        spawn = Game.spawns['Spawn' + flag.name[3:4]]
        if not spawn.memory.reserved_rooms:
            spawn.memory.reserved_rooms = []
        reserved_rooms = spawn.memory.reserved_rooms
        reserved_rooms.append(flag.name)
        if flag.room:
            flag.memory.sources = define_res_room_sources(flag)
            flag.memory.containers = define_res_room_containers(flag)
            flag.memory.controller = define_res_room_controller(flag)
            if not flag.memory.reservators:
                flag.memory.reservators = []
            if flag.memory.controller.reservation < 2000:
                flag.memory.need_reservators = 2
            else:
                flag.memory.need_reservators = 1

    if flag.name[:3] == 'tow':
        if flag.room:
            if len(flag.room.find(FIND_CONSTRUCTION_SITES)) == 0:
                flag.pos.createConstructionSite(STRUCTURE_TOWER)
                flag.remove()
    if flag.name[:3] == 'lin':
        if flag.room:
            if len(flag.room.find(FIND_CONSTRUCTION_SITES)) == 0:
                structures = flag.pos.lookFor(LOOK_STRUCTURES)
                if structures:
                    flag.pos.createFlag('dc' + flag.name)
                    flag.pos.createFlag('fut' + flag.name)
                    flag.remove()
                else:
                    flag.pos.createConstructionSite(STRUCTURE_LINK)
                    flag.remove()
    if flag.name[:3] == 'fut':
        if flag.room:
            if len(flag.room.find(FIND_CONSTRUCTION_SITES)) == 0:
                if len(flag.pos.lookFor(LOOK_STRUCTURES)) == 0:
                    flag.pos.createConstructionSite(STRUCTURE_LINK)
                    flag.remove()
    if flag.name[:3] == 'sto':
        if flag.room:
            if len(flag.room.find(FIND_CONSTRUCTION_SITES)) == 0 and flag.room.energyCapacityAvailable >= 1300:
                flag.pos.createConstructionSite(STRUCTURE_STORAGE)
                flag.remove()
    if flag.name[:3] == 'con':
        if flag.room:
            if flag.room.energyCapacityAvailable >= 550:
                if len(flag.room.find(FIND_CONSTRUCTION_SITES)) == 0:
                    flag.pos.createConstructionSite(STRUCTURE_CONTAINER)
                    flag.remove()
            else:
                if flag.room.controller.reservation:
                    if len(flag.room.find(FIND_CONSTRUCTION_SITES)) == 0:
                        flag.pos.createConstructionSite(STRUCTURE_CONTAINER)
                        flag.remove()
    if flag.name[:2] == 'dc':
        if flag.room:
            define_deconstructions(flag)
    if flag.name == 's' or flag.name[:1] == 'e':
        flag_pos = flag.pos
        # flag.remove()
        semicircles = 1.3
        flag_number = 0
        if flag.name[:1] == 'e':
            if len(flag.name) == 2:
                flag_number = int(flag.name[1:2])
            if len(flag.name) == 3:
                flag_number = int(flag.name[1:3])
        starting_flag_number = flag_number
        if flag_number < 10:
            for circle in range(1, 3):
                for direction in range(1, 5):
                    semicircles = semicircles + 0.5
                    for semicircle in range(1, round(semicircles)):
                        if direction == 1:
                            flag_pos.x = flag_pos.x + 1
                            flag_pos.y = flag_pos.y - 1
                            flag_number = place_e_flag(flag_pos, starting_flag_number, flag_number)
                            if starting_flag_number < flag_number:
                                break
                        if direction == 2:
                            flag_pos.x = flag_pos.x + 1
                            flag_pos.y = flag_pos.y + 1
                            flag_number = place_e_flag(flag_pos, starting_flag_number, flag_number)
                            if starting_flag_number < flag_number:
                                break
                        if direction == 3:
                            flag_pos.x = flag_pos.x - 1
                            flag_pos.y = flag_pos.y + 1
                            flag_number = place_e_flag(flag_pos, starting_flag_number, flag_number)
                            if starting_flag_number < flag_number:
                                break
                        if direction == 4:
                            flag_pos.x = flag_pos.x - 1
                            flag_pos.y = flag_pos.y - 1
                            flag_number = place_e_flag(flag_pos, starting_flag_number, flag_number)
                            if starting_flag_number < flag_number:
                                break
    if flag.name == '0':
        for f in Object.keys(Game.flags):
            flag_e = Game.flags[f]
            if flag_e.name[:1] == 'e' or flag_e.name[:1] == 's':
                flag_e.remove()
        flag.remove()


def place_e_flag(position, starting_flag_number, flag_number):
    if 4 < position.x < 45 and 4 < position.y < 45:
        terrain = position.lookFor(LOOK_TERRAIN)
        print(str(terrain) + flag_number)
        structures = position.lookFor(LOOK_STRUCTURES)
        flags = position.lookFor(LOOK_FLAGS)
        if terrain != 'wall' and len(structures) == 0 and len(flags) == 0:
            extensions = _.sum(position.findInRange(FIND_FLAGS, 1), lambda s: s.name[:1] == 'e' or s.name == 's')
            swamps = _.sum(position.findInRange(LOOK_TERRAIN, 3),
                           lambda t: t.type == 'swamp')
            if extensions > 0 and swamps == 0 and flag_number <= starting_flag_number + 3:
                position.createFlag(str('e' + flag_number))
                flag_number = flag_number + 1
    return flag_number
