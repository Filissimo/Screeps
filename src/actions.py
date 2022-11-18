from defs import *
from src import jobs

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def creep_mining(creep):
    if _.sum(creep.carry) < creep.carryCapacity:
        creep.say('⛏')
        source = Game.getObjectById(creep.memory.target)
        if creep.pos.isNearTo(source):
            result = creep.harvest(source)
            if result != OK:
                del creep.memory.target
                jobs.define_target(creep)
                print("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, 'mine', result))
        else:
            result = creep.moveTo(source, {'visualizePathStyle': {
                'fill': 'transparent',
                'stroke': '#fff',
                'lineStyle': 'dashed',
                'strokeWidth': .15,
                'opacity': .1
            }, range: 0})
            if result == -2:
                jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def withdraw_from_closest(creep):
    if _.sum(creep.carry) <= 0:
        creep.say('🛒')
        target = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER or
                               s.structureType == STRUCTURE_STORAGE) and
                              s.store[RESOURCE_ENERGY] >= creep.carryCapacity) \
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
                creep.moveTo(target, {'visualizePathStyle': {
                    'fill': 'transparent',
                    'stroke': '#fff',
                    'lineStyle': 'dashed',
                    'strokeWidth': .15,
                    'opacity': .1
                }, range: 0})
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def delivering_for_spawning(creep):
    if _.sum(creep.carry) > 0:
        creep.say('🚼')
        target = Game.getObjectById(creep.memory.target)
        if target:
            is_close = creep.pos.isNearTo(target)
            if is_close:
                del creep.memory.target
                jobs.define_target(creep)
            else:
                creep.moveTo(target, {'visualizePathStyle': {
                    'fill': 'transparent',
                    'stroke': '#fff',
                    'lineStyle': 'dashed',
                    'strokeWidth': .15,
                    'opacity': .1
                }, range: 0})
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def accidentally_delivering_for_spawning(creep):
    if creep.store[RESOURCE_ENERGY] > 0:
        targets = _.filter((creep.room.find(FIND_STRUCTURES)),
                           lambda s: ((s.structureType == STRUCTURE_SPAWN or
                                       s.structureType == STRUCTURE_EXTENSION) and
                                      s.energy < s.energyCapacity))
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
    if _.sum(creep.carry) > 0:
        creep.say('⚒')
        target = creep.pos.findClosestByRange(FIND_CONSTRUCTION_SITES)
        if target:
            is_close = creep.pos.inRangeTo(target, 3)
            if is_close:
                result = creep.build(target)
                if result != OK:
                    del creep.memory.target
                    jobs.define_target(creep)
                    print("[{}] Unknown result from creep.build({}): {}".format(creep.name, 'build', result))
                if not creep.pos.isNearTo(target):
                    creep.moveTo(target, {'visualizePathStyle': {
                        'fill': 'transparent',
                        'stroke': '#fff',
                        'lineStyle': 'dashed',
                        'strokeWidth': .15,
                        'opacity': .1
                    }, range: 0})
            else:
                creep.moveTo(target, {'visualizePathStyle': {
                    'fill': 'transparent',
                    'stroke': '#fff',
                    'lineStyle': 'dashed',
                    'strokeWidth': .15,
                    'opacity': .1
                }, range: 0})
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def upgrading(creep):
    if _.sum(creep.carry) > 0:
        creep.say('🔬')
        target = Game.getObjectById(creep.memory.target)
        is_close = creep.pos.inRangeTo(target, 3)
        if is_close:
            result = creep.upgradeController(target)
            if result != OK:
                del creep.memory.target
                jobs.define_target(creep)
                print("[{}] Unknown result from creep.upgradeController({}): {}".format(
                    creep.name, 'upgrade', result))
            if not creep.pos.inRangeTo(target, 1):
                creep.moveTo(target, {'visualizePathStyle': {
                    'fill': 'transparent',
                    'stroke': '#fff',
                    'lineStyle': 'dashed',
                    'strokeWidth': .15,
                    'opacity': .1
                }, range: 0})
        else:
            creep.moveTo(target, {'visualizePathStyle': {
                'fill': 'transparent',
                'stroke': '#fff',
                'lineStyle': 'dashed',
                'strokeWidth': .15,
                'opacity': .1
            }, range: 0})
    else:
        jobs.define_target(creep)


