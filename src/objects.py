from defs import *

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
        jobs = ['defender', 'miner', 'lorry', 'worker', 'starter', 'reservator1', 'reservator2', 'stealer1', 'stealer2']
        for job_name in jobs:
            my_creeps = _.filter(Game.creeps, lambda c: c.memory != undefined)
            my_creeps_with_memory = _.filter(my_creeps, lambda c: c.memory.job != undefined)
            creeps_filtered = _.filter(my_creeps_with_memory,
                                       lambda c: c.memory.home == self.spawn.id and c.memory.job == job_name and
                                                 c.ticksToLive > 30)
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
                need_miners = len(sources) * 2
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
                    if container_fullest.store[RESOURCE_ENERGY] < container_fullest.store.getCapacity() * 0.5:
                        if need_additional_lorries > -2:
                            need_additional_lorries = need_additional_lorries - 0.01
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
                if 4 > number_of_creeps_filtered:
                    worker_to_stealer = _(self.spawn.room.find(FIND_CREEPS)) \
                        .filter(lambda c: c.memory.job == 'worker' and
                                          c.store[RESOURCE_ENERGY] == 0).sample()
                    if worker_to_stealer:
                        del worker_to_stealer.memory.duty
                        del worker_to_stealer.memory.target
                        worker_to_stealer.memory.job = 'stealer1'

            elif job_name == 'stealer2':
                self.spawn.memory.stealer2s = number_of_creeps_filtered
                if self.spawn.memory.need_stealer2s > number_of_creeps_filtered:
                    worker_to_stealer = _(self.spawn.room.find(FIND_CREEPS)) \
                        .filter(lambda c: c.memory.job == 'worker' and
                                          c.store[RESOURCE_ENERGY] == 0).sample()
                    if worker_to_stealer:
                        del worker_to_stealer.memory.duty
                        del worker_to_stealer.memory.target
                        worker_to_stealer.memory.job = 'stealer2'

        if self.spawn.memory.lorries == 0 or self.spawn.memory.miners == 0:
            worker_to_starter = _(self.spawn.room.find(FIND_CREEPS)
                                  .filter(lambda c: c.memory.job == 'worker')).sample()
            if worker_to_starter:
                worker_to_starter.memory.job = 'starter'
                del worker_to_starter.memory.duty
                del worker_to_starter.memory.target

        if self.spawn.memory.lorries > 0 and self.spawn.memory.miners > 0:
            starter_to_worker = _(self.spawn.room.find(FIND_CREEPS)
                                  .filter(lambda c: c.memory.job == 'starter')).sample()
            if starter_to_worker:
                starter_to_worker.memory.job = 'worker'
                del starter_to_worker.memory.duty
                del starter_to_worker.memory.target

        return desired_job

    def define_body(self, job_name):
        desired_body = []
        if job_name == 'defender':
            if self.spawn.room.energyCapacityAvailable >= 210:
                desired_body = [TOUGH, RANGED_ATTACK, MOVE]
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
            if self.spawn.room.energyCapacityAvailable >= 450:
                desired_body.extend([CARRY, CARRY, CARRY, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE])
        elif job_name[:10] == 'reservator':
            if self.spawn.room.energyCapacityAvailable >= 700:
                desired_body = [CLAIM, MOVE, MOVE]
        return desired_body


