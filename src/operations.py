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


def move_away_from_creeps(creep):
    move_away_bool = False
    creep_to_flee = _(creep.room.find(FIND_MY_CREEPS)) \
        .filter(lambda c: c.id != creep.id and c.id != creep.memory.healer) \
        .sortBy(lambda c: c.pos.getRangeTo(creep)).first()
    if creep_to_flee:
        creep.memory.work_place = True
        if creep.pos.inRangeTo(creep_to_flee, 2):
            creep.say('👣')
            all_creeps_except_me = _.filter(creep.room.find(FIND_MY_CREEPS), lambda c: (c.id != creep.id))
            flee_condition = _.map(all_creeps_except_me, lambda c: {'pos': c.pos, 'range': 4})
            flee_path = PathFinder.search(
                creep.pos,
                flee_condition,
                {'flee': True}
            ).path
            creep.moveByPath(flee_path)
            move_away_bool = True
    return move_away_bool


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


def pick_up_tombstone(creep):
    target = Game.getObjectById(creep.memory.target)
    if target:
        if target.store[RESOURCE_ENERGY] > 0:
            creep.say('⚰')
            if creep.pos.isNearTo(target):
                del creep.memory.path
                result = creep.withdraw(target, RESOURCE_ENERGY)
                if result == OK or result == -6 or result == -8:
                    del creep.memory.target
                    del creep.memory.task
            creep.moveTo(target)
        else:
            del creep.memory.task
    else:
        del creep.memory.task


def pick_up_energy(creep):
    energy_near = creep.pos.findInRange(FIND_DROPPED_RESOURCES, 1)[0]
    if energy_near:
        creep.pickup(energy_near)
    tombstone = creep.pos.findInRange(FIND_TOMBSTONES, 1)[0]
    if tombstone:
        creep.withdraw(tombstone, RESOURCE_ENERGY)


def verify_targets_energy_on_the_way(creep, target, cluster_memory):
    containers = cluster_memory.claimed_room.containers
    for target_in_memory in containers:
        if target_in_memory.id == target.id:
            target_in_memory.energy_on_the_way = target_in_memory.energy_on_the_way + \
                                                 creep.store[RESOURCE_ENERGY] - creep.store.getCapacity()


def decrease_creeps_needed(creep_virtual):
    spawn = Game.spawns[creep_virtual.cluster]
    creeps_needed = spawn.memory.creeps_needed
    if creep_virtual.role == 'worker':
        if creeps_needed.workers > 1:
            creeps_needed.workers = creeps_needed.workers - 0.01
    if creep_virtual.role == 'hauler':
        if creeps_needed.haulers > 1:
            creeps_needed.haulers = creeps_needed.haulers - 0.01


def withdraw_by_memory(creep, cluster_memory):
    if creep.store[RESOURCE_ENERGY] <= 0:
        target = Game.getObjectById(creep.memory.target)
        if target:
            creep.say('🚚')
            verify_targets_energy_on_the_way(creep, target, cluster_memory)
            if target.store[RESOURCE_ENERGY] > 0:
                is_close = creep.pos.isNearTo(target)
                if is_close:
                    if target.structureType == STRUCTURE_STORAGE:
                        decrease_creeps_needed(creep)
                    result = creep.withdraw(target, RESOURCE_ENERGY)
                    if result != OK:
                        del creep.memory.task
                        print("[{}] Unknown result from creep.withdraw({}):"
                              " {}".format(creep.name, 'withdraw', result))
                moving_by_path(creep, target)
            else:
                del creep.memory.task
        else:
            del creep.memory.task
    else:
        del creep.memory.task