def miner_mines(creep):
    if _.sum(creep.carry) <= 42:
        creep.say('⛏')
        source = Game.getObjectById(creep.memory.source)
        if creep.pos.isNearTo(source):
            result = creep.harvest(source)
            if result != OK and result != -6:
                del creep.memory.target
                jobs.define_target(creep)
                print("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, 'mine', result))
        else:
            result = creep.moveTo(source, {'visualizePathStyle': {
                'fill': 'transparent',
                'stroke': '#fff',
                'lineStyle': 'dashed',
                'strokeWidth': .15,
                'opacity': .1
            }, range: 0})
            if result == -2:
                jobs.define_target(creep)
    elif _.sum(creep.carry) > 42:
        jobs.define_target(creep)


def miner_delivers(creep):
    if _.sum(creep.carry) > 0:
        creep.say('🧱')
        target = Game.getObjectById(creep.memory.container)
        if target:
            is_close = creep.pos.isNearTo(target)
            if is_close:
                result = creep.transfer(target, RESOURCE_ENERGY)
                if result == OK:
                    del creep.memory.target
                    jobs.define_target(creep)
                elif result == ERR_FULL:
                    print(creep.name + " - container is full!")
                    home = Game.getObjectById(creep.memory.home)
                    need_additional_lorries = home.memory.need_additional_lorries
                    need_additional_lorries = round((need_additional_lorries + 0.01), 2)
                    home.memory.need_additional_lorries = need_additional_lorries
                else:
                    del creep.memory.target
                    jobs.define_target(creep)
                    print("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                        creep.name, 'store', RESOURCE_ENERGY, result))
            else:
                creep.moveTo(target, {'visualizePathStyle': {
                    'fill': 'transparent',
                    'stroke': '#fff',
                    'lineStyle': 'dashed',
                    'strokeWidth': .15,
                    'opacity': .1
                }, range: 0})
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def paving_roads(creep):
    if not Memory.roads:
        Memory.roads = []
    real_coors_str = str(creep.pos)
    roads_memory = Memory.roads
    road_coors_new_object = {real_coors_str: 20}
    new_counter = undefined
    if_on_road = _(creep.pos.lookFor(LOOK_STRUCTURES)) \
        .filter(lambda s: (s.structureType == STRUCTURE_ROAD or
                           s.structureType == STRUCTURE_SPAWN)).sample()
    if not if_on_road:
        for road_memory in roads_memory:
            str_road_memory = str(road_memory)
            str_road_coors = '{\'' + real_coors_str + '\': ' + str(road_memory[real_coors_str]) + '}'
            if str_road_memory == str_road_coors:
                new_counter = road_memory[real_coors_str] + 13
                roads_memory.remove(road_memory)
        if str(roads_memory) == '[]':
            roads_memory.append(road_coors_new_object)
        else:
            if new_counter:
                if new_counter >= 2000:
                    construction_sites = _.sum(creep.room.find(FIND_CONSTRUCTION_SITES),
                                               lambda cs: cs.progress < cs.progressTotal)
                    if construction_sites <= 3:
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
                result = creep.dismantle(target)
                if result != OK:
                    del creep.memory.target
                    jobs.define_target(creep)
                    print("[{}] Unknown result from creep.dismantle({}): {}"
                          .format(creep.name, 'dismantle', result))
            else:
                result = creep.moveTo(target, {'visualizePathStyle': {
                    'fill': 'transparent',
                    'stroke': '#fff',
                    'lineStyle': 'dashed',
                    'strokeWidth': .15,
                    'opacity': .1
                }, range: 0})
                if result != OK:
                    jobs.define_target(creep)
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def move_away_from_source(creep):
    source = creep.pos.findClosestByRange(FIND_SOURCES)
    if source:
        if creep.pos.inRangeTo(source, 1):
            creep.say('🔜')
            flee_condition = _.map(creep.room.find(FIND_SOURCES), lambda c: {'pos': c.pos, 'range': 3})
            flee_path = PathFinder.search(
                creep.pos,
                flee_condition,
                {'flee': True}
            ).path
            creep.moveByPath(flee_path)


def not_fleeing(creep):
    not_fleeing_bool = True
    enemy = creep.pos.findClosestByRange(FIND_HOSTILE_CREEPS)
    if enemy:
        if creep.pos.inRangeTo(enemy, 5):
            creep.say('🏳️')
            flee_condition = _.map(creep.room.find(FIND_HOSTILE_CREEPS), lambda c: {'pos': c.pos, 'range': 7})
            flee_path = PathFinder.search(
                creep.pos,
                flee_condition,
                {'flee': True}
            ).path
            creep.moveByPath(flee_path)
            not_fleeing_bool = False
            my_creeps = _.filter(Game.creeps, lambda c: c.memory != undefined)
            my_creeps_with_memory = _.filter(my_creeps, lambda c: c.memory.job != undefined)
            creeps_filtered = _.filter(my_creeps_with_memory,
                                       lambda c: c.memory.home == creep.memory.home and c.memory.job == 'defender' and
                                                 c.ticksToLive > 50)

            for defender in creeps_filtered:
                if defender.memory.duty == 'defending' and defender.memory.fleeing_creep is None:
                    defender.memory.fleeing_creep = creep.id
                    defender.memory.duty = 'going_to_help'
    return not_fleeing_bool


def creep_repairing(creep):
    move_away_from_source(creep)
    if _.sum(creep.carry) > 0:
        creep.say('🔧')
        target = Game.getObjectById(creep.memory.target)
        if target.hits > target.hitsMax * 0.8:
            target = _(creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: (s.hits < s.hitsMax * 0.8)) \
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
                    creep.moveTo(target, {'visualizePathStyle': {
                        'fill': 'transparent',
                        'stroke': '#fff',
                        'lineStyle': 'dashed',
                        'strokeWidth': .15,
                        'opacity': .1
                    }, range: 0})
            else:
                creep.moveTo(target, {'visualizePathStyle': {
                    'fill': 'transparent',
                    'stroke': '#fff',
                    'lineStyle': 'dashed',
                    'strokeWidth': .15,
                    'opacity': .1
                }, range: 0})
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def pick_up_tombstone(creep):
    target = Game.getObjectById(creep.memory.target)
    print(str(target) + ' ' + creep.name)
    if target:
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
            creep.moveTo(target, {'visualizePathStyle': {
                'fill': 'transparent',
                'stroke': '#fff',
                'lineStyle': 'dashed',
                'strokeWidth': .15,
                'opacity': .1
            }, range: 0})
            print(creep.name + ' moving to pick up')
    else:
        jobs.define_target(creep)


def withdrawing_from_memory(creep):
    if _.sum(creep.carry) <= 0:
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
                creep.moveTo(target, {'visualizePathStyle': {
                    'fill': 'transparent',
                    'stroke': '#fff',
                    'lineStyle': 'dashed',
                    'strokeWidth': .15,
                    'opacity': .1
                }, range: 0})
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def delivering_to_from_memory(creep):
    if _.sum(creep.carry) > 0:
        creep.say('🚛')
        target = Game.getObjectById(creep.memory.target)
        if target:
            is_close = creep.pos.isNearTo(target)
            if is_close:
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
                creep.moveTo(target, {'visualizePathStyle': {
                    'fill': 'transparent',
                    'stroke': '#fff',
                    'lineStyle': 'dashed',
                    'strokeWidth': .15,
                    'opacity': .1
                }, range: 0})
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def attacking(creep):
    enemy = creep.pos.findClosestByRange(FIND_HOSTILE_CREEPS)
    if enemy:
        creep.say('⚔')
        if creep.pos.inRangeTo(enemy, 4):
            creep.rangedAttack(enemy)
            flee_condition = _.map(creep.room.find(FIND_HOSTILE_CREEPS), lambda c: {'pos': c.pos, 'range': 7})
            flee_path = PathFinder.search(
                creep.pos,
                flee_condition,
                {'flee': True}
            ).path
            creep.moveByPath(flee_path)
        else:
            creep.moveTo(enemy, {'visualizePathStyle': {
                'fill': 'transparent',
                'stroke': '#fff',
                'lineStyle': 'dashed',
                'strokeWidth': .15,
                'opacity': .1
            }, range: 0})
    else:
        jobs.define_target(creep)


def move_away_from_creeps(creep):
    result = False
    creep_to_flee = _(creep.room.find(FIND_MY_CREEPS)) \
        .filter(lambda c: (c.id != creep.id)) \
        .sortBy(lambda c: c.pos.getRangeTo(creep)).first()
    if creep_to_flee:
        if creep.pos.inRangeTo(creep_to_flee, 3):
            creep.say('🚶')
            all_creeps_except_me = _.filter(creep.room.find(FIND_MY_CREEPS), lambda c: (c.id != creep.id))
            flee_condition = _.map(all_creeps_except_me, lambda c: {'pos': c.pos, 'range': 5})
            flee_path = PathFinder.search(
                creep.pos,
                flee_condition,
                {'flee': True}
            ).path
            creep.moveByPath(flee_path)
            result = True
    return result


def defending(creep):
    creep.say('🛡️')
    jobs.define_target(creep)


def going_to_flag(creep):
    creep.say('🏁')
    flag = Game.flags[creep.memory.flag]
    creep.moveTo(flag, {'visualizePathStyle': {
        'fill': 'transparent',
        'stroke': '#fff',
        'lineStyle': 'dashed',
        'strokeWidth': .15,
        'opacity': .1
    }, range: 0})
    if creep.pos.inRangeTo(flag, 40):
        jobs.define_target(creep)


def reserving(creep):
    controller = Game.getObjectById(creep.memory.controller)
    if creep.reserveController(controller) != OK:
        creep.moveTo(controller, {'visualizePathStyle': {
            'fill': 'transparent',
            'stroke': '#fff',
            'lineStyle': 'dashed',
            'strokeWidth': .15,
            'opacity': .1
        }, range: 0})
    if controller:
        creep.say('📍')
        if controller.reservation:
            if controller.reservation.ticksToEnd > 10:
                home = Game.getObjectById(creep.memory.home)
                if creep.name[10:11] == 1:
                    if not home.memory.need_stealer1s:
                        home.memory.need_stealer1s = 1
                if creep.name[10:11] == 2:
                    if not home.memory.need_stealer2s:
                        home.memory.need_stealer2s = 1


def going_home(creep):
    going_home_bool = False
    home = Game.getObjectById(creep.memory.home)
    if creep.room != home.room:
        if (_.sum(creep.carry) > 0 and creep.memory.job[:7] == 'stealer')\
                or (_.sum(creep.carry) == 0 and creep.memory.job == 'worker'):
            creep.say('🏡')
            creep.moveTo(home, {'visualizePathStyle': {
                'fill': 'transparent',
                'stroke': '#fff',
                'lineStyle': 'dashed',
                'strokeWidth': .15,
                'opacity': .1
            }, range: 0})
            going_home_bool = True
    else:
        jobs.define_target(creep)
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
                result = creep.transfer(target, RESOURCE_ENERGY)
                if result == ERR_FULL:
                    print(creep.name + " - container is full!")
                    home = Game.getObjectById(creep.memory.home)
                    need_additional_lorries = home.memory.need_additional_lorries
                    need_additional_lorries = round((need_additional_lorries + 0.01), 2)
                    home.memory.need_additional_lorries = need_additional_lorries
                    creep.memory.job = 'worker'
                    del creep.memory.target
                    del creep.memory.duty
                elif result != OK:
                    del creep.memory.target
                    jobs.define_target(creep)
                    print("[{}] Unknown result from creep.transfer({}):"
                          " {}".format(creep.name, 'transfer', result))
            else:
                creep.moveTo(target, {'visualizePathStyle': {
                    'fill': 'transparent',
                    'stroke': '#fff',
                    'lineStyle': 'dashed',
                    'strokeWidth': .15,
                    'opacity': .1
                }, range: 0})
        else:
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def going_to_help(creep):
    creep.say('🗡️')
    fleeing_creep = Game.getObjectById(creep.memory.fleeing_creep)
    if fleeing_creep:
        creep.moveTo(fleeing_creep, {'visualizePathStyle': {
            'fill': 'transparent',
            'stroke': '#fff',
            'lineStyle': 'dashed',
            'strokeWidth': .15,
            'opacity': .1
        }, range: 0})
        if creep.pos.inRangeTo(fleeing_creep, 5):
            jobs.define_target(creep)
    else:
        jobs.define_target(creep)


def claiming(creep):
    controller = Game.getObjectById(creep.memory.controller)
    if controller:
        result = creep.claimController(controller)
        if result == ERR_NOT_IN_RANGE:
            creep.moveTo(controller, {'visualizePathStyle': {
                'fill': 'transparent',
                'stroke': '#fff',
                'lineStyle': 'dashed',
                'strokeWidth': .15,
                'opacity': .1
            }, range: 0})
            creep.say('MY')
        else:
            flag = Game.flags[Memory.claim]
            if flag:
                flag.pos.createConstructionSite(STRUCTURE_SPAWN)
                Memory.building_spawn = flag.name


def not_going_to_bs(creep):
    not_going_to_bs_bool = True
    flag = Game.flags[creep.memory.flag]
    if flag:
        if creep.room != flag.room:
            creep.moveTo(flag)
            creep.say('BS')
            print('BS ' + creep.name)
            not_going_to_bs_bool = False
            creep.memory.job = 'spawn_builder'
    return not_going_to_bs_bool
