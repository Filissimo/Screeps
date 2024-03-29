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
        creep_to_renew = spawn.pos.findClosestByRange(FIND_MY_CREEPS)
        if creep_to_renew:
            if creep_to_renew.pos.isNearTo(spawn) and creep_to_renew.ticksToLive < 300:
                spawn.renewCreep(creep_to_renew)
                print(creep_to_renew.name + ' renewed: ' + creep_to_renew.ticksToLive)
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
    spawn_jobs = ['defender', 'miner', 'lorry', 'worker', 'claimer', 'spawn_builder',
                  'reservator1', 'reservator2', 'stealer1', 'stealer2', 'starter']
    for job_name in spawn_jobs:
        my_creeps = _.filter(Game.creeps, lambda c: c.memory != undefined)
        my_creeps_with_memory = _.filter(my_creeps, lambda c: c.memory.job != undefined)
        creeps_filtered = _.filter(my_creeps_with_memory,
                                   lambda c: c.memory.home == spawn.id and c.memory.job == job_name and
                                             c.ticksToLive > 50)
        actual_spawn_builders = _.filter(my_creeps_with_memory,
                                         lambda c: c.memory.home == spawn.id and
                                                   c.memory.flag == 'BS' and
                                                   c.ticksToLive > 50)
        spawn_memory.spawn_builders = len(actual_spawn_builders)
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
            spawn_memory.need_defenders = (need_defenders * 2) + 3
            spawn_memory.starters = number_of_creeps_filtered
            if spawn_memory.need_defenders > number_of_creeps_filtered:
                if spawn_memory.lorries >= spawn_memory.need_lorries or spawn_memory.lorries <= 0:
                    if spawn_memory.workers >= spawn_memory.need_workers:
                        desired_job = job_name
        elif job_name == 'starter':
            spawn_memory.starters = number_of_creeps_filtered
            if spawn_memory.need_starters > number_of_creeps_filtered:
                desired_job = job_name
        elif job_name == 'miner':
            spawn_memory.miners = number_of_creeps_filtered
            need_miners = containers_near_mine * 2
            spawn_memory.need_miners = need_miners
            need_starters = len(sources) * 3
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
                if container_fullest.store[RESOURCE_ENERGY] >= container_fullest.store.getCapacity() * 0.9:
                    if spawn_memory.need_lorries <= spawn_memory.lorries:
                        need_additional_lorries = need_additional_lorries + 0.01
                if container_fullest.store[RESOURCE_ENERGY] < container_fullest.store.getCapacity() * 0.9:
                    if spawn_memory.need_lorries >= spawn_memory.lorries - 1.5:
                        need_additional_lorries = need_additional_lorries - 0.05
            if container_emptiest:
                if container_emptiest.store[RESOURCE_ENERGY] > container_emptiest.store.getCapacity() * 0.3:
                    if spawn_memory.need_workers <= spawn_memory.workers:
                        need_additional_workers = need_additional_workers + 0.01
                if container_emptiest.store[RESOURCE_ENERGY] <= container_emptiest.store.getCapacity() * 0.3:
                    if spawn_memory.need_workers >= spawn_memory.workers - 1.5:
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
        elif job_name == 'lorry':
            spawn_memory.lorries = number_of_creeps_filtered
            if spawn_memory.need_lorries > number_of_creeps_filtered:
                desired_job = job_name

        elif job_name == 'worker':
            spawn_memory.workers = number_of_creeps_filtered
            if spawn_memory.need_workers > number_of_creeps_filtered:
                if spawn_memory.lorries >= spawn_memory.need_lorries or spawn_memory.lorries <= 0:
                    if spawn_memory.miners >= spawn_memory.need_miners:
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
                                      c.store[RESOURCE_ENERGY] == 0 and
                                      c.store.getCapacity() >= 200).sample()
                if worker_to_stealer:
                    if spawn_memory.lorries >= spawn_memory.need_lorries or spawn_memory.lorries <= 0:
                        if spawn_memory.workers >= spawn_memory.need_workers:
                            del worker_to_stealer.memory.duty
                            del worker_to_stealer.memory.target
                            worker_to_stealer.memory.job = 'stealer1'
            if spawn_memory.need_stealer1s < number_of_creeps_filtered - 1:
                stealer_to_worker = _(spawn.room.find(FIND_MY_CREEPS)) \
                    .filter(lambda c: c.memory.job[:7] == 'stealer' and
                                      c.store[RESOURCE_ENERGY] == 0).sample()
                if stealer_to_worker:
                    if spawn_memory.workers >= spawn_memory.need_workers:
                        del stealer_to_worker.memory.duty
                        del stealer_to_worker.memory.target
                        stealer_to_worker.memory.job = 'worker'

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

        elif job_name == 'claimer':
            flag_name = Memory.claim
            spawn_memory.claimers = number_of_creeps_filtered
            if flag_name:
                if flag_name[5:6] == spawn.name[5:6]:
                    if Memory.building_spawn:
                        if spawn_memory.need_spawn_builders:
                            flag = Game.flags[flag_name]
                            flag.pos.createFlag('BS')
                            flag.remove()
                            del Memory.claim
                        else:
                            spawn_memory.need_spawn_builders = 1
                    else:
                        if number_of_creeps_filtered <= 0:
                            desired_job = job_name
        elif job_name == 'spawn_builder':
            if spawn_memory.need_spawn_builders > spawn_memory.spawn_builders:
                if spawn_memory.lorries >= spawn_memory.need_lorries or spawn_memory.lorries <= 0:
                    if spawn_memory.miners >= spawn_memory.need_miners:
                        if spawn_memory.workers >= spawn_memory.need_workers:
                            worker_to_sb = _(spawn.room.find(FIND_MY_CREEPS)) \
                                .filter(lambda c: c.memory.job == 'worker' and
                                                  c.store[RESOURCE_ENERGY] >= c.store.getCapacity() and
                                                  c.store.getCapacity >= 200).sample()
                            if worker_to_sb:
                                del worker_to_sb.memory.duty
                                del worker_to_sb.memory.target
                                worker_to_sb.memory.job = 'spawn_builder'
                                worker_to_sb.memory.flag = 'BS'
            if spawn_memory.need_spawn_builders <= spawn_memory.spawn_builders:
                sb_toWorker = _(actual_spawn_builders) \
                    .filter(lambda c: c.store[RESOURCE_ENERGY] <= 0 and
                            c.memory.target == undefined).sample()
                if sb_toWorker:
                    del sb_toWorker.memory.duty
                    del sb_toWorker.memory.target
                    sb_toWorker.memory.job = 'worker'
                    del sb_toWorker.memory.flag

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
                              .filter(lambda c: c.memory.job == 'starter' and
                                                c.memory.flag != 'BS')).sample()
        if starter_to_worker:
            starter_to_worker.memory.job = 'worker'
            del starter_to_worker.memory.duty
            del starter_to_worker.memory.target
    spawn.memory = spawn_memory

    return desired_job


def define_body(spawn, job_name):
    desired_body = []
    if job_name == 'defender':
        for a in range(1, 3):
            if spawn.room.energyCapacityAvailable >= a * 260:
                desired_body.extend([TOUGH])
        for a in range(1, 4):
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
        range_max = round(spawn.memory.need_lorries + 1)
        if range_max >= 7:
            range_max = 6
        for a in range(0, range_max):
            if spawn.room.energyAvailable >= a * 150:
                desired_body.extend([CARRY, CARRY, MOVE])
    elif job_name[:10] == 'reservator' or job_name == 'claimer':
        if spawn.room.energyCapacityAvailable >= 700:
            desired_body = [CLAIM, MOVE, MOVE]
    return desired_body