def transfer_by_memory(creep, cluster_memory):
    if creep.store[RESOURCE_ENERGY] > 0:
        target = Game.getObjectById(creep.memory.target)
        if target:
            verify_targets_energy_on_the_way(creep, target, cluster_memory)
            creep.say('🚛')
            is_close = creep.pos.isNearTo(target)
            if is_close:
                result = creep.transfer(target, RESOURCE_ENERGY)
                if result == OK or result == ERR_FULL:
                    del creep.memory.task
                else:
                    del creep.memory.task
                    print("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                        creep.name, 'store', RESOURCE_ENERGY, result))
            moving_by_path(creep, target)
        else:
            del creep.memory.task
    else:
        del creep.memory.task


def moving_by_path(creep, target):
    result = undefined
    if target:
        if creep.pos.inRangeTo(target, 1):
            if creep.pos.isNearTo(target):
                creep.memory.work_place = True
            else:
                creep.moveTo(target)
            if creep.memory.path:
                del creep.memory.path
        else:
            creep.memory.work_place = False
            creeps_close = creep.pos.findInRange(FIND_MY_CREEPS, 2)
            busy_creep = _(creeps_close).filter(lambda c: c.memory.work_place is True).sample()
            not_my_creep_close = _(creep.pos.findInRange(FIND_HOSTILE_CREEPS, 1)).sample()
            if busy_creep or not_my_creep_close:
                creep.moveTo(target)
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
    else:
        del creep.memory.path


def transfer_to_spawning_structure(creep, cluster_memory):
    while creep.store[RESOURCE_ENERGY] > 0 and cluster_memory.claimed_room.energy_percentage < 100:
        accidentally_delivering_for_spawning(creep)
        target = Game.getObjectById(creep.memory.target)
        if target:
            cluster_memory.claimed_room.energy_on_the_way = cluster_memory.claimed_room.energy_on_the_way + \
                                                            creep.store[RESOURCE_ENERGY]
            if target.energy < target.energyCapacity:
                if creep.pos.isNearTo(target):
                    creep.say('🪂')
                    creep.transfer(target, RESOURCE_ENERGY)
                    tasks.define_another_spawning_structure(creep, cluster_memory)
                    return
                else:
                    creep.say('⚙')
                    moving_by_path(creep, target)
                    return
            else:
                tasks.define_another_spawning_structure(creep, cluster_memory)
        else:
            tasks.define_another_spawning_structure(creep, cluster_memory)
    else:
        del creep.memory.task


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


def withdraw_from_closest(creep):
    if creep.store[RESOURCE_ENERGY] <= 0:
        target = _(creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER or
                               s.structureType == STRUCTURE_STORAGE
                               or s.structureType == STRUCTURE_LINK
                               or s.structureType == STRUCTURE_TERMINAL) and
                              s.store[RESOURCE_ENERGY] >= creep.store.getCapacity()) \
            .sortBy(lambda s: s.pos.getRangeTo(creep)).first()
        if target:
            creep.say('🛒')
            moving_by_path(creep, target)
            is_close = creep.pos.isNearTo(target)
            if is_close:
                result = creep.withdraw(target, RESOURCE_ENERGY)
                if result != OK:
                    del creep.memory.target
                    del creep.memory.task
                    print("[{}] Unknown result from creep.withdraw({}):"
                          " {}".format(creep.name, 'withdraw', result))
        else:
            del creep.memory.task
    else:
        del creep.memory.task


