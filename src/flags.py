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
    if flag.name[:5] == 'Steal':
        need_stealers = flag.memory.need_stealers
        stealers = flag.memory.stealers
        if flag.room:
            sources = flag.room.find(FIND_SOURCES)
            for source in sources:
                if source.energy / source.ticksToRegeneration > 10 or source.energy >= 2500:
                    if need_stealers <= stealers:
                        need_stealers = need_stealers + 0.01
                if source.energy / source.ticksToRegeneration < 10 or source.energy <= 0:
                    if need_stealers >= stealers - 1:
                        need_stealers = need_stealers - 0.01
                flag.memory.need_stealers = round(need_stealers, 2)
            print(flag.name + ': Stealers - ' + stealers + ' / ' + need_stealers)
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


def place_e_flag(position,  starting_flag_number, flag_number):
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



