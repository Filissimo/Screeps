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
    create_extension(spawn)
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
    need_restart = True
    if spawn_memory.miners >= spawn_memory.need_miners - 1 and spawn_memory.lorries > 0:
        need_restart = False
    desired_job = ' no creeps needed to spawn.'
    if not need_restart:
        container_fullest = _(spawn.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: s.structureType == STRUCTURE_CONTAINER) \
            .sortBy(lambda s: s.store[RESOURCE_ENERGY]).last()
        container_emptiest = _(spawn.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: s.structureType == STRUCTURE_CONTAINER) \
            .sortBy(lambda s: s.store[RESOURCE_ENERGY]).first()
        if container_fullest:
            if container_fullest.store[RESOURCE_ENERGY] >= container_fullest.store.getCapacity():
                if spawn_memory.need_lorries <= spawn_memory.lorries:
                    spawn_memory.need_additional_lorries = spawn_memory.need_additional_lorries + 0.05
            if container_fullest.store[RESOURCE_ENERGY] >= container_fullest.store.getCapacity() * 0.9:
                if spawn_memory.need_lorries <= spawn_memory.lorries:
                    spawn_memory.need_additional_lorries = spawn_memory.need_additional_lorries + 0.01
            if container_fullest.store[RESOURCE_ENERGY] < container_fullest.store.getCapacity() * 0.5:
                if spawn_memory.need_lorries >= spawn_memory.lorries - 1:
                    spawn_memory.need_additional_lorries = spawn_memory.need_additional_lorries - 0.1
        if container_emptiest:
            if container_emptiest.store[RESOURCE_ENERGY] > container_emptiest.store.getCapacity() * 0.3:
                if spawn_memory.need_workers <= spawn_memory.workers:
                    spawn_memory.need_additional_workers = spawn_memory.need_additional_workers + 0.02
            if container_emptiest.store[RESOURCE_ENERGY] <= container_emptiest.store.getCapacity() * 0.3:
                if spawn_memory.need_workers >= spawn_memory.workers - 1.5:
                    spawn_memory.need_additional_workers = spawn_memory.need_additional_workers - 0.01
    sources = spawn.room.find(FIND_SOURCES)
    containers_near_mine = 0
    if not spawn_memory.need_starters:
        spawn_memory.need_starters = len(sources)
    need_starters = spawn_memory.need_starters
    for source in sources:
        container_near_mine = _.filter(source.pos.findInRange(FIND_STRUCTURES, 2),
                                       lambda s: (s.structureType == STRUCTURE_CONTAINER))
        # if len(container_near_mine) == 0:
        #     create_container(source)
        # else:
        containers_near_mine = containers_near_mine + len(container_near_mine)

        starters = spawn_memory.starters
        if need_restart:
            if source.energy > source.ticksToRegeneration * 10 or source.energy >= 2000:
                    need_starters = need_starters + 0.01
                    print('+ starters')
            if source.energy < source.ticksToRegeneration * 10:
                if need_starters >= starters - 2:
                    need_starters = need_starters - 0.03
                    print('- starters')
    if not need_restart:
        need_starters = 0
    spawn_memory.need_starters = round(need_starters, 2)

    if need_restart:
        worker_to_starter = _(spawn.room.find(FIND_MY_CREEPS)
                              .filter(lambda c: c.memory != undefined)
                              .filter(lambda c: c.memory.job == 'worker')).sample()
        if worker_to_starter:
            if spawn_memory.workers > 1:
                worker_to_starter.memory.job = 'starter'
                del worker_to_starter.memory.duty
                del worker_to_starter.memory.target

    if not need_restart:
        starter_to_worker = _(spawn.room.find(FIND_MY_CREEPS)
                              .filter(lambda c: c.memory != undefined)
                              .filter(lambda c: c.memory.job == 'starter' and
                                                c.memory.flag != 'BS' and
                                                c.store[RESOURCE_ENERGY] <= 0)).sample()
        if starter_to_worker:
            starter_to_worker.memory.job = 'worker'
            del starter_to_worker.memory.duty
            del starter_to_worker.memory.target

    spawn_jobs = ['defender', 'miner', 'lorry', 'worker', 'claimer', 'spawn_builder',
                  'reservator', 'stealer', 'starter']
    my_creeps = _.filter(Game.creeps, lambda c: c.memory != undefined)
    my_creeps_with_memory = _.filter(my_creeps, lambda c: c.memory.job != undefined)
    actual_spawn_builders = _.filter(my_creeps_with_memory,
                                     lambda c: c.memory.home == spawn.id and
                                               c.memory.flag == 'BS' and
                                               c.ticksToLive > 30)
    spawn_memory.spawn_builders = len(actual_spawn_builders)
    for job_name in spawn_jobs:
        creeps_filtered = _.filter(my_creeps_with_memory,
                                   lambda c: c.memory.home == spawn.id and c.memory.job == job_name and
                                             c.ticksToLive > 50)
        number_of_creeps_filtered = len(creeps_filtered)

        if job_name == 'defender':
            need_defenders = len(spawn.room.find(FIND_HOSTILE_CREEPS))
            spawn_memory.need_defenders = (need_defenders * 2) + 3
            spawn_memory.starters = number_of_creeps_filtered
            if spawn_memory.need_defenders > number_of_creeps_filtered:
                if spawn_memory.lorries >= spawn_memory.need_lorries:
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
            if not spawn_memory.need_additional_workers:
                spawn_memory.need_additional_workers = 0
            need_additional_workers = spawn_memory.need_additional_workers
            if not spawn_memory.need_additional_lorries:
                spawn_memory.need_additional_lorries = 0
            need_additional_lorries = spawn_memory.need_additional_lorries
            need_workers = 0
            if containers_near_mine > 0:
                need_workers = 1
            if spawn_memory.lorries > 0:
                need_workers = containers_near_mine
            need_lorries = 1
            if spawn_memory.miners == 0:
                need_lorries = 0
                need_additional_lorries = 0
            if spawn_memory.miners > 0:
                need_lorries = containers_near_mine
            spawn_memory.need_lorries = round((need_lorries + need_additional_lorries), 2)
            spawn_memory.need_workers = round((need_workers + need_additional_workers), 2)
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

        elif job_name == 'reservator':
            flags = Object.keys(Game.flags)
            for flag_name in flags:
                if flag_name[:6] == 'steal' + spawn.name[5:6]:
                    flag = Game.flags[flag_name]
                    flag_memory = flag.memory
                    spawn_memory.reservators = number_of_creeps_filtered
                    reservators_on_the_flag = _.sum(creeps_filtered, lambda r: r.memory == flag_name)
                    if 2 > reservators_on_the_flag:

                        # STOPPED HERE !!!

                        if creeps_filtered[0]:
                            controller = Game.getObjectById(creeps_filtered[0].memory.controller)
                            if controller:
                                if controller.reservation:
                                    if controller.reservation.ticksToEnd < 2000:
                                        desired_job = job_name
                                    if controller.reservation.ticksToEnd >= 2000:
                                        job_name == undefined
                                if controller.reservation is undefined:
                                    desired_job = job_name

        elif job_name == 'stealer':
            spawn_memory.stealers = number_of_creeps_filtered
            if spawn_memory.need_stealers > number_of_creeps_filtered:
                worker_to_stealer = _(spawn.room.find(FIND_MY_CREEPS)) \
                    .filter(lambda c: c.memory.job == 'worker' and
                                      c.store[RESOURCE_ENERGY] == 0 and
                                      c.store.getCapacity() >= 200).sample()
                if worker_to_stealer:
                    if spawn_memory.lorries >= spawn_memory.need_lorries:
                        if spawn_memory.workers >= spawn_memory.need_workers:
                            del worker_to_stealer.memory.duty
                            del worker_to_stealer.memory.target
                            worker_to_stealer.memory.job = 'stealer'
            if spawn_memory.need_stealers < number_of_creeps_filtered - 1:
                stealer_to_worker = _(spawn.room.find(FIND_MY_CREEPS)) \
                    .filter(lambda c: c.memory.job[:7] == 'stealer' and
                                      c.store[RESOURCE_ENERGY] == 0).sample()
                if stealer_to_worker:
                    if spawn_memory.workers >= spawn_memory.need_workers:
                        del stealer_to_worker.memory.duty
                        del stealer_to_worker.memory.target
                        stealer_to_worker.memory.job = 'worker'

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
                if spawn_memory.lorries >= spawn_memory.need_lorries:
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

    spawn.memory = spawn_memory

    print(spawn.name + ': desired job: ' + desired_job)

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
        for a in range(1, 10):
            if spawn.room.energyAvailable >= a * 200:
                desired_body.extend([WORK, CARRY, MOVE])
    elif job_name == 'worker':
        for a in range(1, 10):
            if spawn.room.energyCapacityAvailable >= a * 200:
                desired_body.extend([WORK, CARRY, MOVE])
    elif job_name == 'miner':
        if spawn.room.energyCapacityAvailable >= 400:
            desired_body.extend([WORK, WORK, WORK, CARRY, MOVE, MOVE])
    elif job_name == 'lorry':
        range_max = round((spawn.memory.need_lorries + 4) * 0.8)
        if range_max >= 7:
            range_max = 6
        for a in range(1, range_max):
            if spawn.room.energyCapacityAvailable >= a * 150:
                desired_body.extend([CARRY, CARRY, MOVE])
    elif job_name[:10] == 'reservator' or job_name == 'claimer':
        if spawn.room.energyCapacityAvailable >= 700:
            desired_body = [CLAIM, MOVE, MOVE]
    print('Final desired body: ' + str(desired_body))

    return desired_body


