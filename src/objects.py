import clusters
import roles
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
        clusters.cluster_runner(self.spawn)

    def towering_towers(self, spawn):
        towers = _.filter(spawn.room.find(FIND_STRUCTURES), lambda s: s.structureType == STRUCTURE_TOWER)
        if towers:
            for tower in towers:
                if tower.store[RESOURCE_ENERGY] >= 10:
                    enemy = _(tower.room.find(FIND_HOSTILE_CREEPS,
                                              {'filter': lambda e: e.owner.username != 'rep71Le'})).sortBy(
                        lambda e: e.pos.getRangeTo(tower)).first()
                    if enemy:
                        if tower.pos.inRangeTo(enemy, 15):
                            tower.attack(enemy)
                    damaged_creep = _(tower.pos.findInRange(FIND_MY_CREEPS, 15)) \
                        .filter(lambda c: c.hits < c.hitsMax - 300) \
                        .sortBy(lambda c: c.pos.getRangeTo(tower)).first()
                    if damaged_creep:
                        tower.heal(damaged_creep)


# noinspection PyMethodMayBeStatic
class CreepRunner:
    def __init__(self, creep):
        self.creep = creep

    def creeping_creep(self):
        jobs.job_runner(self.creep)
        roles.role_runner(self.creep)


class FlagRunner:
    def __init__(self, flag):
        self.flag = flag

    def flagging_flag(self):
        flags.flag_runner(self.flag)
