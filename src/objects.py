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


# noinspection PyMethodMayBeStatic
class SpawnRunner:
    def __init__(self, spawn):
        self.spawn = spawn

    def spawning_creep(self, spawn):
        job_name = self.creep_needed_to_spawn()
        if not self.spawn.spawning:
            if job_name:
                if Memory.Number_of_creep is undefined:
                    Memory.Number_of_creep = 0
                number_of_creep = Memory.Number_of_creep
                desired_body = self.define_body(job_name)
                result = self.spawn.spawnCreep(desired_body,
                                               job_name + '-' + str(number_of_creep),
                                               {'memory': {'job': job_name, 'home': self.spawn.id}})
                if result == OK:
                    print(str(desired_body) + ' - job: ' + job_name + ' - spawning.       Capacity: '
                          + self.spawn.room.energyCapacityAvailable)
                    number_of_creep = number_of_creep + 1
                    Memory.Number_of_creep = number_of_creep

    def creep_needed_to_spawn(self):
        desired_job = False
        self.spawn.memory.need_starters = False
        spawn_jobs = ['defender', 'miner', 'lorry', 'worker', 'starter',
                      'reservator1', 'reservator2', 'stealer1', 'stealer2']
        for job_name in spawn_jobs:
            my_creeps = _.filter(Game.creeps, lambda c: c.memory != undefined)
            my_creeps_with_memory = _.filter(my_creeps, lambda c: c.memory.job != undefined)
            creeps_filtered = _.filter(my_creeps_with_memory,
                                       lambda c: c.memory.home == self.spawn.id and c.memory.job == job_name and
                                                 c.ticksToLive > 50)
            number_of_creeps_filtered = len(creeps_filtered)
            sources = self.spawn.room.find(FIND_SOURCES)
            containers_near_mine = 0
            container_fullest = _(self.spawn.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: s.structureType == STRUCTURE_CONTAINER) \
                .sortBy(lambda s: s.store[RESOURCE_ENERGY]).last()
            container_emptiest = _(self.spawn.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: s.structureType == STRUCTURE_CONTAINER) \
                .sortBy(lambda s: s.store[RESOURCE_ENERGY]).first()
            for source in sources:
                container_near_mine = _.sum(self.spawn.room.find(FIND_STRUCTURES),
                                            lambda s: (s.structureType == STRUCTURE_CONTAINER and
                                                       s.pos.inRangeTo(source, 2)))
                containers_near_mine = containers_near_mine + container_near_mine
            if job_name == 'defender':
                need_defenders = len(self.spawn.room.find(FIND_HOSTILE_CREEPS))
                self.spawn.memory.need_defenders = (need_defenders * 2) + 1
                self.spawn.memory.starters = number_of_creeps_filtered
                if self.spawn.memory.need_defenders > number_of_creeps_filtered:
                    desired_job = job_name
            elif job_name == 'miner':
                self.spawn.memory.miners = number_of_creeps_filtered
                need_miners = containers_near_mine * 2
                need_starters = len(sources) * 4
                if not self.spawn.memory.need_additional_workers:
                    self.spawn.memory.need_additional_workers = 0
                need_additional_workers = self.spawn.memory.need_additional_workers
                if not self.spawn.memory.need_additional_lorries:
                    self.spawn.memory.need_additional_lorries = 0
                need_additional_lorries = self.spawn.memory.need_additional_lorries
                if number_of_creeps_filtered > 0:
                    need_starters = 0
                need_workers = 0
                if containers_near_mine > 0:
                    need_workers = 1
                if self.spawn.memory.lorries > 0:
                    need_workers = containers_near_mine
                if container_fullest:
                    if container_fullest.store[RESOURCE_ENERGY] >= container_fullest.store.getCapacity() * 0.7:
                        need_additional_lorries = need_additional_lorries + 0.01
                        self.spawn.memory.need_additional_lorries = need_additional_lorries
                    if container_fullest.store[RESOURCE_ENERGY] < container_fullest.store.getCapacity() * 0.7:
                        if need_additional_lorries > -2:
                            need_additional_lorries = need_additional_lorries - 0.05
                            self.spawn.memory.need_additional_lorries = need_additional_lorries
                if container_emptiest:
                    if container_emptiest.store[RESOURCE_ENERGY] > container_emptiest.store.getCapacity() * 0.4:
                        need_additional_workers = need_additional_workers + 0.01
                        self.spawn.memory.need_additional_workers = need_additional_workers
                    if container_emptiest.store[RESOURCE_ENERGY] <= container_emptiest.store.getCapacity() * 0.3:
                        if need_additional_workers > -2:
                            need_additional_workers = need_additional_workers - 0.01
                            self.spawn.memory.need_additional_workers = need_additional_workers
                need_lorries = 0
                if self.spawn.memory.miners > 0:
                    need_lorries = 1
                if containers_near_mine > 0:
                    need_lorries = containers_near_mine
                self.spawn.memory.need_lorries = round((need_lorries + need_additional_lorries), 2)
                self.spawn.memory.need_workers = round((need_workers + need_additional_workers), 2)
                self.spawn.memory.need_miners = need_miners
                self.spawn.memory.need_starters = need_starters
                if self.spawn.memory.need_miners > number_of_creeps_filtered:
                    desired_job = job_name
            elif job_name == 'starter':
                self.spawn.memory.starters = number_of_creeps_filtered
                if self.spawn.memory.need_starters > number_of_creeps_filtered:
                    desired_job = job_name
            elif job_name == 'lorry':
                self.spawn.memory.lorries = number_of_creeps_filtered
                if self.spawn.memory.need_lorries > number_of_creeps_filtered:
                    if self.spawn.memory.miners >= self.spawn.memory.need_miners:
                        desired_job = job_name

            elif job_name == 'worker':
                self.spawn.memory.workers = number_of_creeps_filtered
                if self.spawn.memory.need_workers > number_of_creeps_filtered:
                    if self.spawn.memory.lorries >= len(sources):
                        if self.spawn.memory.miners >= (len(sources) * 2) - 1:
                            desired_job = job_name

            elif job_name == 'reservator1':
                if self.spawn.memory.steal1:
                    self.spawn.memory.reservator1s = number_of_creeps_filtered
                    if 2 > number_of_creeps_filtered:
                        if creeps_filtered[0]:
                            controller = Game.getObjectById(creeps_filtered[0].memory.controller)
                            if controller:
                                if controller.reservation:
                                    if controller.reservation.ticksToEnd < 1000:
                                        desired_job = job_name
                                    if controller.reservation.ticksToEnd >= 1000:
                                        job_name == undefined
                        if controller is undefined:
                            desired_job = job_name

            elif job_name == 'reservator2':
                if self.spawn.memory.steal2:
                    self.spawn.memory.reservator2s = number_of_creeps_filtered
                    if 2 > number_of_creeps_filtered:
                        if creeps_filtered[0]:
                            controller = Game.getObjectById(creeps_filtered[0].memory.controller)
                            if controller:
                                if controller.reservation:
                                    if controller.reservation.ticksToEnd < 1000:
                                        desired_job = job_name
                                    if controller.reservation.ticksToEnd >= 1000:
                                        job_name == undefined
                        if controller is undefined:
                            desired_job = job_name

            elif job_name == 'stealer1':
                self.spawn.memory.stealer1s = number_of_creeps_filtered
                if self.spawn.memory.need_stealer1s > number_of_creeps_filtered:
                    worker_to_stealer = _(self.spawn.room.find(FIND_MY_CREEPS)) \
                        .filter(lambda c: c.memory.job == 'worker' and
                                          c.store[RESOURCE_ENERGY] == 0).sample()
                    if worker_to_stealer:
                        del worker_to_stealer.memory.duty
                        del worker_to_stealer.memory.target
                        worker_to_stealer.memory.job = 'stealer1'

            elif job_name == 'stealer2':
                self.spawn.memory.stealer2s = number_of_creeps_filtered
                if self.spawn.memory.need_stealer2s > number_of_creeps_filtered:
                    worker_to_stealer = _(self.spawn.room.find(FIND_MY_CREEPS)) \
                        .filter(lambda c: c.memory.job == 'worker' and
                                          c.store[RESOURCE_ENERGY] == 0).sample()
                    if worker_to_stealer:
                        del worker_to_stealer.memory.duty
                        del worker_to_stealer.memory.target
                        worker_to_stealer.memory.job = 'stealer2'

        if self.spawn.memory.lorries == 0 or self.spawn.memory.miners == 0:
            worker_to_starter = _(self.spawn.room.find(FIND_MY_CREEPS)
                                  .filter(lambda c: c.memory != undefined)
                                  .filter(lambda c: c.memory.job == 'worker')).sample()
            if worker_to_starter:
                worker_to_starter.memory.job = 'starter'
                del worker_to_starter.memory.duty
                del worker_to_starter.memory.target

        if self.spawn.memory.lorries > 0 and self.spawn.memory.miners > 0:
            starter_to_worker = _(self.spawn.room.find(FIND_MY_CREEPS)
                                  .filter(lambda c: c.memory != undefined)
                                  .filter(lambda c: c.memory.job == 'starter')).sample()
            if starter_to_worker:
                starter_to_worker.memory.job = 'worker'
                del starter_to_worker.memory.duty
                del starter_to_worker.memory.target

        return desired_job

    def define_body(self, job_name):
        desired_body = []
        if job_name == 'defender':
            for a in range(1, 10):
                if self.spawn.room.energyCapacityAvailable >= a * 300:
                    desired_body.extend([TOUGH, TOUGH, TOUGH, TOUGH, TOUGH])
            for a in range(1, 10):
                if self.spawn.room.energyCapacityAvailable >= a * 300:
                    desired_body.extend([RANGED_ATTACK, MOVE, MOVE])
        elif job_name == 'starter':
            desired_body = [WORK, CARRY, MOVE]
        elif job_name == 'worker':
            for a in range(1, 10):
                if self.spawn.room.energyCapacityAvailable >= a * 200:
                    desired_body.extend([WORK, CARRY, MOVE])
        elif job_name == 'miner':
            if self.spawn.room.energyCapacityAvailable >= 550:
                desired_body.extend([WORK, WORK, WORK, WORK, CARRY, MOVE, MOVE])
        elif job_name == 'lorry':
            range_max = self.spawn.memory.need_lorries
            for a in range(1, range_max):
                if self.spawn.room.energyCapacityAvailable >= a * 150:
                    desired_body.extend([CARRY, CARRY, MOVE])
        elif job_name[:10] == 'reservator':
            if self.spawn.room.energyCapacityAvailable >= 700:
                desired_body = [CLAIM, MOVE, MOVE]
        return desired_body


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
        if self.flag:
            if self.flag.name[:5] == 'Steal':
                spawn = Game.spawns[('Spawn' + self.flag.name[5:6])]
                if spawn:
                    if self.flag.name[6:7] == 1:
                        spawn.memory.steal1 = True
                    elif self.flag.name[6:7] == 2:
                        spawn.memory.steal2 = True