def create_extension(spawn):
    if len(spawn.room.find(FIND_CONSTRUCTION_SITES)) == 0:
        controller_lvl = spawn.room.controller.level
        extensions = _.filter(spawn.room.find(FIND_STRUCTURES), lambda s: s.structureType == STRUCTURE_EXTENSION)
        if controller_lvl == 2:
            if len(extensions) < 5:
                max_range = len(extensions) + 1
                verify_square_and_place_extension(spawn.pos)
                for extension in extensions:
                    verify_square_and_place_extension(extension.pos)
        elif controller_lvl > 2:
            if len(extensions) < (controller_lvl - 2) * 10:
                max_range = len(extensions) + 1
                verify_square_and_place_extension(spawn.pos)
                for extension in extensions:
                    verify_square_and_place_extension(extension.pos)


def verify_square_and_place_extension(position):
    semicircles = 1.3
    for circle in range(1, 3):
        for direction in range(1, 5):
            semicircles = semicircles + 0.5
            for semicircle in range(1, round(semicircles)):
                if direction == 1:
                    position.x = position.x + 1
                    position.y = position.y - 1
                    extension_placed = place_extension(position)
                    if extension_placed:
                        break
                if direction == 2:
                    position.x = position.x + 1
                    position.y = position.y + 1
                    extension_placed = place_extension(position)
                    if extension_placed:
                        break
                if direction == 3:
                    position.x = position.x - 1
                    position.y = position.y + 1
                    extension_placed = place_extension(position)
                    if extension_placed:
                        break
                if direction == 4:
                    position.x = position.x - 1
                    position.y = position.y - 1
                    extension_placed = place_extension(position)
                    if extension_placed:
                        break


