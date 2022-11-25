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


def flag_runner(flag):
    if flag.name[:3] == 'sto':
        if flag.room:
            if len(flag.room.find(FIND_CONSTRUCTION_SITES)) == 0:
                flag.pos.createConstructionSite(STRUCTURE_STORAGE)
                flag.remove()
    if flag.name[:3] == 'con':
        if flag.room:
            if flag.room.energyCapacityAvailable >= 400:
                if len(flag.room.find(FIND_CONSTRUCTION_SITES)) == 0:
                    flag.pos.createConstructionSite(STRUCTURE_CONTAINER)
                    flag.remove()
            else:
                if flag.room.controller.reservation:
                    if len(flag.room.find(FIND_CONSTRUCTION_SITES)) == 0:
                        flag.pos.createConstructionSite(STRUCTURE_CONTAINER)
                        flag.remove()
    if flag.name[:5] == 'Steal':
        if flag.room:
            stealers_in_the_room = _.filter(flag.room.find(FIND_MY_CREEPS), lambda c: c.memory.job == 'stealer' and
                                            c.ticksToLive > 100)
            flag.memory.stealers_in_the_room = len(stealers_in_the_room)
            total_carry = 0
            total_carryCapacity = 0
            one_stealer_capacity = 0
            for stealer_in_the_room in stealers_in_the_room:
                total_carry = total_carry + stealer_in_the_room.store[RESOURCE_ENERGY]
                total_carryCapacity = total_carryCapacity + stealer_in_the_room.store.getCapacity()
                one_stealer_capacity = stealer_in_the_room.store.getCapacity()
            sources = flag.room.find(FIND_SOURCES)
            if len(sources) * 300 > total_carryCapacity or flag.memory.need_additional_stealers > 0:
                flag.memory.give_stealers = True
            else:
                flag.memory.give_stealers = False
            if sources:
                if len(sources) * 300 < total_carryCapacity - one_stealer_capacity and \
                        flag.memory.need_additional_stealers == 0:
                    flag.memory.take_stealers = True
                else:
                    flag.memory.take_stealers = False
            if not flag.memory.need_lorries:
                flag.memory.need_lorries = 0
            factor = total_carryCapacity / 20
            need_lorries = flag.memory.need_lorries
            if len(stealers_in_the_room) > 0:
                if total_carry > 0:
                    if total_carryCapacity / total_carry < factor:
                        if need_lorries < len(stealers_in_the_room) * 3:
                            need_lorries = need_lorries + 0.01
                            # home.memory.need_additional_lorries = home.memory.need_additional_lorries + 0.01
                    else:
                        if need_lorries > 0:
                            need_lorries = need_lorries - 0.01
                            # home.memory.need_additional_lorries = home.memory.need_additional_lorries - 0.05
                lorries = flag.memory.lorries
                if lorries < need_lorries and len(stealers_in_the_room) > lorries:
                    flag.memory.give_lorries = True
                if lorries > need_lorries + 1:
                    flag.memory.give_lorries = False
                flag.memory.need_lorries = round(need_lorries, 2)
            else:
                flag.memory.need_lorries = 0
            print('      ' + flag.name +
                  '  -  Stealers: ' +
                  str(len(stealers_in_the_room)) + '. Need more: ' + str(flag.memory.give_stealers) +
                  ' - ' + str(total_carryCapacity) + '/' + str(total_carry) + '=' +
                  round((total_carryCapacity / (total_carry + 1)), 2) + '(factor=' + round(factor, 2) + ')' +
                  '.  Lorries: ' + str(lorries) + '/' + round(need_lorries, 2))
    if flag.name[:2] == 'dc':
        define_deconstructions(flag)
    if flag.name[:5] == 'claim':
        Memory.claim = flag.name
    if flag.name == 'BS':
        need_spawn_builders = flag.memory.need_spawn_builders
        spawn_builders = flag.memory.spawn_builders
        sources = flag.room.find(FIND_SOURCES)
        for source in sources:
            if source.energy > source.ticksToRegeneration * 10 or source.energy >= 2900:
                if need_spawn_builders <= spawn_builders:
                    need_spawn_builders = need_spawn_builders + 0.01
            if source.energy / source.ticksToRegeneration < 8 or source.energy <= 0:
                if need_spawn_builders >= spawn_builders - 1:
                    need_spawn_builders = need_spawn_builders - 0.02
            flag.memory.need_spawn_builders = round(need_spawn_builders, 2)
        print(flag.name + ': spawn_builders - ' + spawn_builders + ' / ' + need_spawn_builders)
        if flag.room.energyCapacityAvailable > 0:
            flag.remove()
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
