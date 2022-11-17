from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def spawn_runner(spawn):
    job_name = creep_needed_to_spawn(spawn)
    if not spawn.spawning:
        if job_name:
            if Memory.Number_of_creep is undefined:
                Memory.Number_of_creep = 0
            number_of_creep = Memory.Number_of_creep
            desired_body = define_body(spawn, job_name)
            result = spawn.spawnCreep(desired_body,
                                      job_name + '-' + str(number_of_creep),
                                      {'memory': {'job': job_name, 'home': spawn.id}})
            if result == OK:
                print(str(desired_body) + ' - job: ' + job_name + ' - spawning.       Capacity: '
                      + spawn.room.energyCapacityAvailable)
                number_of_creep = number_of_creep + 1
                Memory.Number_of_creep = number_of_creep


def creep_needed_to_spawn(spawn):
    spawn_memory = spawn.memory
    desired_job = False
    spawn_memory.need_starters = False
    spawn_jobs = ['defender', 'miner', 'lorry', 'worker', 'starter',
                  'reservator1', 'reservator2', 'stealer1', 'stealer2']
    for job_name in spawn_jobs:
        my_creeps = _.filter(Game.creeps, lambda c: c.memory != undefined)
        my_creeps_with_memory = _.filter(my_creeps, lambda c: c.memory.job != undefined)
        creeps_filtered = _.filter(my_creeps_with_memory,
                                   lambda c: c.memory.home == spawn.id and c.memory.job == job_name and
                                             c.ticksToLive > 50)
        number_of_creeps_filtered = len(creeps_filtered)
        sources = spawn.room.find(FIND_SOURCES)
        containers_near_mine = 0
        container_fullest = _(spawn.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: s.structureType == STRUCTURE_CONTAINER) \
            .sortBy(lambda s: s.store[RESOURCE_ENERGY]).last()
        container_emptiest = _(spawn.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: s.structureType == STRUCTURE_CONTAINER) \
            .sortBy(lambda s: s.store[RESOURCE_ENERGY]).first()
        for source in sources:
            container_near_mine = _.sum(spawn.room.find(FIND_STRUCTURES),
                                        lambda s: (s.structureType == STRUCTURE_CONTAINER and
                                                   s.pos.inRangeTo(source, 2)))
            containers_near_mine = containers_near_mine + container_near_mine
        if job_name == 'defender':
            need_defenders = len(spawn.room.find(FIND_HOSTILE_CREEPS))
            spawn_memory.need_defenders = (need_defenders * 2) + 2
            spawn_memory.starters = number_of_creeps_filtered
            if spawn_memory.need_defenders > number_of_creeps_filtered:
                desired_job = job_name
        elif job_name == 'miner':
            spawn_memory.miners = number_of_creeps_filtered
            need_miners = containers_near_mine * 2
            spawn_memory.need_miners = need_miners
            need_starters = len(sources) * 4
            if not spawn_memory.need_additional_workers:
                spawn_memory.need_additional_workers = 0
            need_additional_workers = spawn_memory.need_additional_workers
            if not spawn_memory.need_additional_lorries:
                spawn_memory.need_additional_lorries = 0
            need_additional_lorries = spawn_memory.need_additional_lorries
            if number_of_creeps_filtered > 0:
                need_starters = 0
            need_workers = 0
            if containers_near_mine > 0:
                need_workers = 1
            if spawn_memory.lorries > 0:
                need_workers = containers_near_mine
            if container_fullest:
                if container_fullest.store[RESOURCE_ENERGY] >= container_fullest.store.getCapacity() * 0.7:
                    if spawn_memory.need_lorries <= spawn_memory.lorries:
                        need_additional_lorries = need_additional_lorries + 0.01
                if container_fullest.store[RESOURCE_ENERGY] < container_fullest.store.getCapacity() * 0.7:
                    if spawn_memory.need_lorries >= spawn_memory.lorries:
                        need_additional_lorries = need_additional_lorries - 0.05
            if container_emptiest:
                if container_emptiest.store[RESOURCE_ENERGY] > container_emptiest.store.getCapacity() * 0.5:
                    if spawn_memory.need_workers <= spawn_memory.workers:
                        need_additional_workers = need_additional_workers + 0.01
                if container_emptiest.store[RESOURCE_ENERGY] <= container_emptiest.store.getCapacity() * 0.3:
                    if spawn_memory.need_workers >= spawn_memory.workers:
                        need_additional_workers = need_additional_workers - 0.01
            need_lorries = 0
            if spawn_memory.miners > 0:
                need_lorries = 1
            if containers_near_mine > 0:
                need_lorries = containers_near_mine
            spawn_memory.need_lorries = round((need_lorries + need_additional_lorries), 2)
            spawn_memory.need_workers = round((need_workers + need_additional_workers), 2)
            spawn_memory.need_starters = need_starters
            spawn_memory.need_additional_lorries = need_additional_lorries
            spawn_memory.need_additional_workers = need_additional_workers
            if need_miners > number_of_creeps_filtered:
                desired_job = job_name
        elif job_name == 'starter':
            spawn_memory.starters = number_of_creeps_filtered
            if spawn_memory.need_starters > number_of_creeps_filtered:
                desired_job = job_name
        elif job_name == 'lorry':
            spawn_memory.lorries = number_of_creeps_filtered
            if spawn_memory.need_lorries > number_of_creeps_filtered:
                if spawn_memory.miners >= need_miners:
                    desired_job = job_name

        elif job_name == 'worker':
            spawn_memory.workers = number_of_creeps_filtered
            if spawn_memory.need_workers > number_of_creeps_filtered:
                if spawn_memory.lorries >= len(sources):
                    if spawn_memory.miners >= (containers_near_mine * 2):
                        desired_job = job_name

        elif job_name == 'reservator1':
            if spawn_memory.steal1:
                spawn_memory.reservator1s = number_of_creeps_filtered
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
            if spawn_memory.steal2:
                spawn_memory.reservator2s = number_of_creeps_filtered
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
            spawn_memory.stealer1s = number_of_creeps_filtered
            if spawn_memory.need_stealer1s > number_of_creeps_filtered:
                worker_to_stealer = _(spawn.room.find(FIND_MY_CREEPS)) \
                    .filter(lambda c: c.memory.job == 'worker' and
                                      c.store[RESOURCE_ENERGY] == 0).sample()
                if worker_to_stealer:
                    del worker_to_stealer.memory.duty
                    del worker_to_stealer.memory.target
                    worker_to_stealer.memory.job = 'stealer1'

        elif job_name == 'stealer2':
            spawn_memory.stealer2s = number_of_creeps_filtered
            if spawn_memory.need_stealer2s > number_of_creeps_filtered:
                worker_to_stealer = _(spawn.room.find(FIND_MY_CREEPS)) \
                    .filter(lambda c: c.memory.job == 'worker' and
                                      c.store[RESOURCE_ENERGY] == 0).sample()
                if worker_to_stealer:
                    del worker_to_stealer.memory.duty
                    del worker_to_stealer.memory.target
                    worker_to_stealer.memory.job = 'stealer2'

    if spawn_memory.lorries == 0 or spawn_memory.miners == 0:
        worker_to_starter = _(spawn.room.find(FIND_MY_CREEPS)
                              .filter(lambda c: c.memory != undefined)
                              .filter(lambda c: c.memory.job == 'worker')).sample()
        if worker_to_starter:
            if spawn_memory.workers > 1:
                worker_to_starter.memory.job = 'starter'
                del worker_to_starter.memory.duty
                del worker_to_starter.memory.target

    if spawn_memory.lorries > 0 and spawn_memory.miners > 0:
        starter_to_worker = _(spawn.room.find(FIND_MY_CREEPS)
                              .filter(lambda c: c.memory != undefined)
                              .filter(lambda c: c.memory.job == 'starter')).sample()
        if starter_to_worker:
            starter_to_worker.memory.job = 'worker'
            del starter_to_worker.memory.duty
            del starter_to_worker.memory.target
    spawn.memory = spawn_memory

    return desired_job