def place_extension(position):
    extension_placed = False
    if 4 < position.x < 45 and 4 < position.y < 45:
        terrain = position.lookFor(LOOK_TERRAIN)
        structures = position.lookFor(LOOK_STRUCTURES)
        if terrain != 'wall' and len(structures) == 0:
            extensions = _.sum(position.findInRange(FIND_STRUCTURES, 1),
                               lambda s: s.structureType == STRUCTURE_EXTENSION or
                                         s.structureType == STRUCTURE_SPAWN)
            swamps = _.sum(position.findInRange(LOOK_TERRAIN, 3),
                           lambda t: t.type == 'swamp')
            if extensions > 0 and swamps == 0:
                position.createConstructionSite(STRUCTURE_EXTENSION)
                extension_placed = True
    return extension_placed


def create_container(source):
    print(source)
    if source.room.energyCapacityAvailable < 400:
        walkable_spots = []
        not_walls = _.filter(source.pos.findInRange(LOOK_TERRAIN, 1),
                             lambda t: t.type == "plain" or
                             t.type == 'swamp')
        if len(not_walls) < 2:
            road = source.pos.findInRange(LOOK_STRUCTURES, 1)[0]
            print(str(not_walls))
            if road:
                print(road.pos)
        else:
            for not_wall in not_walls:
                print(not_wall.pos)
        # i = 0
        # for walkable_spot in walkable_spots:
        #     i = i + 1
        #     walkable_spot.createFlag('spot' + str(i))