def worker_mining(creep, cluster_memory):
    source = Game.getObjectById(creep.memory.target)
    if creep.store[RESOURCE_ENERGY] < creep.store.getCapacity():
        for source_in_memory in cluster_memory.claimed_room.sources:
            if source_in_memory.id == source.id:
                source_in_memory.energy_on_the_way = source_in_memory.energy_on_the_way + \
                                                     creep.store[RESOURCE_ENERGY] - creep.store.getCapacity()

                processed_energy_of_source = source_in_memory.energy + source_in_memory.energy_on_the_way
                source_in_memory.processed_energy_of_source = processed_energy_of_source
                source_in_memory.processed_energy_to_ticks_ratio = processed_energy_of_source / source_in_memory.ticks
        if creep.store.getCapacity() - creep.store[RESOURCE_ENERGY] == source.energy:
            creep.say('⚖')
            if source.energy <= 25:
                del creep.memory.task
        else:
            creep.say('⛏')
        if creep.pos.isNearTo(source):
            creep.memory.work_place = True
            close_creep = _(creep.pos.findInRange(FIND_MY_CREEPS, 1)) \
                .filter(lambda c: c.pos.isNearTo(source)) \
                .sortBy(lambda c: c.store[RESOURCE_ENERGY]).first()
            if close_creep:
                if creep.store[RESOURCE_ENERGY] >= close_creep.store[RESOURCE_ENERGY]:
                    creep.transfer(close_creep, RESOURCE_ENERGY)
            result = creep.harvest(source)
            if result == -6:
                coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                     lambda c: c.memory.target == creep.memory.target)
                if len(coworkers) > 1:
                    del creep.memory.task
                else:
                    creep.say('⏳')
            if result != OK and result != -6:
                print("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, 'mine', result))
        elif creep.pos.inRangeTo(source, 3):
            if creep.moveTo(source) == -2:
                del creep.memory.task
        elif not creep.pos.inRangeTo(source, 3):
            moving_by_path(creep, source)
        else:
            if source.energy <= 0:
                coworkers = _.filter(creep.room.find(FIND_MY_CREEPS),
                                     lambda c: c.memory.target == creep.memory.target)
                if len(coworkers) > 1:
                    del creep.memory.task
                else:
                    creep.say('⏳')
            else:
                paving_roads(creep)
    else:
        del creep.memory.task


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
    banned_place = _(creep.pos.lookFor(LOOK_FLAGS)) \
        .filter(lambda s: s.name[:3] == 'ban').sample()
    if on_road or banned_place:
        for road_memory in roads_memory:
            str_road_memory = str(road_memory)
            str_road_coors = '{\'' + real_coors_str + '\': ' + str(road_memory[real_coors_str]) + '}'
            if str_road_memory == str_road_coors:
                roads_memory.remove(road_memory)
    else:
        if not creep.memory.work_place:
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
                    if new_counter >= 5000:
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
                result = creep.dismantle(target)
                if result != OK:
                    del creep.memory.task
                    print("[{}] Unknown result from creep.dismantle({}): {}"
                          .format(creep.name, 'dismantle', result))
                if target.store:
                    if target.store[RESOURCE_ENERGY] > 0:
                        creep.withdraw(target, RESOURCE_ENERGY)
            moving_by_path(creep, target)
        else:
            del creep.memory.task
    else:
        del creep.memory.task


def repairing(creep):
    move_away_from_source(creep)
    if creep.store[RESOURCE_ENERGY] > 0:
        creep.say('🔧')
        target = Game.getObjectById(creep.memory.target)
        if target:
            if target.hits >= target.hitsMax:
                del creep.memory.path
                target = _(creep.room.find(FIND_STRUCTURES)) \
                    .filter(lambda s: (s.hits < s.hitsMax) and
                                      s.structureType != STRUCTURE_WALL) \
                    .sortBy(lambda s: (s.pos.getRangeTo(target))).first()
                if target:
                    creep.memory.target = target.id
                else:
                    del creep.memory.task
            if target:
                is_close = creep.pos.inRangeTo(target, 3)
                if is_close:
                    result = creep.repair(target)
                    if result != OK:
                        del creep.memory.target
                        del creep.memory.task
                        print("[{}] Unknown result from creep.build({}): {}".format(creep.name, 'build', result))
                moving_by_path(creep, target)
            else:
                del creep.memory.task
    else:
        del creep.memory.task


def building(creep):
    move_away_from_source(creep)
    if creep.store[RESOURCE_ENERGY] > 0:
        creep.say('⚒')
        target = Game.getObjectById(creep.memory.target)
        if target:
            is_close = creep.pos.inRangeTo(target, 3)
            if is_close:
                creep.memory.work_place = True
                result = creep.build(target)
                if result != OK:
                    del creep.memory.task
                    print("[{}] Unknown result from creep.build({}): {}".format(creep.name, 'build', result))
            moving_by_path(creep, target)
        else:
            del creep.memory.task
    else:
        del creep.memory.task


def upgrading(creep):
    if creep.store[RESOURCE_ENERGY] > 0:
        creep.say('🔬')
        target = Game.getObjectById(creep.memory.target)
        is_close = creep.pos.inRangeTo(target, 3)
        if is_close:
            result = creep.upgradeController(target)
            if result != OK and result != -6 and result != -9:
                print("[{}] Unknown result from creep.upgradeController({}): {}".format(
                    creep.name, 'upgrade', result))
        moving_by_path(creep, target)
    else:
        del creep.memory.task


def miner_mining(creep, creep_virtual):
    creep_memory = creep.memory
    source = Game.getObjectById(creep_memory.source)
    container = Game.getObjectById(creep_memory.container)
    # creep_virtual.source = source.id
    # creep_virtual.container = container.id
    if container:
        if creep.pos.isNearTo(source) and creep.pos.isNearTo(container):
            if creep.store[RESOURCE_ENERGY] <= 92 and creep.memory.work_place and not creep.memory.repairing:
                pick_up_energy(creep)
                creep.say('⛏')
                source = Game.getObjectById(creep.memory.source)
                result = creep.harvest(source)
                if result != OK and result != -6:
                    print("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, 'mine', result))
                if container.hits > container.hitsMax * 0.2:
                    creep.transfer(container, RESOURCE_ENERGY)
            elif creep.store[RESOURCE_ENERGY] > 0 and creep.memory.work_place and creep.memory.repairing:
                creep.say('🔧')
                creep.repair(container)
            elif creep.store[RESOURCE_ENERGY] > 92 and creep.memory.work_place:
                if container.hits <= container.hitsMax * 0.2:
                    creep.memory.repairing = True
                else:
                    creep.memory.repairing = False
                    creep.say('💼')
                    creep.transfer(container, RESOURCE_ENERGY)
            elif creep.store[RESOURCE_ENERGY] <= 0:
                creep.memory.repairing = False
        else:
            creep.memory.work_place = False
            del creep.memory.task
            del creep.memory.source
            del creep.memory.container
    else:
        creep.memory.work_place = False
        del creep.memory.source
        del creep.memory.container
        del creep.memory.task


def recalculate_miners_path(creep):
    creep_memory = creep.memory
    source = Game.getObjectById(creep_memory.source)
    container = Game.getObjectById(creep_memory.container)
    if container:
        creep.say('?')
        place1 = source.pos
        place2 = container.pos
        if source.pos.x - container.pos.x == 2:
            place1.x = place1.x - 1
            place2.x = place2.x + 1
            if place1.y == place2.y:
                place2.y = place2.y + 1
                road = _.sum(place2.lookFor(LOOK_STRUCTURES), lambda s: s.structureType == STRUCTURE_ROAD)
                if place2.lookFor(LOOK_TERRAIN) == 'wall' and road == 0:
                    place2.y = place2.y - 2
                road = _.sum(place1.lookFor(LOOK_STRUCTURES), lambda s: s.structureType == STRUCTURE_ROAD)
                if place1.lookFor(LOOK_TERRAIN) == 'wall' and road == 0:
                    place1.y = place1.y - 1
                    road = _.sum(place1.lookFor(LOOK_STRUCTURES), lambda s: s.structureType == STRUCTURE_ROAD)
                    if place1.lookFor(LOOK_TERRAIN) == 'wall' and road == 0:
                        place1.y = place1.y + 2
        elif source.pos.x - container.pos.x == - 2:
            place1.x = place1.x + 1
            place2.x = place2.x - 1
            if place1.y == place2.y:
                place2.y = place2.y + 1
                road = _.sum(place2.lookFor(LOOK_STRUCTURES), lambda s: s.structureType == STRUCTURE_ROAD)
                if place2.lookFor(LOOK_TERRAIN) == 'wall' and road == 0:
                    place2.y = place2.y - 2
                road = _.sum(place1.lookFor(LOOK_STRUCTURES), lambda s: s.structureType == STRUCTURE_ROAD)
                if place1.lookFor(LOOK_TERRAIN) == 'wall' and road == 0:
                    place1.y = place1.y - 1
                    road = _.sum(place1.lookFor(LOOK_STRUCTURES), lambda s: s.structureType == STRUCTURE_ROAD)
                    if place1.lookFor(LOOK_TERRAIN) == 'wall' and road == 0:
                        place1.y = place1.y + 2
        elif source.pos.y - container.pos.y == 2:
            place1.y = place1.y - 1
            place2.y = place2.y + 1
            if place1.x == place2.x:
                place2.x = place2.x + 1
                road = _.sum(place2.lookFor(LOOK_STRUCTURES), lambda s: s.structureType == STRUCTURE_ROAD)
                if place2.lookFor(LOOK_TERRAIN) == 'wall' and road == 0:
                    place2.x = place2.x - 2
                road = _.sum(place1.lookFor(LOOK_STRUCTURES), lambda s: s.structureType == STRUCTURE_ROAD)
                if place1.lookFor(LOOK_TERRAIN) == 'wall' and road == 0:
                    place1.x = place1.x - 1
                    road = _.sum(place1.lookFor(LOOK_STRUCTURES), lambda s: s.structureType == STRUCTURE_ROAD)
                    if place1.lookFor(LOOK_TERRAIN) == 'wall' and road == 0:
                        place1.x = place1.x + 2
        elif source.pos.y - container.pos.y == - 2:
            place1.y = place1.y + 1
            place2.y = place2.y - 1
            if place1.x == place2.x:
                place2.x = place2.x + 1
                road = _.sum(place2.lookFor(LOOK_STRUCTURES), lambda s: s.structureType == STRUCTURE_ROAD)
                if place2.lookFor(LOOK_TERRAIN) == 'wall' and road == 0:
                    place2.x = place2.x - 2
                road = _.sum(place1.lookFor(LOOK_STRUCTURES), lambda s: s.structureType == STRUCTURE_ROAD)
                if place1.lookFor(LOOK_TERRAIN) == 'wall' and road == 0:
                    place1.x = place1.x - 1
                    road = _.sum(place1.lookFor(LOOK_STRUCTURES), lambda s: s.structureType == STRUCTURE_ROAD)
                    if place1.lookFor(LOOK_TERRAIN) == 'wall' and road == 0:
                        place1.x = place1.x + 2

        # print(str(place1) + '  ' + str(place2) + '   ' + creep.name)

        miner = _.sum(place2.lookFor(LOOK_CREEPS), lambda c: c.memory.role == 'miner')
        if miner == 0:
            creeps_close = creep.pos.findInRange(FIND_MY_CREEPS, 2)
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
        else:
            creeps_close = creep.pos.findInRange(FIND_MY_CREEPS, 2)
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
        creep.memory = creep_memory
    else:
        del creep.memory.source
        del creep.memory.container
        del creep.memory.task


def going_to_mining_place(creep, creep_virtual):
    creep_memory = creep.memory
    source = Game.getObjectById(creep_memory.source)
    container = Game.getObjectById(creep_memory.container)
    # creep_virtual.source = source.id
    # creep_virtual.container = container.id
    if creep.pos.isNearTo(source) and creep.pos.isNearTo(container):
        creep_memory.work_place = True
        del creep.memory.task
    else:
        creeps_close = creep.pos.findInRange(FIND_MY_CREEPS, 2)
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
                if result == -5:
                    del creep_memory.path
            else:
                recalculate_miners_path(creep)
    creep.memory = creep_memory


def defending(creep):
    if not just_heal_anything(creep):
        if not move_away_from_creeps(creep):
            creep.say('🛡️')


def attacking(creep):
    enemy = creep.pos.findClosestByRange(FIND_HOSTILE_CREEPS, {'filter': lambda e: e.owner.username != 'rep71Le'})
    if enemy:
        creep.say('⚔')
        attack_depending_on_range(creep, enemy)
    else:
        structure = creep.pos.findClosestByRange(FIND_HOSTILE_STRUCTURES,
                                                 {'filter': lambda e: e.owner.username != 'rep71Le'})
        if structure:
            if structure.structureType != STRUCTURE_CONTROLLER:
                creep.say('⚔')
                attack_depending_on_range(creep, structure)
            else:
                del creep.memory.task
        else:
            del creep.memory.task
    healing(creep)


def attack_nearest_structure(creep):
    structure = creep.pos.findClosestByRange(FIND_HOSTILE_STRUCTURES,
                                             {'filter': lambda e: e.owner.username != 'rep71Le'})
    if structure:
        if structure.structureType != STRUCTURE_CONTROLLER:
            creep.say('⚔')
            attack_depending_on_range(creep, structure)


def attack_depending_on_range(creep, target):
    if creep.pos.inRangeTo(target, 3):
        if creep.pos.isNearTo(target):
            enemies = _.filter(creep.pos.findInRange(FIND_HOSTILE_CREEPS, 3),
                               lambda e: e.owner.username != 'rep71Le')
            structures = _.filter(creep.pos.findInRange(FIND_HOSTILE_STRUCTURES, 3),
                                  lambda e: e.owner.username != 'rep71Le')
            all_targets = enemies + structures
            if all_targets:
                creep.rangedMassAttack(all_targets)
        else:
            creep.rangedAttack(target)
            creep.moveTo(target)
            attack_nearest_structure(creep)
    else:
        creep.moveTo(target)
        attack_nearest_structure(creep)


def healing(creep):
    patient = _(creep.pos.findInRange(FIND_MY_CREEPS, 3)) \
        .filter(lambda c: c.hits < c.hitsMax) \
        .sortBy(lambda c: c.hitsMax / c.hits).first()
    if patient:
        if creep.pos.isNearTo(patient):
            creep.heal(patient)
        else:
            creep.rangedHeal(patient)
    else:
        creep.heal(creep)
    return patient


def just_heal_anything(creep):
    need_to_heal = False
    patient = _(creep.room.find(FIND_MY_CREEPS)) \
        .filter(lambda c: c.hits < c.hitsMax and c.id != creep.id) \
        .sortBy(lambda c: c.pos.getRangeTo(creep)).first()
    if patient:
        need_to_heal = True
        creep.say('🚑')
        if creep.pos.isNearTo(patient):
            creep.memory.work_place = True
        else:
            creep.memory.work_place = False
            moving_by_path(creep, patient)
            if creep.pos.isNearTo(patient):
                creep.heal(patient)
            else:
                creep.rangedHeal(patient)
    else:
        creep.heal(creep)
    return need_to_heal


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


def accidentally_delivering_to_worker(creep):
    if creep.store[RESOURCE_ENERGY] > 0:
        targets = creep.pos.findInRange(FIND_MY_CREEPS, 1)
        if targets:
            target_empty_worker = _(targets).filter(lambda t: t.memory.role == 'worker' and
                                                              t.memory.task != 'dismantling' and
                                                              t.store[RESOURCE_ENERGY] < t.store.getCapacity()).sample()
            if target_empty_worker:
                result = creep.transfer(target_empty_worker, RESOURCE_ENERGY)
                if result != OK:
                    print("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                        creep.name, 'accidentally to worker', RESOURCE_ENERGY, result))