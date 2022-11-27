from defs import *
from src import jobs, spawns, flags

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


# noinspection PyMethodMayBeStatic
class SpawnRunner:
    def __init__(self, spawn):
        self.spawn = spawn

    def spawning_spawn(self):
        spawns.spawn_runner(self.spawn)

    def towering_towers(self, spawn):
        towers = _.filter(spawn.room.find(FIND_STRUCTURES), lambda s: s.structureType == STRUCTURE_TOWER)
        if towers:
            for tower in towers:
                if tower.store[RESOURCE_ENERGY] >= 10:
                    enemy = _(tower.pos.findInRange((FIND_HOSTILE_CREEPS,
                                                    {'filter': lambda e: e.owner.username != 'rep71Le'}), 10)) \
                        .sortBy(lambda e: e.pos.getRangeTo(tower)).first()
                    if enemy:
                        tower.attack(enemy)
                    damaged_creep = _(tower.pos.findInRange(FIND_MY_CREEPS, 10))\
                        .filter(lambda c: c.hits < c.hitsMax - 100) \
                        .sortBy(lambda c: c.pos.getRangeTo(tower)).first()
                    if damaged_creep:
                        tower.heal(damaged_creep)


# noinspection PyMethodMayBeStatic
class CreepRunner:
    def __init__(self, creep):
        self.creep = creep

    def creeping_creep(self):
        jobs.job_runner(self.creep)


class FlagRunner:
    def __init__(self, flag):
        self.flag = flag

    def flagging_flag(self):
        flags.flag_runner(self.flag)
