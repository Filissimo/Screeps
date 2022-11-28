from defs import *
from src import jobs, duties_and_targets

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def creep_mining(creep):
    if creep.store[RESOURCE_ENERGY] < creep.carryCapacity:
        creep.say('⛏')
        source = Game.getObjectById(creep.memory.target)
        if creep.pos.isNearTo(source):
            creep.memory.work_place = True
            result = creep.harvest(source)
            if result != OK:
                del creep.memory.target
                jobs.define_target(creep)
                print("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, 'mine', result))
        else:
            moving_by_path(creep, source)
            paving_roads(creep)
    else:
        jobs.define_target(creep)


def stealer_mining(creep):
    source = Game.getObjectById(creep.memory.target)
    if creep.store[RESOURCE_ENERGY] < creep.carryCapacity:
        creep.say('⛏')
        if creep.pos.isNearTo(source):
            creep.memory.work_place = True
            result = creep.harvest(source)
            if result == -6:
                jobs.define_target(creep)
            if result != OK and result != -6:
                print("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, 'mine', result))
            if result == -1:
                if creep.memory.flag:
                    flag = Game.flags[creep.memory.flag]
                    flag.memory.need_stealers = 0
                    jobs.define_target(creep)
        elif creep.pos.inRangeTo(source, 2):
            if creep.moveTo(source) == -2:
                duties_and_targets.decrease_stealers_needed(creep)
                jobs.define_target(creep)
        else:
            moving_by_path(creep, source)
            paving_roads(creep)
    else:
        jobs.define_target(creep)


def withdraw_from_closest(creep):
    if creep.store[RESOURCE_ENERGY] <= 0:
        creep.say('🛒')
        target = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER or
                               s.structureType == STRUCTURE_STORAGE) and
                              s.store[RESOURCE_ENERGY] > 0) \
            .sortBy(lambda s: (s.pos.getRangeTo(creep))).first()
        if target:
            is_close = creep.pos.isNearTo(target)
            if is_close:
                result = creep.withdraw(target, RESOURCE_ENERGY)
                if result != OK:
                    del creep.memory.target
                    jobs.define_target(creep)
                    print("[{}] Unknown result from creep.withdraw({}):"
                          " {}".format(creep.name, 'withdraw', result))
            else:
                moving_by_path(creep, target)
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def delivering_for_spawning(creep):
    if creep.store[RESOURCE_ENERGY] > 0:
        creep.say('🚼')
        target = Game.getObjectById(creep.memory.target)
        if target:
            if target.energy < target.energyCapacity:
                is_close = creep.pos.isNearTo(target)
                if is_close:
                    del creep.memory.target
                    jobs.define_target(creep)
                else:
                    moving_by_path(creep, target)
            else:
                jobs.define_target(creep)
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def accidentally_delivering_for_spawning(creep):
    if creep.store[RESOURCE_ENERGY] > 0:
        targets = _.filter((creep.pos.findInRange(FIND_STRUCTURES, 1)),
                           lambda s: (s.structureType == STRUCTURE_SPAWN or
                                      s.structureType == STRUCTURE_EXTENSION) and
                                     s.energy < s.energyCapacity)
        if targets:
            target_near = _(targets).filter(lambda t: creep.pos.isNearTo(t)).first()
            if target_near:
                result = creep.transfer(target_near, RESOURCE_ENERGY)
                if result != OK:
                    print("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                        creep.name, 'accidentally spawning', RESOURCE_ENERGY, result))
                jobs.define_target(creep)


def building(creep):
    move_away_from_source(creep)
    if creep.store[RESOURCE_ENERGY] > 0:
        creep.say('⚒')
        target = creep.pos.findClosestByRange(FIND_CONSTRUCTION_SITES)
        if target:
            is_close = creep.pos.inRangeTo(target, 3)
            if is_close:
                creep.memory.work_place = True
                result = creep.build(target)
                if result != OK:
                    del creep.memory.target
                    jobs.define_target(creep)
                    print("[{}] Unknown result from creep.build({}): {}".format(creep.name, 'build', result))
                if not creep.pos.isNearTo(target):
                    moving_by_path(creep, target)
            else:
                moving_by_path(creep, target)
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def upgrading(creep):
    if creep.store[RESOURCE_ENERGY] > 0:
        creep.say('🔬')
        target = Game.getObjectById(creep.memory.target)
        is_close = creep.pos.inRangeTo(target, 3)
        if is_close:
            result = creep.upgradeController(target)
            if result != OK and result != -6 and result != -9:
                # del creep.memory.target
                # jobs.define_target(creep)
                print("[{}] Unknown result from creep.upgradeController({}): {}".format(
                    creep.name, 'upgrade', result))
            if not creep.pos.inRangeTo(target, 1):
                creep.moveTo(target)
            else:
                creep.memory.work_place = True
        else:
            moving_by_path(creep, target)
    else:
        jobs.define_target(creep)


def miner_mines(creep):
    creep_memory = creep.memory
    source = Game.getObjectById(creep_memory.source)
    container = Game.getObjectById(creep_memory.container)
    if creep.pos.isNearTo(source) and creep.pos.isNearTo(container):
        if creep.store[RESOURCE_ENERGY] <= 44 and creep.memory.work_place:
            creep.say('⛏')
            source = Game.getObjectById(creep.memory.source)
            result = creep.harvest(source)
            if result != OK and result != -6:
                del creep.memory.target
                jobs.define_target(creep)
                print("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, 'mine', result))
            else:
                jobs.define_target(creep)
            container = Game.getObjectById(creep.memory.container)
            creep.transfer(container, RESOURCE_ENERGY)
        elif creep.store[RESOURCE_ENERGY] > 44 and creep.memory.work_place:
            creep.say('💼')
            container = Game.getObjectById(creep.memory.container)
            creep.transfer(container, RESOURCE_ENERGY)
    else:
        jobs.define_target(creep)


def recalculate_miners_path(creep):
    creep_memory = creep.memory
    source = Game.getObjectById(creep_memory.source)
    container = Game.getObjectById(creep_memory.container)
    creep.say('?')
    place1 = source.pos
    place2 = container.pos
    if source.pos.x - container.pos.x == 2:
        place1.x = place1.x - 1
        place2.x = place2.x + 1
        if place1.y == place2.y:
            place2.y = place2.y + 1
            if place2.lookFor(LOOK_TERRAIN).type == 'wall':
                place2.y = place2.y - 2
    elif source.pos.x - container.pos.x == - 2:
        place1.x = place1.x + 1
        place2.x = place2.x - 1
        if place1.y == place2.y:
            place2.y = place2.y + 1
            if place2.lookFor(LOOK_TERRAIN).type == 'wall':
                place2.y = place2.y - 2
    elif source.pos.y - container.pos.y == 2:
        place1.y = place1.y - 1
        place2.y = place2.y + 1
        if place1.x == place2.x:
            place2.x = place2.x + 1
            if place2.lookFor(LOOK_TERRAIN).type == 'wall':
                place2.x = place2.x - 2
    elif source.pos.y - container.pos.y == - 2:
        place1.y = place1.y + 1
        place2.y = place2.y - 1
        if place1.x == place2.x:
            place2.x = place2.x + 1
            if place2.lookFor(LOOK_TERRAIN).type == 'wall':
                place2.x = place2.x - 2

    print(str(place1) + '  ' + str(place2))

    miner = _.sum(place1.lookFor(LOOK_CREEPS), lambda c: c.memory.job == 'miner')
    if miner == 0:
        creeps_close = creep.pos.findInRange(FIND_MY_CREEPS, 1)
        busy_creep = _(creeps_close).filter(lambda c: c.memory.work_place is True).sample()
        not_my_creep_close = _(creep.pos.findInRange(FIND_HOSTILE_CREEPS, 1)).sample()
        if busy_creep or not_my_creep_close:
            if creep.memory.path:
                del creep.memory.path
            creep.moveTo(place1)
        else:
            path = creep.pos.findPathTo(place1, {'ignoreCreeps': True})
            if len(path):
                creep.memory.path = path
                creep.moveByPath(path)
    else:
        creeps_close = creep.pos.findInRange(FIND_MY_CREEPS, 1)
        busy_creep = _(creeps_close).filter(lambda c: c.memory.work_place is True).sample()
        not_my_creep_close = _(creep.pos.findInRange(FIND_HOSTILE_CREEPS, 1)).sample()
        if busy_creep or not_my_creep_close:
            if creep.memory.path:
                del creep.memory.path
            creep.moveTo(place2)
        else:
            path = creep.pos.findPathTo(place2, {'ignoreCreeps': True})
            if len(path):
                creep.memory.path = path
                creep.moveByPath(path)

    creep.memory = creep_memory


def going_to_workplace(creep):
    creep_memory = creep.memory
    source = Game.getObjectById(creep_memory.source)
    container = Game.getObjectById(creep_memory.container)
    if creep.pos.isNearTo(source) and creep.pos.isNearTo(container):
        creep_memory.work_place = True
        jobs.define_target(creep)
    else:
        creeps_close = creep.pos.findInRange(FIND_MY_CREEPS, 1)
        busy_creep = _(creeps_close).filter(lambda c: c.memory.work_place is True).sample()
        not_my_creep_close = _(creep.pos.findInRange(FIND_HOSTILE_CREEPS, 1)).sample()
        if busy_creep or not_my_creep_close:
            recalculate_miners_path(creep)
        else:
            creep_memory.work_place = False
            path = creep_memory.path
            if len(path):
                creep.say('🔍')
                result = creep.moveByPath(path)
                print(result + '  ' + creep.name)
                if result == -5:
                    del creep_memory.path
            else:
                recalculate_miners_path(creep)
    creep.memory = creep_memory


def paving_roads(creep):
    if not Memory.roads:
        Memory.roads = []
    real_coors_str = str(creep.pos)
    roads_memory = Memory.roads
    road_coors_new_object = {real_coors_str: 100}
    new_counter = undefined
    on_road = _(creep.pos.lookFor(LOOK_STRUCTURES)) \
        .filter(lambda s: (s.structureType == STRUCTURE_ROAD or
                           s.structureType == STRUCTURE_SPAWN)).sample()
    if on_road:
        for road_memory in roads_memory:
            str_road_memory = str(road_memory)
            str_road_coors = '{\'' + real_coors_str + '\': ' + str(road_memory[real_coors_str]) + '}'
            if str_road_memory == str_road_coors:
                roads_memory.remove(road_memory)
    else:
        for road_memory in roads_memory:
            str_road_memory = str(road_memory)
            str_road_coors = '{\'' + real_coors_str + '\': ' + str(road_memory[real_coors_str]) + '}'
            if str_road_memory == str_road_coors:
                new_counter = road_memory[real_coors_str] + 70
                roads_memory.remove(road_memory)
        if str(roads_memory) == '[]':
            roads_memory.append(road_coors_new_object)
        else:
            if new_counter:
                if new_counter >= 2000:
                    construction_sites = _.sum(creep.room.find(FIND_CONSTRUCTION_SITES),
                                               lambda cs: cs.progress < cs.progressTotal)
                    if construction_sites <= 4:
                        result = creep.pos.createConstructionSite(STRUCTURE_ROAD)
                        if result != OK:
                            print(creep + ': no road, on construction site ' + creep.pos +
                                  ', construction sites: ' + construction_sites)
                        else:
                            print(creep + ': no road, paving ' + creep.pos +
                                  ', construction sites: ' + str(construction_sites))
                    else:
                        print(creep + ': no road ' + creep.pos +
                              ', but there are too many construction sites: ' + construction_sites)
                else:
                    road_increased_counter = {real_coors_str: new_counter}
                    roads_memory.append(road_increased_counter)
            else:
                roads_memory.append(road_coors_new_object)
    Memory.roads = roads_memory


def dismantling(creep):
    if creep.store[RESOURCE_ENERGY] < creep.store.getCapacity():
        target = Game.getObjectById(creep.memory.target)
        if target:
            creep.say('💣')
            is_close = creep.pos.isNearTo(target)
            if is_close:
                creep.memory.work_place = True
                result = creep.dismantle(target)
                if result != OK:
                    del creep.memory.target
                    jobs.define_target(creep)
                    print("[{}] Unknown result from creep.dismantle({}): {}"
                          .format(creep.name, 'dismantle', result))
            else:
                result = moving_by_path(creep, target)
                if result != OK:
                    jobs.define_target(creep)
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def move_away_from_source(creep):
    move_away_bool = False
    source = creep.pos.findClosestByRange(FIND_SOURCES)
    if source:
        if source.id != creep.memory.target:
            if creep.pos.inRangeTo(source, 1):
                creep.say('🔜')
                flee_condition = _.map(creep.room.find(FIND_SOURCES), lambda c: {'pos': c.pos, 'range': 3})
                flee_path = PathFinder.search(
                    creep.pos,
                    flee_condition,
                    {'flee': True}
                ).path
                creep.moveByPath(flee_path)
                move_away_bool = True
    return move_away_bool


def not_fleeing(creep):
    not_fleeing_bool = True
    enemy = creep.pos.findClosestByRange(FIND_HOSTILE_CREEPS, {'filter': lambda e: e.owner.username != 'rep71Le'})
    if enemy:
        if creep.pos.inRangeTo(enemy, 7):
            creep.say('🏳️')
            flee_condition = _.map(creep.room.find(FIND_HOSTILE_CREEPS), lambda c: {'pos': c.pos, 'range': 9})
            flee_path = PathFinder.search(
                creep.pos,
                flee_condition,
                {'flee': True}
            ).path
            creep.moveByPath(flee_path)
            not_fleeing_bool = False
    return not_fleeing_bool


def creep_repairing(creep):
    move_away_from_source(creep)
    if creep.store[RESOURCE_ENERGY] > 0:
        creep.say('🔧')
        target = Game.getObjectById(creep.memory.target)
        print('repairing ' + str(target.pos))
        if target.hits > target.hitsMax * 0.8:
            del creep.memory.path
            target = _(creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: (s.hits < s.hitsMax * 0.8) and
                                  s.structureType != STRUCTURE_WALL) \
                .sortBy(lambda s: (s.pos.getRangeTo(target))).first()
            if target:
                creep.memory.target = target.id
            else:
                jobs.define_target(creep)
        if target:
            is_close = creep.pos.inRangeTo(target, 3)
            if is_close:
                result = creep.repair(target)
                if result != OK:
                    del creep.memory.target
                    jobs.define_target(creep)
                    print("[{}] Unknown result from creep.build({}): {}".format(creep.name, 'build', result))
                if not creep.pos.inRangeTo(target, 1):
                    moving_by_path(creep, target)
                else:
                    creep.memory.work_place = True
            else:
                moving_by_path(creep, target)
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def pick_up_tombstone(creep):
    target = Game.getObjectById(creep.memory.target)
    print(str(target) + ' ' + creep.name)
    if target:
        if target.store[RESOURCE_ENERGY] > 0:
            creep.say('⚰')
            if creep.pos.isNearTo(target):
                result = creep.withdraw(target, RESOURCE_ENERGY)
                print(creep.name + ' picking up ' + result)
                if result == OK or result == -6:
                    del creep.memory.target
                    jobs.define_target(creep)
                if result == -8:
                    del creep.memory.target
                    jobs.define_target(creep)
            else:
                moving_by_path(creep, target)
                print(creep.name + ' moving to pick up')
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def withdrawing_from_memory(creep):
    if creep.store[RESOURCE_ENERGY] <= 0:
        creep.say('🚚')
        target = Game.getObjectById(creep.memory.target)
        if target:
            is_close = creep.pos.isNearTo(target)
            if is_close:
                result = creep.withdraw(target, RESOURCE_ENERGY)
                if result != OK:
                    del creep.memory.target
                    jobs.define_target(creep)
                    print("[{}] Unknown result from creep.withdraw({}):"
                          " {}".format(creep.name, 'withdraw', result))
            else:
                moving_by_path(creep, target)
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def delivering_to_from_memory(creep):
    if creep.store[RESOURCE_ENERGY] > 0:
        creep.say('🚛')
        target = Game.getObjectById(creep.memory.target)
        if target:
            is_close = creep.pos.isNearTo(target)
            if is_close:
                creep.memory.work_place = True
                result = creep.transfer(target, RESOURCE_ENERGY)
                if result == OK or result == ERR_FULL:
                    del creep.memory.target
                    jobs.define_target(creep)
                else:
                    del creep.memory.target
                    jobs.define_target(creep)
                    print("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                        creep.name, 'store', RESOURCE_ENERGY, result))
            else:
                moving_by_path(creep, target)
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def attacking(creep):
    enemy = creep.pos.findClosestByRange(FIND_HOSTILE_CREEPS, {'filter': lambda e: e.owner.username != 'rep71Le'})
    if enemy:
        creep.say('⚔')
        if creep.pos.inRangeTo(enemy, 3):
            creep.rangedAttack(enemy)
            if 4 < creep.pos.x < 45 and 4 < creep.pos.y < 45:
                flee_condition = _.map(creep.room.find(FIND_HOSTILE_CREEPS), lambda c: {'pos': c.pos, 'range': 5})
                flee_path = PathFinder.search(
                    creep.pos,
                    flee_condition,
                    {'flee': True}
                ).path
                creep.moveByPath(flee_path)
        else:
            moving_by_path(creep, enemy)
    else:
        jobs.define_target(creep)


def move_away_from_creeps(creep):
    result = False
    creep_to_flee = _(creep.room.find(FIND_MY_CREEPS)) \
        .filter(lambda c: c.id != creep.id and c.id != creep.memory.healer) \
        .sortBy(lambda c: c.pos.getRangeTo(creep)).first()
    if creep_to_flee:
        if creep.pos.inRangeTo(creep_to_flee, 2):
            creep.say('👣')
            all_creeps_except_me = _.filter(creep.room.find(FIND_MY_CREEPS), lambda c: (c.id != creep.id))
            flee_condition = _.map(all_creeps_except_me, lambda c: {'pos': c.pos, 'range': 3})
            flee_path = PathFinder.search(
                creep.pos,
                flee_condition,
                {'flee': True}
            ).path
            creep.moveByPath(flee_path)
            result = True
    return result


def defending(creep):
    message = 'Боря - пупырчатый и безмозглый дуропьян, которому лень выкаблучиваться!'
    all_line = '          ' + message + '                '
    start_point = creep.memory.start_point
    current_message = all_line[start_point:(start_point + 10)]
    step = 3
    if start_point < len(all_line) - 10 - step:
        creep.memory.start_point = start_point + step
    else:
        creep.memory.start_point = 0
    creep.say(current_message, {'public': True})
    # creep.say('🛡️')
    jobs.define_target(creep)


def going_to_flag(creep):
    creep.say('🏁')
    flag = Game.flags[creep.memory.flag]
    moving_by_path(creep, flag)
    if flag:
        if creep.pos.inRangeTo(flag, 40):
            jobs.define_target(creep)


def not_going_to_flag(creep):
    going_to_flag_bool = False
    creep.say('🏁')
    flag = Game.flags[creep.memory.flag]
    moving_by_path(creep, flag)
    if flag:
        if creep.pos.inRangeTo(flag, 40):
            del creep.memory.path
            going_to_flag_bool = True
    return going_to_flag_bool


def reserving(creep):
    controller = Game.getObjectById(creep.memory.controller)
    if creep.pos.isNearTo(controller):
        creep.memory.work_place = True
        if creep.reserveController(controller) != OK:
            if creep.attackController(controller) == -11:
                creep.say('W')
            else:
                creep.say('A')
        else:
            creep.say('R')
    else:
        moving_by_path(creep, controller)
        creep.say('📍')
        paving_roads(creep)


def going_home(creep):
    going_home_bool = False
    home = Game.getObjectById(creep.memory.home)
    if creep.room != home.room:
        if (creep.store[RESOURCE_ENERGY] > 0 and creep.memory.job == 'stealer') \
                or creep.memory.job == 'worker' or \
                creep.memory.job == 'starter' or \
                creep.memory.job == 'lorry' or \
                creep.memory.job == 'stealorry':
            creep.say('🏡')
            moving_by_path(creep, home)
            going_home_bool = True
            creep.memory.work_place = False
    return going_home_bool


def transferring_to_closest(creep):
    if creep.store[RESOURCE_ENERGY] > 0:
        creep.say('🧰')
        target = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER or
                               s.structureType == STRUCTURE_STORAGE)) \
            .sortBy(lambda s: (s.pos.getRangeTo(creep))).first()
        if target:
            is_close = creep.pos.isNearTo(target)
            if is_close:
                creep.memory.work_place = True
                result = creep.transfer(target, RESOURCE_ENERGY)
                if result == -8:
                    return result
                elif result != OK:
                    del creep.memory.target
                    jobs.define_target(creep)
                    print("[{}] Unknown result from creep.transfer({}):"
                          " {}".format(creep.name, 'transfer', result))
            else:
                moving_by_path(creep, target)
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def going_to_help(creep):
    creep.say('🗡️')
    flag_to_defend = Game.flags[creep.memory.flag]
    if flag_to_defend:
        moving_by_path(creep, flag_to_defend)
        if creep.pos.inRangeTo(flag_to_defend, 40):
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def claiming(creep):
    controller = Game.getObjectById(creep.memory.controller)
    if controller:
        result = creep.claimController(controller)
        if result == ERR_NOT_IN_RANGE:
            moving_by_path(creep, controller)
            creep.say('MY')
        else:
            flag = Game.flags[Memory.claim]
            if flag:
                flag.pos.createConstructionSite(STRUCTURE_SPAWN)
                Memory.building_spawn = flag.name


def not_going_to_bs(creep):
    not_going_to_bs_bool = True
    flag = Game.flags['BS']
    if flag:
        if creep.room != flag.room:
            moving_by_path(creep, flag)
            creep.say('BS')
            not_going_to_bs_bool = False
    return not_going_to_bs_bool


def moving_by_path(creep, target):
    result = undefined
    if not creep.spawning:
        if creep.pos.inRangeTo(target, 3):
            result = creep.moveTo(target)
            if creep.memory.path:
                del creep.memory.path
        else:
            creeps_close = creep.pos.findInRange(FIND_MY_CREEPS, 2)
            busy_creep = _(creeps_close).filter(lambda c: c.memory.work_place is True).sample()
            not_my_creep_close = _(creep.pos.findInRange(FIND_HOSTILE_CREEPS, 1)).sample()
            if busy_creep or not_my_creep_close:
                result = creep.moveTo(target)
                if creep.memory.path:
                    del creep.memory.path
            else:
                path = creep.memory.path
                if len(path):
                    result = creep.moveByPath(path)
                if not len(path):
                    path = creep.pos.findPathTo(target, {'ignoreCreeps': True})
                    if len(path):
                        creep.memory.path = path
                        result = creep.moveByPath(path)
                if result == -5:
                    del creep.memory.path
                if result != OK and result != -11:
                    print(creep.name + ': ' + result + '   not moving!')

    return result


def accidentally_delivering_to_worker(creep):
    if creep.store[RESOURCE_ENERGY] > 0:
        targets = creep.pos.findInRange(FIND_MY_CREEPS, 1)
        if targets:
            target_empty_worker = _(targets).filter(lambda t: (t.memory.job == 'worker') and
                                                              t.store[RESOURCE_ENERGY] < t.store.getCapacity()).sample()
            if target_empty_worker:
                result = creep.transfer(target_empty_worker, RESOURCE_ENERGY)
                if result != OK:
                    print("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                        creep.name, 'accidentally to worker', RESOURCE_ENERGY, result))
                jobs.define_target(creep)


def accidentally_delivering_to_lorry(creep):
    if creep.store[RESOURCE_ENERGY] > 0:
        targets = creep.pos.findInRange(FIND_MY_CREEPS, 1)
        if targets:
            target_empty_lorry = _(targets) \
                .filter(lambda t: t.memory.job == 'lorry' and
                                  t.store[RESOURCE_ENERGY] < t.store.getCapacity()).first()
            if target_empty_lorry:
                result = creep.transfer(target_empty_lorry, RESOURCE_ENERGY)
                if result != OK:
                    print("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                        creep.name, 'accidentally to lorry', RESOURCE_ENERGY, result))
                    if creep.memory.path:
                        del creep.memory.path


def accidentally_delivering_to_stealorry(creep):
    if creep.store[RESOURCE_ENERGY] > 0:
        targets = creep.pos.findInRange(FIND_MY_CREEPS, 1)
        if targets:
            target_empty_lorry = _(targets) \
                .filter(lambda t: t.memory.job == 'stealorry' and
                                  t.store[RESOURCE_ENERGY] < t.store.getCapacity()).first()
            if target_empty_lorry:
                result = creep.transfer(target_empty_lorry, RESOURCE_ENERGY)
                if result != OK:
                    print("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                        creep.name, 'accidentally to lorry', RESOURCE_ENERGY, result))
                    if creep.memory.path:
                        del creep.memory.path


def helping_stealers(creep):
    if Game.getObjectById(creep.memory.home).room != creep.room:
        target = Game.getObjectById(creep.memory.target)
        if creep.store[RESOURCE_ENERGY] < creep.store.getCapacity():
            if target:
                target.memory.has_lorry = creep.id
                if creep.pos.isNearTo(target):
                    creep.say('😄')
                    creep.memory.work_place = True
                else:
                    creep.say('💰')
                    creep.memory.work_place = False
                    moving_by_path(creep, target)
                    paving_roads(creep)
                if (target.memory.duty == 'repairing' or target.memory.duty == 'building') \
                        and creep.store[RESOURCE_ENERGY] > 0:
                    creep.transfer(target, RESOURCE_ENERGY)
            else:
                jobs.define_target(creep)
        else:
            if target:
                if target.memory.repairing or target.memory.building:
                    if target:
                        target.memory.has_lorry = creep.id
                        if creep.pos.isNearTo(target):
                            creep.say('😆')
                            creep.memory.work_place = True
                        else:
                            creep.say('🎒')
                            creep.memory.work_place = False
                            moving_by_path(creep, target)
                        if target.memory.duty == 'repairing' or target.memory.duty == 'building':
                            creep.transfer(target, RESOURCE_ENERGY)
                    else:
                        jobs.define_target(creep)
                else:
                    if target:
                        del target.memory.has_lorry
                    jobs.define_target(creep)
            else:
                if target:
                    del target.memory.has_lorry
                jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def helping_workers(creep):
    if creep.store[RESOURCE_ENERGY] > 0:
        target = Game.getObjectById(creep.memory.target)
        if target:
            target.memory.has_lorry = creep.id
            if creep.pos.isNearTo(target):
                creep.say('😆')
                creep.memory.work_place = True
            else:
                creep.say('🎒')
                creep.memory.work_place = False
                moving_by_path(creep, target)
            creep.transfer(target, RESOURCE_ENERGY)
            # if creep.store[RESOURCE_ENERGY] < 100:
            container = _(creep.pos.findInRange(FIND_STRUCTURES, 1)) \
                .filter(lambda s: s.structureType == STRUCTURE_CONTAINER or
                                  s.structureType == STRUCTURE_STORAGE).sample()
            if container:
                creep.withdraw(container, RESOURCE_ENERGY)
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def pick_up_energy(creep):
    energy_near = creep.pos.findInRange(FIND_DROPPED_RESOURCES, 1)[0]
    if energy_near:
        creep.pickup(energy_near)


def nursing(creep):
    target = Game.getObjectById(creep.memory.target)
    if target:
        if not target.memory.healer:
            if creep.hits < creep.hitsMax / 4:
                target.memory.healer = creep.id
        if creep.pos.isNearTo(target):
            creep.memory.work_place = True
        else:
            creep.memory.work_place = False
            enemy = creep.pos.findClosestByRange(FIND_HOSTILE_CREEPS,
                                                 {'filter': lambda e: e.owner.username != 'rep71Le'})
            if enemy:
                if creep.pos.inRangeTo(enemy, 5):
                    creep.rangedAttack(enemy)
                    if 4 < creep.pos.x < 45 and 4 < creep.pos.y < 45:
                        flee_condition = _.map(creep.room.find(FIND_HOSTILE_CREEPS),
                                               lambda c: {'pos': c.pos, 'range': 7})
                        flee_path = PathFinder.search(
                            creep.pos,
                            flee_condition,
                            {'flee': True}
                        ).path
                        creep.moveByPath(flee_path)
                else:
                    moving_by_path(creep, target)
        patient = _(creep.pos.findInRange(FIND_MY_CREEPS, 3))\
            .filter(lambda c: c.hits < c.hitsMax)\
            .sortBy(lambda c: c.hitsMax / c.hits).first()
        if patient:
            if creep.pos.isNearTo(patient):
                creep.heal(patient)
            else:
                creep.rangedHeal(patient)
        else:
            creep.heal(creep)
    else:
        jobs.define_target(creep)
