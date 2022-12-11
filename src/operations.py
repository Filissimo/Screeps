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
    result = False
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
            result = True
    return result


def withdraw_by_memory(creep, cluster_memory):
    if creep.store[RESOURCE_ENERGY] <= 0:
        creep.say('🚚')
        target = Game.getObjectById(creep.memory.target)
        if target:
            for target_in_memory in cluster_memory.claimed_room.containers:
                if target_in_memory.id == target.id:
                    if not target_in_memory.energy_on_the_way:
                        target_in_memory.energy_on_the_way = creep.store[RESOURCE_ENERGY] - creep.store.getCapacity()
                    else:
                        target_in_memory.energy_on_the_way = target_in_memory.energy_on_the_way +\
                            creep.store[RESOURCE_ENERGY] - creep.store.getCapacity()
            if target.store[RESOURCE_ENERGY] >= creep.store.getCapacity():
                is_close = creep.pos.isNearTo(target)
                if is_close:
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
            if target.structureType == STRUCTURE_CONTAINER:
                creep.say('🚛')
                for target_in_memory in cluster_memory.claimed_room.containers:
                    if target_in_memory.id == target.id:
                        if not target_in_memory.energy_on_the_way:
                            target_in_memory.energy_on_the_way = creep.store[RESOURCE_ENERGY]
                        else:
                            target_in_memory.energy_on_the_way = \
                                target_in_memory.energy_on_the_way + creep.store[RESOURCE_ENERGY]
            else:
                creep.say('⚙')
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
