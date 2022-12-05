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
    if flag.name[:5] == 'Steal':
        if flag.room:
            enemies = flag.room.find(FIND_HOSTILE_CREEPS, {'filter': lambda e: e.owner.username != 'rep71Le'})
            if len(enemies) <= 0:
                sources = flag.room.find(FIND_SOURCES)
                mines_near_container = 0
                for source in sources:
                    mine_near_container = _.filter(source.pos.findInRange(FIND_STRUCTURES, 2),
                                                   lambda s: (s.structureType == STRUCTURE_CONTAINER
                                                              or s.structureType == STRUCTURE_LINK))

                    if len(mine_near_container) == 1:
                        mines_near_container = mines_near_container + 1
                flag_memory = flag.memory
                flag_memory.need_miners = mines_near_container * 2
                if mines_near_container < len(sources):
                    if not flag_memory.need_stealers:
                        flag_memory.need_stealers = 3
                    need_stealers = flag_memory.need_stealers
                    stealers = flag_memory.stealers
                    for source in sources:
                        if source.energy >= 3000 or source.energy / source.ticksToRegeneration > 10:
                            if need_stealers < stealers + 2:
                                need_stealers = need_stealers + 0.05
                                if stealers == 0:
                                    need_stealers = 3
                        if source.energy / source.ticksToRegeneration < 8 or source.energy <= 0:
                            if need_stealers > 1:
                                need_stealers = need_stealers - 0.001
                    flag_memory.need_stealers = need_stealers
                else:
                    need_repairs = _(flag.room.find(FIND_STRUCTURES)) \
                        .filter(lambda s: (s.hits < s.hitsMax * 0.2) and
                                          s.structureType != STRUCTURE_WALL) \
                        .sortBy(lambda s: (s.hitsMax / s.hits)).last()
                    if need_repairs:
                        do_not_repairs = Memory.deconstructions
                        if do_not_repairs:
                            for do_not_repair in do_not_repairs:
                                if need_repairs:
                                    if need_repairs.id == do_not_repair:
                                        flag_memory.need_repairs = True
                                        need_repairs = undefined
                                        flag_memory.need_stealers = 1
                    else:
                        flag_memory.need_repairs = False
                        flag_memory.need_stealers = 0
                controller = flag.room.controller
                reservation = 0
                if controller.reservation:
                    reservation = controller.reservation.ticksToEnd
                flag_memory.reservation = reservation
                if reservation < 2000:
                    flag_memory.need_reservators = 2
                else:
                    flag_memory.need_reservators = 1
                print('      ' + flag.name +
                      '  -  Stealers: ' +
                      str(flag_memory.stealers) + '/' + str(round(flag_memory.need_stealers, 3)) +
                      '.  Reservation: ' + reservation +
                      '.  Miners: ' +
                      str(flag_memory.miners) + '/' + str(round(flag_memory.need_miners, 3))
                      )
                flag.memory = flag_memory
            else:
                defenders = _.sum(flag.room.find(FIND_MY_CREEPS), lambda c: c.memory.job == 'defender')
                if len(defenders) < 1:
                    flag.pos.createFlag('A' + flag.name)
                    flag.remove()
        else:
            flag.memory.need_stealers = 3
    if flag.name[:1] == 'A':
        if flag.room:
            stealers = _.filter(flag.room.find(FIND_MY_CREEPS), lambda c: c.memory.job == 'stealer')
            if len(stealers) > 0:
                for stealer in stealers:
                    del stealer.memory.duty
                    del stealer.memory.target
                    del stealer.memory.flag
                    del stealer.memory.path
                    stealer.memory.job = 'worker'
            defenders = _.sum(flag.room.find(FIND_MY_CREEPS), lambda c: c.memory.job == 'defender')
            enemies = _.sum(flag.room.find(FIND_HOSTILE_CREEPS))
            if defenders >= 1 and enemies == 0:
                flag.pos.createFlag(flag.name[1:])
                flag.remove()
    if flag.name[:1] == 'o':
        spawn = Game.spawns['Spawn' + flag.name[1:2]]
        spawn.memory.need_offenders = int(flag.name[2:3])
    if flag.name[:2] == 'dc':
        define_deconstructions(flag)
    if flag.name[:5] == 'claim':
        Memory.claim = flag.name
    if flag.name == 'BS':
        need_spawn_builders = flag.memory.need_spawn_builders
        spawn_builders = flag.memory.spawn_builders
        sources = flag.room.find(FIND_SOURCES)
        flag.pos.createConstructionSite(STRUCTURE_SPAWN)
        for source in sources:
            if source.energy > source.ticksToRegeneration * 10 or source.energy >= 2900:
                if need_spawn_builders <= spawn_builders:
                    need_spawn_builders = need_spawn_builders + 0.01
            if source.energy / source.ticksToRegeneration < 8 or source.energy <= 0:
                if need_spawn_builders >= spawn_builders - 1:
                    need_spawn_builders = need_spawn_builders - 0.02
            flag.memory.need_spawn_builders = need_spawn_builders
        print(flag.name + ': spawn_builders - ' + spawn_builders + ' / ' + round(need_spawn_builders, 3))
        if flag.room.energyCapacityAvailable > 0:
            flag.remove()
            del Memory.building_spawn
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