# noinspection PyMethodMayBeStatic
class CreepRunner:
    def __init__(self, creep):
        self.creep = creep
        self.job = creep.memory.job

    def creeping_creep(self):
        if self.job == 'starter':
            self.run_starter()
        if self.job == 'miner':
            self.run_miner()
        if self.job == 'worker':
            self.run_worker()
        if self.job == 'lorry':
            self.run_lorry()
        if self.job == 'defender':
            self.run_defender()
        if self.job[:10] == 'reservator':
            self.run_reservator()
        if self.job[:7] == 'stealer':
            self.run_stealer()

    def run_starter(self):
        if self.creep.memory.target:
            if self.creep.memory.duty == 'mining':
                self.creep_mining()
            elif self.creep.memory.duty == 'withdrawing_from_closest':
                self.withdraw_from_closest()
            elif self.creep.memory.duty == 'delivering_for_spawn':
                self.delivering_for_spawning()
            elif self.creep.memory.duty == 'building':
                self.building()
            elif self.creep.memory.duty == 'upgrading':
                self.upgrading()
        else:
            self.define_starter_target()

    def run_worker(self):
        if self.creep.memory.target:
            self.paving_roads()
            if self.creep.memory.duty == 'dismantling_road':
                self.dismantling_road()
            elif self.creep.memory.duty == 'withdrawing_from_closest':
                self.withdraw_from_closest()
            elif self.creep.memory.duty == 'mining':
                self.creep_mining()
            elif self.creep.memory.duty == 'repairing':
                self.creep_repairing()
            elif self.creep.memory.duty == 'building':
                self.building()
            elif self.creep.memory.duty == 'upgrading':
                self.upgrading()
        else:
            self.define_worker_target()

    def run_miner(self):
        if self.creep.memory.source and self.creep.memory.container and self.creep.memory.duty:
            if self.creep.memory.duty == 'mining':
                self.miner_mines()
            elif self.creep.memory.duty == 'to_closest_container':
                self.miner_delivers()
        else:
            self.define_miner_targets()

    def run_lorry(self):
        if self.creep.memory.target:
            self.paving_roads()
            if self.creep.memory.duty == 'picking_up_tombstone':
                self.pick_up_tombstone()
            elif self.creep.memory.duty == 'withdrawing_from_fullest':
                self.withdrawing_from_fullest()
            elif self.creep.memory.duty == 'delivering_for_spawn':
                self.delivering_for_spawning()
            elif self.creep.memory.duty == 'delivering_to_emptiest':
                self.delivering_to_from_memory()
            elif self.creep.memory.duty == 'delivering_to_storage':
                self.delivering_to_from_memory()
        else:
            self.define_lorry_target()

    def run_defender(self):
        if self.creep.memory.duty:
            if self.creep.memory.duty == 'attacking':
                self.attacking()
            elif self.creep.memory.duty == 'defending':
                self.defending()
        else:
            self.define_defender_targets()

    def run_reservator(self):
        if self.creep.memory.duty:
            if self.creep.memory.duty == 'go_to_flag':
                self.going_to_flag()
            elif self.creep.memory.duty == 'reserving':
                self.reserving()
        else:
            self.define_reservator_targets()

    def define_reservator_targets(self):
        del self.creep.memory.duty
        del self.creep.memory.flag
        if not self.define_reservators_flag():
            self.define_controller()

    def run_stealer(self):
        self.paving_roads()
        if self.creep.memory.duty:
            if self.creep.memory.duty == 'go_to_flag':
                self.going_to_flag()
            elif self.creep.memory.duty == 'mining':
                self.creep_mining()
            elif self.creep.memory.duty == 'repairing':
                self.creep_repairing()
            elif self.creep.memory.duty == 'building':
                self.building()
            elif self.creep.memory.duty == 'going_home':
                self.going_home()
            elif self.creep.memory.duty == 'transferring_to_closest':
                self.transferring_to_closest()
        else:
            self.define_stealer_targets()

    def define_stealer_targets(self):
        del self.creep.memory.duty
        del self.creep.memory.target
        del self.creep.memory.flag
        if not self.define_stealers_flag():
            if not self.define_mining_target():
                if not self.define_closest_to_transfer():
                    if not self.define_repairing_target():
                        if not self.define_building_target():
                            self.define_going_home()

    def define_target(self):
        if self.job == 'starter':
            self.define_starter_target()
        elif self.job == 'miner':
            self.define_miner_targets()
        elif self.job == 'lorry':
            self.define_lorry_target()
        elif self.job == 'worker':
            self.define_worker_target()
        elif self.job == 'defender':
            self.define_defender_targets()
        if self.job[:10] == 'reservator':
            self.define_reservator_targets()
        if self.job[:7] == 'stealer':
            self.define_stealer_targets()

    def define_starter_target(self):
        del self.creep.memory.duty
        del self.creep.memory.target
        if not self.define_closest_to_withdraw():
            if not self.define_mining_target():
                if not self.define_deliver_for_spawn_target():
                    if not self.define_building_target():
                        self.define_upgrading_target()

    def define_miner_targets(self):
        if self.creep.memory.source and self.creep.memory.container:
            if self.creep.memory.duty == 'mining' and _.sum(self.creep.carry) > 42:
                self.creep.memory.duty = 'to_closest_container'
                self.creep.memory.target = 'to_closest_container'
            elif _.sum(self.creep.carry) <= 0:
                self.creep.memory.duty = 'mining'
                self.creep.memory.target = 'mining'
        else:
            sources = self.creep.room.find(FIND_SOURCES)
            for source in sources:
                container_near_mine = _(self.creep.room.find(FIND_STRUCTURES)) \
                    .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER and
                                       s.pos.inRangeTo(source, 2))) \
                    .sample()
                if container_near_mine:
                    miners = _.filter(self.creep.room.find(FIND_CREEPS),
                                      lambda c: c.memory.job == 'miner' and
                                                c.memory.container == container_near_mine.id and
                                                c.ticksToLive > 70)
                    if len(miners) < 2:
                        self.creep.memory.container = container_near_mine.id
                        self.creep.memory.source = source.id

    def define_worker_target(self):
        del self.creep.memory.duty
        del self.creep.memory.target
        if not self.define_closest_to_withdraw():
            if not self.define_mining_target():
                if not self.define_repairing_target():
                    if not self.define_building_target():
                        self.define_upgrading_target()

    def define_lorry_target(self):
        del self.creep.memory.duty
        del self.creep.memory.target
        if not self.define_lorry_to_pickup_tombstone():
            if not self.define_fullest():
                if not self.define_deliver_for_spawn_target():
                    if not self.define_emptiest():
                        self.define_storage()

    def define_mining_target(self):
        target = undefined
        if _.sum(self.creep.carry) <= 0:
            target = self.creep.pos.findClosestByPath(FIND_SOURCES_ACTIVE)
            if target:
                self.creep.memory.duty = 'mining'
                self.creep.memory.target = target.id
        return target

    def define_deliver_for_spawn_target(self):
        target = undefined
        if _.sum(self.creep.carry) > 0:
            target = _(self.creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION)
                                   and s.energy < s.energyCapacity)) \
                .sample()
            if target:
                self.creep.memory.duty = 'delivering_for_spawn'
                self.creep.memory.target = target.id
        return target

    def define_building_target(self):
        target = undefined
        if _.sum(self.creep.carry) > 0:
            target = self.creep.pos.findClosestByRange(FIND_CONSTRUCTION_SITES)
            if target:
                self.creep.memory.duty = 'building'
                self.creep.memory.target = target.id
        return target

    def define_upgrading_target(self):
        target = undefined
        if _.sum(self.creep.carry) > 0:
            target = _(self.creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: (s.structureType == STRUCTURE_CONTROLLER)) \
                .sample()
            if target:
                self.creep.memory.duty = 'upgrading'
                self.creep.memory.target = target.id
        return target

    def define_repairing_target(self):
        target = undefined
        if _.sum(self.creep.carry) > 0:
            target = _(self.creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: (s.hits < s.hitsMax * 0.05)) \
                .sortBy(lambda s: (s.hitsMax / s.hits)).last()
            if target:
                self.creep.memory.duty = 'repairing'
                self.creep.memory.target = target.id
        return target

    def define_closest_to_withdraw(self):
        target = undefined
        if _.sum(self.creep.carry) <= 0:
            target = _(self.creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER or
                                   s.structureType == STRUCTURE_STORAGE) and
                                  s.store[RESOURCE_ENERGY] >= self.creep.carryCapacity).sample()
            if target:
                self.creep.memory.duty = 'withdrawing_from_closest'
                self.creep.memory.target = target.id
        return target

    def define_fullest(self):
        target = undefined
        if _.sum(self.creep.carry) <= 0:
            target = _(self.creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER or
                                   s.structureType == STRUCTURE_STORAGE) and
                                  s.store[RESOURCE_ENERGY] > s.store.getCapacity() * 0.2) \
                .sortBy(lambda s: s.store[RESOURCE_ENERGY]).last()
            if target:
                self.creep.memory.duty = 'withdrawing_from_fullest'
                self.creep.memory.target = target.id
        return target

    def define_emptiest(self):
        target = undefined
        if _.sum(self.creep.carry) > 0:
            target = _(self.creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: s.structureType == STRUCTURE_CONTAINER and
                                  s.store[RESOURCE_ENERGY] < s.store.getCapacity() * 0.5) \
                .sortBy(lambda s: s.store[RESOURCE_ENERGY]).first()
            if target:
                self.creep.memory.duty = 'delivering_to_emptiest'
                self.creep.memory.target = target.id
        return target

    def creep_mining(self):
        if _.sum(self.creep.carry) < self.creep.carryCapacity:
            source = Game.getObjectById(self.creep.memory.target)
            if self.creep.pos.isNearTo(source):
                result = self.creep.harvest(source)
                if result != OK:
                    del self.creep.memory.target
                    self.define_target()
                    print("[{}] Unknown result from creep.harvest({}): {}".format(self.creep.name, 'mine', result))
            else:
                result = self.creep.moveTo(source, {'visualizePathStyle': {
                    'fill': 'transparent',
                    'stroke': '#fff',
                    'lineStyle': 'dashed',
                    'strokeWidth': .15,
                    'opacity': .1
                }, range: 0})
                if result == -2:
                    self.define_target()
        else:
            self.define_target()

    def delivering_for_spawning(self):
        if _.sum(self.creep.carry) > 0:
            target = _(self.creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: ((s.structureType == STRUCTURE_SPAWN or
                                    s.structureType == STRUCTURE_EXTENSION)
                                   and s.energy < s.energyCapacity)) \
                .sortBy(lambda s: (s.pos.getRangeTo(self.creep))).first()
            if target:
                is_close = self.creep.pos.isNearTo(target)
                if is_close:
                    result = self.creep.transfer(target, RESOURCE_ENERGY)
                    if result == OK or result == ERR_FULL:
                        del self.creep.memory.target
                        self.define_target()
                    else:
                        del self.creep.memory.target
                        self.define_target()
                        print("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                            self.creep.name, 'store', RESOURCE_ENERGY, result))
                else:
                    self.creep.moveTo(target, {'visualizePathStyle': {
                        'fill': 'transparent',
                        'stroke': '#fff',
                        'lineStyle': 'dashed',
                        'strokeWidth': .15,
                        'opacity': .1
                    }, range: 0})
            else:
                self.define_target()
        else:
            self.define_target()

    def upgrading(self):
        if _.sum(self.creep.carry) > 0:
            target = Game.getObjectById(self.creep.memory.target)
            is_close = self.creep.pos.inRangeTo(target, 3)
            if is_close:
                result = self.creep.upgradeController(target)
                if result != OK:
                    del self.creep.memory.target
                    self.define_target()
                    print("[{}] Unknown result from creep.upgradeController({}): {}".format(
                        self.creep.name, 'upgrade', result))
                if not self.creep.pos.inRangeTo(target, 1):
                    self.creep.moveTo(target, {'visualizePathStyle': {
                        'fill': 'transparent',
                        'stroke': '#fff',
                        'lineStyle': 'dashed',
                        'strokeWidth': .15,
                        'opacity': .1
                    }, range: 0})
            else:
                self.creep.moveTo(target, {'visualizePathStyle': {
                    'fill': 'transparent',
                    'stroke': '#fff',
                    'lineStyle': 'dashed',
                    'strokeWidth': .15,
                    'opacity': .1
                }, range: 0})
        else:
            self.define_target()

    def building(self):
        self.move_away_from_source()
        if _.sum(self.creep.carry) > 0:
            target = self.creep.pos.findClosestByRange(FIND_CONSTRUCTION_SITES)
            if target:
                is_close = self.creep.pos.inRangeTo(target, 3)
                if is_close:
                    result = self.creep.build(target)
                    if result != OK:
                        del self.creep.memory.target
                        self.define_target()
                        print("[{}] Unknown result from creep.build({}): {}".format(self.creep.name, 'build', result))
                    if not self.creep.pos.isNearTo(target):
                        self.creep.moveTo(target, {'visualizePathStyle': {
                            'fill': 'transparent',
                            'stroke': '#fff',
                            'lineStyle': 'dashed',
                            'strokeWidth': .15,
                            'opacity': .1
                        }, range: 0})
                else:
                    self.creep.moveTo(target, {'visualizePathStyle': {
                        'fill': 'transparent',
                        'stroke': '#fff',
                        'lineStyle': 'dashed',
                        'strokeWidth': .15,
                        'opacity': .1
                    }, range: 0})
            else:
                self.define_target()
        else:
            self.define_target()

    def miner_delivers(self):
        if _.sum(self.creep.carry) > 0:
            target = Game.getObjectById(self.creep.memory.container)
            if target:
                is_close = self.creep.pos.isNearTo(target)
                if is_close:
                    result = self.creep.transfer(target, RESOURCE_ENERGY)
                    if result == OK or result == ERR_FULL:
                        del self.creep.memory.target
                        self.define_target()
                    else:
                        del self.creep.memory.target
                        self.define_target()
                        print("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                            self.creep.name, 'store', RESOURCE_ENERGY, result))
                else:
                    self.creep.moveTo(target, {'visualizePathStyle': {
                        'fill': 'transparent',
                        'stroke': '#fff',
                        'lineStyle': 'dashed',
                        'strokeWidth': .15,
                        'opacity': .1
                    }, range: 0})
            else:
                self.define_target()
        else:
            self.define_target()

    def miner_mines(self):
        if _.sum(self.creep.carry) <= 42:
            source = Game.getObjectById(self.creep.memory.source)
            if self.creep.pos.isNearTo(source):
                result = self.creep.harvest(source)
                if result != OK and result != -6:
                    del self.creep.memory.target
                    self.define_target()
                    print("[{}] Unknown result from creep.harvest({}): {}".format(self.creep.name, 'mine', result))
            else:
                result = self.creep.moveTo(source, {'visualizePathStyle': {
                    'fill': 'transparent',
                    'stroke': '#fff',
                    'lineStyle': 'dashed',
                    'strokeWidth': .15,
                    'opacity': .1
                }, range: 0})
                if result == -2:
                    self.define_target()
        elif _.sum(self.creep.carry) > 42:
            self.define_target()

    def creep_repairing(self):
        self.move_away_from_source()
        if _.sum(self.creep.carry) > 0:
            target = Game.getObjectById(self.creep.memory.target)
            if target.hits < target.hitsMax * 0.8:
                target = _(self.creep.room.find(FIND_STRUCTURES)) \
                    .filter(lambda s: (s.hits < s.hitsMax * 0.8)) \
                    .sortBy(lambda s: (s.pos.getRangeTo(target))).first()
                if target:
                    self.creep.memory.target = target.id
            if target:
                is_close = self.creep.pos.inRangeTo(target, 3)
                if is_close:
                    result = self.creep.repair(target)
                    if result != OK:
                        del self.creep.memory.target
                        self.define_target()
                        print("[{}] Unknown result from creep.build({}): {}".format(self.creep.name, 'build', result))
                    if not self.creep.pos.inRangeTo(target, 1):
                        self.creep.moveTo(target, {'visualizePathStyle': {
                            'fill': 'transparent',
                            'stroke': '#fff',
                            'lineStyle': 'dashed',
                            'strokeWidth': .15,
                            'opacity': .1
                        }, range: 0})
                else:
                    self.creep.moveTo(target, {'visualizePathStyle': {
                        'fill': 'transparent',
                        'stroke': '#fff',
                        'lineStyle': 'dashed',
                        'strokeWidth': .15,
                        'opacity': .1
                    }, range: 0})
            else:
                self.define_target()
        else:
            self.define_target()

    def withdraw_from_closest(self):
        if _.sum(self.creep.carry) <= 0:
            target = _(self.creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER or
                                   s.structureType == STRUCTURE_STORAGE) and
                                  s.store[RESOURCE_ENERGY] >= self.creep.carryCapacity) \
                .sortBy(lambda s: (s.pos.getRangeTo(self.creep))).first()
            if target:
                is_close = self.creep.pos.isNearTo(target)
                if is_close:
                    result = self.creep.withdraw(target, RESOURCE_ENERGY)
                    if result != OK:
                        del self.creep.memory.target
                        self.define_target()
                        print("[{}] Unknown result from creep.withdraw({}):"
                              " {}".format(self.creep.name, 'withdraw', result))
                else:
                    self.creep.moveTo(target, {'visualizePathStyle': {
                        'fill': 'transparent',
                        'stroke': '#fff',
                        'lineStyle': 'dashed',
                        'strokeWidth': .15,
                        'opacity': .1
                    }, range: 0})
            else:
                self.define_target()
        else:
            self.define_target()

    def withdrawing_from_fullest(self):
        if _.sum(self.creep.carry) <= 0:
            target = Game.getObjectById(self.creep.memory.target)
            if target:
                is_close = self.creep.pos.isNearTo(target)
                if is_close:
                    result = self.creep.withdraw(target, RESOURCE_ENERGY)
                    if result != OK:
                        del self.creep.memory.target
                        self.define_target()
                        print("[{}] Unknown result from creep.withdraw({}):"
                              " {}".format(self.creep.name, 'withdraw', result))
                else:
                    self.creep.moveTo(target, {'visualizePathStyle': {
                        'fill': 'transparent',
                        'stroke': '#fff',
                        'lineStyle': 'dashed',
                        'strokeWidth': .15,
                        'opacity': .1
                    }, range: 0})
            else:
                self.define_target()
        else:
            self.define_target()

    def delivering_to_from_memory(self):
        if _.sum(self.creep.carry) > 0:
            target = Game.getObjectById(self.creep.memory.target)
            if target:
                is_close = self.creep.pos.isNearTo(target)
                if is_close:
                    result = self.creep.transfer(target, RESOURCE_ENERGY)
                    if result == OK or result == ERR_FULL:
                        del self.creep.memory.target
                        self.define_target()
                    else:
                        del self.creep.memory.target
                        self.define_target()
                        print("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                            self.creep.name, 'store', RESOURCE_ENERGY, result))
                else:
                    self.creep.moveTo(target, {'visualizePathStyle': {
                        'fill': 'transparent',
                        'stroke': '#fff',
                        'lineStyle': 'dashed',
                        'strokeWidth': .15,
                        'opacity': .1
                    }, range: 0})
            else:
                self.define_target()
        else:
            self.define_target()

    def move_away_from_source(self):
        source = self.creep.pos.findClosestByRange(FIND_SOURCES)
        if source:
            # self.creep.moveTo(source.pos, {'visualizePathStyle':{
            #                                                 'fill': 'transparent',
            #                                                 'stroke': '#fff',
            #                                                 'lineStyle': 'dashed',
            #                                                 'strokeWidth': .15,
            #                                                 'opacity': .1
            #                                             }, range: 0})
            if self.creep.pos.inRangeTo(source, 1):
                flee_condition = _.map(self.creep.room.find(FIND_SOURCES), lambda c: {'pos': c.pos, 'range': 3})
                flee_path = PathFinder.search(
                    self.creep.pos,
                    flee_condition,
                    {'flee': True}
                ).path
                self.creep.moveByPath(flee_path)

    def define_lorry_to_pickup_tombstone(self):
        target = undefined
        if _.sum(self.creep.carry) < self.creep.carryCapacity:
            target = _(self.creep.room.find(FIND_TOMBSTONES)) \
                .filter(lambda t: (t.store[RESOURCE_ENERGY] > 0)).first()
            if target != undefined:
                creep_to_pickup = _(self.creep.room.find(FIND_CREEPS)) \
                    .filter(lambda c: (c.carryCapacity > _.sum(c.carry)) and
                                      c.memory.job == 'lorry') \
                    .sortBy(lambda c: (c.pos.getRangeTo(target))).first()
                if creep_to_pickup:
                    creep_to_pickup.memory.duty = 'picking_up_tombstone'
                    creep_to_pickup.memory.target = target.id
        return target

    def pick_up_tombstone(self):
        target = Game.getObjectById(self.creep.memory.target)
        print(str(target) + ' ' + self.creep.name)
        if target:
            if self.creep.pos.isNearTo(target):
                result = self.creep.withdraw(target, RESOURCE_ENERGY)
                print(self.creep.name + ' picking up ' + result)
                if result == OK or result == -6:
                    del self.creep.memory.target
                    self.define_target()
                if result == -8:
                    del self.creep.memory.target
                    self.define_target()
            else:
                self.creep.moveTo(target, {'visualizePathStyle': {
                    'fill': 'transparent',
                    'stroke': '#fff',
                    'lineStyle': 'dashed',
                    'strokeWidth': .15,
                    'opacity': .1
                }, range: 0})
                print(self.creep.name + ' moving to pick up')
        else:
            self.define_target()

    def paving(self):
        if _.sum(self.creep.store) <= 0:
            self.creep.memory.paving_trigger = True
        if _.sum(self.creep.store) >= self.creep.store.getCapacity() and self.creep.memory.paving_trigger:
            if_on_road = _(self.creep.pos.lookFor(LOOK_STRUCTURES)) \
                .filter(lambda s: (s.structureType == STRUCTURE_ROAD or
                                   s.structureType == STRUCTURE_SPAWN)).sample()
            if if_on_road:
                print(self.creep + ': on road ' + self.creep.pos)
                # self.verify_roads()
            else:
                construction_sites = _.sum(self.creep.room.find(FIND_CONSTRUCTION_SITES),
                                           lambda cs: cs.progress < cs.progressTotal)
                if construction_sites <= 1:
                    result = self.creep.pos.createConstructionSite(STRUCTURE_ROAD)
                    if result != OK:
                        print(self.creep + ': no road, on construction site ' + self.creep.pos +
                              ', construction sites: ' + construction_sites)
                    else:
                        print(self.creep + ': no road, paving ' + self.creep.pos +
                              ', construction sites: ' + str(construction_sites))
                        self.creep.memory.paving_trigger = False
                else:
                    print(self.creep + ': no road ' + self.creep.pos +
                          ', but there are too many construction sites: ' + construction_sites)
                    self.creep.memory.paving_trigger = False

    def paving_roads(self):
        if not Memory.roads:
            Memory.roads = []
        real_coors_str = str(self.creep.pos)
        roads_memory = Memory.roads
        road_coors_new_object = {real_coors_str: 20}
        new_counter = undefined
        if_on_road = _(self.creep.pos.lookFor(LOOK_STRUCTURES)) \
            .filter(lambda s: (s.structureType == STRUCTURE_ROAD or
                               s.structureType == STRUCTURE_SPAWN)).sample()
        if not if_on_road:
            for road_memory in roads_memory:
                str_road_memory = str(road_memory)
                str_road_coors = '{\'' + real_coors_str + '\': ' + str(road_memory[real_coors_str]) + '}'
                if str_road_memory == str_road_coors:
                    new_counter = road_memory[real_coors_str] + 10
                    roads_memory.remove(road_memory)
            if str(roads_memory) == '[]':
                roads_memory.append(road_coors_new_object)
            else:
                if new_counter:
                    if new_counter >= 2000:
                        construction_sites = _.sum(self.creep.room.find(FIND_CONSTRUCTION_SITES),
                                                   lambda cs: cs.progress < cs.progressTotal)
                        if construction_sites <= 1:
                            result = self.creep.pos.createConstructionSite(STRUCTURE_ROAD)
                            if result != OK:
                                print(self.creep + ': no road, on construction site ' + self.creep.pos +
                                      ', construction sites: ' + construction_sites)
                            else:
                                print(self.creep + ': no road, paving ' + self.creep.pos +
                                      ', construction sites: ' + str(construction_sites))
                        else:
                            print(self.creep + ': no road ' + self.creep.pos +
                                  ', but there are too many construction sites: ' + construction_sites)
                    else:
                        road_increased_counter = {real_coors_str: new_counter}
                        roads_memory.append(road_increased_counter)
                else:
                    roads_memory.append(road_coors_new_object)
                Memory.roads = roads_memory

    def dismantling_road(self):
        if self.creep.store[RESOURCE_ENERGY] < self.creep.store.getCapacity():
            target = Game.getObjectById(self.creep.memory.target)
            if target:
                is_close = self.creep.pos.isNearTo(target)
                if is_close:
                    result = self.creep.dismantle(target)
                    if result != OK:
                        del self.creep.memory.target
                        self.define_target()
                        print("[{}] Unknown result from creep.dismantle({}): {}"
                              .format(self.creep.name, 'dismantle', result))
                else:
                    self.creep.moveTo(target, {'visualizePathStyle': {
                        'fill': 'transparent',
                        'stroke': '#fff',
                        'lineStyle': 'dashed',
                        'strokeWidth': .15,
                        'opacity': .1
                    }, range: 0})
            else:
                self.define_target()
        else:
            self.define_target()

    def define_road_to_dismantle(self):
        target = undefined
        if self.creep.store[RESOURCE_ENERGY] < self.creep.store.getCapacity():
            home = Game.getObjectById(self.creep.memory.home)
            target = Game.getObjectById(home.memory.road_to_dismantle)
            if target:
                self.creep.memory.duty = 'dismantling_road'
                self.creep.memory.target = target.id
        return target

    def define_defender_targets(self):
        if self.creep.memory.enemy and self.creep.memory.base:
            if self.creep.memory.duty == 'attacking':
                self.creep.memory.target = 'attacking'
            elif self.creep.memory.duty == 'defending':
                self.creep.memory.target = 'defending'
        else:
            enemy = self.creep.pos.findClosestByRange(FIND_HOSTILE_CREEPS)
            if enemy:
                self.creep.memory.duty = 'attacking'
                self.creep.memory.enemy = enemy.id
            else:
                self.creep.memory.duty = 'defending'
                self.creep.memory.base = self.creep.memory.home
                del self.creep.memory.enemy

    def attacking(self):
        hazard = self.creep.pos.findClosestByRange(FIND_HOSTILE_CREEPS)
        if hazard:
            if self.creep.pos.inRangeTo(hazard, 3):
                flee_condition = _.map(self.creep.room.find(FIND_HOSTILE_CREEPS), lambda c: {'pos': c.pos, 'range': 5})
                flee_path = PathFinder.search(
                    self.creep.pos,
                    flee_condition,
                    {'flee': True}
                ).path
                self.creep.moveByPath(flee_path)
        enemy = Game.getObjectById(self.creep.memory.enemy)
        if enemy:
            is_close = self.creep.pos.inRangeTo(enemy, 3)
            if is_close:
                result = self.creep.rangedAttack(enemy)
                if result != OK:
                    del self.creep.memory.enemy
                    self.define_target()
                    print("[{}] Unknown result from creep.ranged attack({}): {}".format(self.creep.name, 'r a', result))
                if not self.creep.pos.isNearTo(enemy):
                    self.creep.moveTo(enemy, {'visualizePathStyle': {
                        'fill': 'transparent',
                        'stroke': '#fff',
                        'lineStyle': 'dashed',
                        'strokeWidth': .15,
                        'opacity': .1
                    }, range: 0})
            else:
                self.creep.moveTo(enemy, {'visualizePathStyle': {
                    'fill': 'transparent',
                    'stroke': '#fff',
                    'lineStyle': 'dashed',
                    'strokeWidth': .15,
                    'opacity': .1
                }, range: 0})
        else:
            self.define_target()
            self.define_target()

    def defending(self):
        self.move_away_from_creeps()

    def move_away_from_creeps(self):
        creep_to_flee = _(self.creep.room.find(FIND_CREEPS)) \
            .filter(lambda c: (c.id != self.creep.id)) \
            .sortBy(lambda c: (c.pos.getRangeTo(creep_to_flee))).last()
        if creep_to_flee:
            if self.creep.pos.inRangeTo(creep_to_flee, 3):
                all_creeps_except_me = _.filter(self.creep.room.find(FIND_CREEPS), lambda c: (c.id != self.creep.id))
                flee_condition = _.map(all_creeps_except_me, lambda c: {'pos': c.pos, 'range': 7})
                flee_path = PathFinder.search(
                    self.creep.pos,
                    flee_condition,
                    {'flee': True}
                ).path
                self.creep.moveByPath(flee_path)

    def define_storage(self):
        target = undefined
        if _.sum(self.creep.carry) > 0:
            target = _.filter(self.creep.room.find(FIND_STRUCTURES),
                              lambda s: s.structureType == STRUCTURE_STORAGE)
            if target:
                self.creep.memory.duty = 'delivering_to_storage'
                self.creep.memory.target = target[0].id
        return target

    def define_reservators_flag(self):
        home = Game.getObjectById(self.creep.memory.home)
        flag = Game.flags["Steal" + home.name[5:6] + self.creep.name[10:11]]
        if flag:
            self.creep.memory.flag = flag.name
            self.creep.memory.duty = 'go_to_flag'
            if self.creep.pos.isNearTo(flag):
                flag = undefined
                del self.creep.memory.duty
        return flag

    def define_stealers_flag(self):
        flag = undefined
        if self.creep.store[RESOURCE_ENERGY] <= 0:
            home = Game.getObjectById(self.creep.memory.home)
            flag = Game.flags["Steal" + home.name[5:6] + self.creep.memory.job[7:8]]
            if flag:
                if self.creep.room == home.room:
                    self.creep.memory.flag = flag.name
                    self.creep.memory.duty = 'go_to_flag'
                    if self.creep.pos.isNearTo(flag):
                        flag = undefined
                        del self.creep.memory.duty
                else:
                    flag = undefined
        return flag

    def define_controller(self):
        controller = _(self.creep.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: s.structureType == STRUCTURE_CONTROLLER).sample()
        if controller:
            self.creep.memory.controller = controller.id
            self.creep.memory.duty = 'reserving'
        return controller

    def going_to_flag(self):
        flag = Game.flags[self.creep.memory.flag]
        self.creep.moveTo(flag, {'visualizePathStyle': {
            'fill': 'transparent',
            'stroke': '#fff',
            'lineStyle': 'dashed',
            'strokeWidth': .15,
            'opacity': .1
        }, range: 0})
        if self.creep.pos.isNearTo(flag):
            self.define_target()

    def reserving(self):
        controller = Game.getObjectById(self.creep.memory.controller)
        if self.creep.reserveController(controller) != OK:
            self.creep.moveTo(controller, {'visualizePathStyle': {
                'fill': 'transparent',
                'stroke': '#fff',
                'lineStyle': 'dashed',
                'strokeWidth': .15,
                'opacity': .1
            }, range: 0})
        if controller.reservation:
            if controller.reservation.ticksToEnd > 10:
                home = Game.getObjectById(self.creep.memory.home)
                if self.creep.name[10:11] == 1:
                    if not home.memory.need_stealer1s:
                        home.memory.need_stealer1s = 1
                if self.creep.name[10:11] == 2:
                    if not home.memory.need_stealer2s:
                        home.memory.need_stealer2s = 1

    def define_mine_to_steal(self):
        source = undefined
        if _.sum(self.creep.carry) <= 0:
            home = Game.getObjectById(self.creep.memory.home)
            my_creeps = _.filter(Game.creeps, lambda c: c.memory != undefined)
            reservators = _.filter(my_creeps,
                                   lambda c: c.memory.home == home.id and
                                             c.memory.job == ('reservator' + home.name[5:6]) and
                                             c.memory.controller != undefined)
            if reservators[0] != undefined:
                source = _(reservators[0].room.find(FIND_SOURCES_ACTIVE)) \
                    .sortBy(lambda s: s.amount).first()
                if source:
                    self.creep.memory.duty = 'stealing_mine'
                    self.creep.memory.target = source.id
        return source

    def stealing_mine(self):
        if _.sum(self.creep.carry) < self.creep.carryCapacity:
            source = Game.getObjectById(self.creep.memory.target)
            self.creep.moveTo(source, {'visualizePathStyle': {
                'fill': 'transparent',
                'stroke': '#fff',
                'lineStyle': 'dashed',
                'strokeWidth': .15,
                'opacity': .1
            }, range: 0})
            if self.creep.room == source.room:
                source = self.creep.pos.findClosestByPath(FIND_SOURCES_ACTIVE)
                if source:
                    self.creep.memory.target = source.id
                    if self.creep.pos.isNearTo(source):
                        result = self.creep.harvest(source)
                        if result != OK:
                            del self.creep.memory.target
                            self.define_target()
                            print("[{}] Unknown result from creep.harvest({}): {}".format(self.creep.name, 'mine',
                                                                                          result))
                    else:
                        self.creep.moveTo(source)
        else:
            self.define_target()

    def define_going_home(self):
        home = undefined
        if _.sum(self.creep.carry) > 0:
            home = Game.getObjectById(self.creep.memory.home)
            if home.room != self.creep.room:
                self.creep.memory.duty = 'going_home'
                self.creep.memory.target = home.id
        return home

    def going_home(self):
        home = Game.getObjectById(self.creep.memory.home)
        if self.creep.room != home.room:
            if _.sum(self.creep.carry) > 0:
                self.creep.moveTo(home, {'visualizePathStyle': {
                    'fill': 'transparent',
                    'stroke': '#fff',
                    'lineStyle': 'dashed',
                    'strokeWidth': .15,
                    'opacity': .1
                }, range: 0})
        else:
            self.define_target()

    def define_closest_to_transfer(self):
        target = undefined
        if self.creep.store[RESOURCE_ENERGY] > 0:
            target = _(self.creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER or
                                   s.structureType == STRUCTURE_STORAGE)) \
                .sortBy(lambda s: s.pos.getRangeTo(self.creep)).first()
            if target:
                self.creep.memory.duty = 'transferring_to_closest'
                self.creep.memory.target = target.id
        return target

    def transferring_to_closest(self):
        if self.creep.store[RESOURCE_ENERGY] > 0:
            target = _(self.creep.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: (s.structureType == STRUCTURE_CONTAINER or
                                   s.structureType == STRUCTURE_STORAGE)) \
                .sortBy(lambda s: (s.pos.getRangeTo(self.creep))).first()
            if target:
                is_close = self.creep.pos.isNearTo(target)
                if is_close:
                    result = self.creep.transfer(target, RESOURCE_ENERGY)
                    if result != OK:
                        del self.creep.memory.target
                        self.define_target()
                        print("[{}] Unknown result from creep.withdraw({}):"
                              " {}".format(self.creep.name, 'withdraw', result))
                else:
                    self.creep.moveTo(target, {'visualizePathStyle': {
                        'fill': 'transparent',
                        'stroke': '#fff',
                        'lineStyle': 'dashed',
                        'strokeWidth': .15,
                        'opacity': .1
                    }, range: 0})
            else:
                self.define_target()
        else:
            self.define_target()


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
