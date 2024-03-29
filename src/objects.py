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