def define_body(spawn, job_name):
    desired_body = []
    if job_name == 'defender':
        for a in range(1, 10):
            if spawn.room.energyCapacityAvailable >= a * 260:
                desired_body.extend([TOUGH])
        for a in range(1, 10):
            if spawn.room.energyCapacityAvailable >= a * 260:
                desired_body.extend([RANGED_ATTACK, MOVE, MOVE])
    elif job_name == 'starter':
        desired_body = [WORK, CARRY, MOVE]
    elif job_name == 'worker':
        for a in range(1, 10):
            if spawn.room.energyCapacityAvailable >= a * 200:
                desired_body.extend([WORK, CARRY, MOVE])
    elif job_name == 'miner':
        if spawn.room.energyCapacityAvailable >= 550:
            desired_body.extend([WORK, WORK, WORK, WORK, CARRY, MOVE, MOVE])
    elif job_name == 'lorry':
        range_max = spawn.memory.need_lorries + 1
        for a in range(0, range_max):
            if spawn.room.energyCapacityAvailable >= a * 150:
                desired_body.extend([CARRY, CARRY, MOVE])
    elif job_name[:10] == 'reservator':
        if spawn.room.energyCapacityAvailable >= 700:
            desired_body = [CLAIM, MOVE, MOVE]
    return desired_body
