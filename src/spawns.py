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
            if creep_to_renew.pos.isNearTo(spawn) and creep_to_renew.ticksToLive < 1000:
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
    if spawn_memory.miners >= spawn_memory.need_miners - 1 and spawn_memory.miners >= 2 and spawn_memory.lorries > 0:
        need_restart = False
    desired_job = undefined
    sources = spawn.room.find(FIND_SOURCES)
    if not need_restart:
        container_fullest = _(spawn.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: s.structureType == STRUCTURE_CONTAINER) \
            .sortBy(lambda s: s.store[RESOURCE_ENERGY]).last()
        container_emptiest = _(spawn.room.find(FIND_STRUCTURES)) \
            .filter(lambda s: s.structureType == STRUCTURE_CONTAINER) \
            .sortBy(lambda s: s.store[RESOURCE_ENERGY]).first()
        if container_fullest and container_emptiest:
            if container_fullest.store[RESOURCE_ENERGY] - container_emptiest.store[RESOURCE_ENERGY] > 700:
                if spawn_memory.need_lorries <= spawn_memory.lorries + 1:
                    spawn_memory.need_additional_lorries = spawn_memory.need_additional_lorries + 0.02
            elif container_fullest.store[RESOURCE_ENERGY] >= container_fullest.store.getCapacity():
                if spawn_memory.need_lorries <= spawn_memory.lorries + 1:
                    spawn_memory.need_additional_lorries = spawn_memory.need_additional_lorries + 0.02
            else:
                if spawn_memory.lorries + 1 >= spawn_memory.need_lorries > len(sources) + 0.5:
                    spawn_memory.need_additional_lorries = spawn_memory.need_additional_lorries - 0.05
            if container_emptiest.store[RESOURCE_ENERGY] > container_emptiest.store.getCapacity() * 0.35:
                if spawn_memory.need_workers <= spawn_memory.workers + 1:
                    spawn_memory.need_additional_workers = spawn_memory.need_additional_workers + 0.01
            if container_emptiest.store[RESOURCE_ENERGY] <= container_emptiest.store.getCapacity() * 0.3:
                if spawn_memory.need_workers >= spawn_memory.workers - 1.5:
                    spawn_memory.need_additional_workers = spawn_memory.need_additional_workers - 0.02
    containers_near_mine = 0
    if not spawn_memory.need_starters:
        spawn_memory.need_starters = len(sources)
    need_starters = spawn_memory.need_starters
    enough_lorries = False
    if spawn_memory.lorries >= len(sources) + 1:
        enough_lorries = True
    for source in sources:
        container_near_mine = _.filter(source.pos.findInRange(FIND_STRUCTURES, 2),
                                       lambda s: (s.structureType == STRUCTURE_CONTAINER))

        if len(container_near_mine) == 0:
            create_container(source)
        else:
            containers_near_mine = containers_near_mine + len(container_near_mine)

        starters = spawn_memory.starters
        if need_restart:
            if source.energy > source.ticksToRegeneration * 15 or source.energy >= 2800:
                need_starters = need_starters + 0.01
            if source.energy < source.ticksToRegeneration * 10:
                if need_starters >= starters - 2:
                    need_starters = need_starters - 0.03
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
                                                c.store[RESOURCE_ENERGY] <= 0)).sample()
        if starter_to_worker:
            starter_to_worker.memory.job = 'worker'
            del starter_to_worker.memory.duty
            del starter_to_worker.memory.target

    defended = False
    if spawn_memory.defenders >= 2:
        defended = True

    spawn_jobs = ['defender', 'miner', 'lorry', 'worker', 'claimer', 'spawn_builder',
                  'reservator', 'stealer', 'starter', 'healer', 'truck']
    my_creeps = _.filter(Game.creeps, lambda c: c.memory != undefined)
    my_creeps_with_memory = _.filter(my_creeps, lambda c: c.memory.job != undefined)
    actual_spawn_builders = _.filter(my_creeps_with_memory,
                                     lambda c: c.memory.home == spawn.id and
                                               c.memory.flag == 'BS' and
                                               c.ticksToLive > 30)
    flag_bs = Game.flags['BS']
    if flag_bs:
        flag_bs.memory.spawn_builders = len(actual_spawn_builders)
    for job_name in spawn_jobs:
        creeps_filtered = _.filter(my_creeps_with_memory,
                                   lambda c: c.memory.home == spawn.id and c.memory.job == job_name and
                                             c.ticksToLive > 70)
        number_of_creeps_filtered = len(creeps_filtered)

        if job_name == 'defender':
            need_defenders = len(spawn.room.find(FIND_HOSTILE_CREEPS,
                                                 {'filter': lambda e: e.owner.username != 'rep71Le'}))
            spawn_memory.need_defenders = need_defenders + 2
            spawn_memory.defenders = number_of_creeps_filtered
            if spawn_memory.need_defenders > number_of_creeps_filtered:
                desired_job = job_name
        elif job_name == 'healer':
            spawn_memory.healers = number_of_creeps_filtered
            if spawn_memory.healers < spawn_memory.defenders:
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
            need_lorries = 3
            if spawn_memory.miners == 0:
                need_lorries = 0
                need_additional_lorries = 0
            if spawn_memory.miners > 0:
                need_lorries = 3
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
            if defended and not need_restart:
                spawn_memory.workers = number_of_creeps_filtered
                if spawn_memory.need_workers > number_of_creeps_filtered:
                    if enough_lorries:
                        desired_job = job_name

        elif job_name == 'reservator':
            if not need_restart and defended:
                if enough_lorries:
                    flags = Object.keys(Game.flags)
                    for flag_name in flags:
                        if flag_name[:6] == 'Steal' + spawn.name[5:6]:
                            flag = Game.flags[flag_name]
                            flag_memory = flag.memory
                            reservators_on_the_flag = _.filter(creeps_filtered, lambda c: c.memory.flag == flag_name)
                            flag_memory.reservators = len(reservators_on_the_flag)
                            if flag.room:
                                if flag_memory.need_reservators > len(reservators_on_the_flag):
                                    if flag_memory.reservation < 2000:
                                        desired_job = job_name
                            flag.memory = flag_memory

        elif job_name == 'stealer':
            if defended:
                for flag_name in Object.keys(Game.flags):
                    if flag_name[:6] == 'Steal' + spawn.name[5:6]:
                        flag = Game.flags[flag_name]
                        flag_memory = flag.memory
                        stealers_on_the_flag = _.filter(creeps_filtered, lambda c: c.memory.flag == flag_name)
                        flag.memory.stealers = len(stealers_on_the_flag)
                        if flag_memory.need_stealers > flag_memory.stealers \
                                and spawn_memory.workers > spawn_memory.need_workers - 0.1:
                            worker_to_stealer = _(spawn.room.find(FIND_MY_CREEPS)) \
                                .filter(lambda c: c.memory.job == 'worker' and
                                                  c.store[RESOURCE_ENERGY] == 0 and
                                                  c.store.getCapacity() >= 150).sample()
                            if worker_to_stealer:
                                del worker_to_stealer.memory.duty
                                del worker_to_stealer.memory.path
                                del worker_to_stealer.memory.target
                                worker_to_stealer.memory.job = 'stealer'
                                worker_to_stealer.memory.flag = flag_name
                        if flag.room:
                            if flag_memory.need_stealers < flag_memory.stealers - 1:
                                stealer_to_worker = _(spawn.room.find(FIND_MY_CREEPS)) \
                                    .filter(lambda s: s.store[RESOURCE_ENERGY] <= 0 and
                                                      s.memory.job == 'stealer') \
                                    .sample()
                                if stealer_to_worker:
                                    del stealer_to_worker.memory.duty
                                    del stealer_to_worker.memory.target
                                    del stealer_to_worker.memory.flag
                                    del stealer_to_worker.memory.path
                                    stealer_to_worker.memory.job = 'worker'

        elif job_name == 'truck':
            if not need_restart and defended and enough_lorries:
                for flag_name in Object.keys(Game.flags):
                    if flag_name[:7] == 'Energy' + spawn.name[5:6]:
                        flag = Game.flags[flag_name]
                        flag_memory = flag.memory
                        flag_memory.trucks = number_of_creeps_filtered
                        if 3 > number_of_creeps_filtered:
                            desired_job = job_name

        elif job_name == 'claimer':
            flag_name = Memory.claim
            spawn_memory.claimers = number_of_creeps_filtered
            if flag_name:
                if Memory.building_spawn:
                    flag = Game.flags[flag_name]
                    if flag:
                        flag.pos.createFlag('BS')
                        flag.remove()
                        del Memory.claim
                else:
                    if number_of_creeps_filtered <= 0:
                        desired_job = job_name

        elif job_name == 'spawn_builder':
            if enough_lorries and defended:
                flag = Game.flags['BS']
                if flag:
                    flag_memory = flag.memory
                    if not flag_memory.need_spawn_builders:
                        flag_memory.need_spawn_builders = 3
                    if flag_memory.need_spawn_builders > flag_memory.spawn_builders:
                        if spawn_memory.miners >= spawn_memory.need_miners:
                            if spawn_memory.workers > 0:
                                worker_to_sb = _(spawn.room.find(FIND_MY_CREEPS)) \
                                    .filter(lambda c: c.memory.job == 'worker' and
                                                      c.store[RESOURCE_ENERGY] <= 0 and
                                                      c.store.getCapacity() >= 200) \
                                    .sample()
                                if worker_to_sb:
                                    del worker_to_sb.memory.duty
                                    del worker_to_sb.memory.target
                                    worker_to_sb.memory.job = 'spawn_builder'
                                    worker_to_sb.memory.flag = 'BS'

    spawn.memory = spawn_memory

    print('          ' + spawn.name + ': desired job: ' + desired_job)

    return desired_job


def define_body(spawn, job_name):
    desired_body = []
    if job_name == 'defender':
        for a in range(1, 5):
            if spawn.room.energyAvailable >= a * 260:
                desired_body.extend([TOUGH])
        for a in range(1, 5):
            if spawn.room.energyAvailable >= a * 260:
                desired_body.extend([RANGED_ATTACK, MOVE, MOVE])
    if job_name == 'healer':
        for a in range(1, 4):
            if spawn.room.energyAvailable >= a * 360:
                desired_body.extend([TOUGH])
        for a in range(1, 4):
            if spawn.room.energyAvailable >= a * 360:
                desired_body.extend([HEAL, MOVE, MOVE])
    elif job_name == 'starter':
        for a in range(1, 6):
            if spawn.room.energyAvailable >= a * 200:
                desired_body.extend([WORK, CARRY, MOVE])
    elif job_name == 'worker':
        for a in range(1, 6):
            if spawn.room.energyCapacityAvailable >= a * 200:
                desired_body.extend([WORK, CARRY, MOVE])
    elif job_name == 'miner':
        if spawn.room.energyCapacityAvailable >= 400:
            desired_body.extend([WORK, WORK, WORK, CARRY, MOVE, MOVE])
    elif job_name == 'lorry':
        for a in range(1, 5):
            if spawn.room.energyAvailable >= a * 150:
                desired_body.extend([CARRY, CARRY, MOVE])
    elif job_name == 'truck':
        for a in range(1, 11):
            if spawn.room.energyCapacityAvailable >= a * 150:
                desired_body.extend([CARRY, CARRY, MOVE])
    elif job_name[:10] == 'reservator' or job_name == 'claimer':
        if spawn.room.energyCapacityAvailable >= 700:
            desired_body = [CLAIM, MOVE, MOVE]

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
        roads = _.filter(position.lookFor(LOOK_STRUCTURES), lambda s: s.structureType == STRUCTURE_ROAD)
        if terrain != 'wall' and len(roads) > 0:
            position.createFlag('dc' + roads[0].id)
            extension_placed = True
        elif terrain != 'wall' and len(structures) == 0:
            extensions = _.sum(position.findInRange(FIND_STRUCTURES, 1),
                               lambda s: s.structureType == STRUCTURE_EXTENSION or
                                         s.structureType == STRUCTURE_SPAWN)
            swamps = _.sum(position.findInRange(LOOK_TERRAIN, 3),
                           lambda t: t.type == 'swamp')
            if extensions > 0 and swamps == 0:
                position.createConstructionSite(STRUCTURE_EXTENSION)
                extension_placed = True
    return extension_placed


def look_for_spots_near_position(position):
    list_of_spots = []
    circle = '12334411'
    for spot in circle:
        if spot == 1:
            position.x = position.x + 1
            list_of_spots.append({position: position.lookFor(LOOK_TERRAIN)})
        elif spot == 2:
            position.y = position.y + 1
            list_of_spots.append({position: position.lookFor(LOOK_TERRAIN)})
        elif spot == 3:
            position.x = position.x - 1
            list_of_spots.append({position: position.lookFor(LOOK_TERRAIN)})
        elif spot == 4:
            position.y = position.y - 1
            list_of_spots.append({position: position.lookFor(LOOK_TERRAIN)})
    return list_of_spots


def create_container(source):
    if source.room.energyCapacityAvailable >= 400:
        if len(source.room.find(FIND_CONSTRUCTION_SITES)) == 0:
            flag = _(source.pos.findInRange(FIND_FLAGS, 2)).filter(lambda f: f.name[:3] == 'con').sample()
            if flag:
                flag.pos.createConstructionSite(STRUCTURE_CONTAINER)
                flag.remove()

        # path = source.pos.findPathTo(spawn, {'ignoreCreeps': True})
        # if len(path):
        #     print(path[1].x + ' ' + path[1].y)
        #     container = spawn.pos
        #     container.x = path[1].x
        #     container.y = path[1].y
        #     place_near_source = container
        #     print(str(source.pos.x) + ' ' + str(container.x))
        #     if source.pos.x - container.x == 2:
        #         place_near_source.x = container.x + 1
        #         if place_near_source.lookFor(LOOK_TERRAIN) != 'wall':
        #             if container.y != source.pos.y:
        #                 place_near_source.y = source.pos.y
        #                 if place_near_source.lookFor(LOOK_TERRAIN) != 'wall':
        #                     container.createFlag('Container')
        #                 else:
        #                     if container.y < source.pos.y:
        #                         place_near_source.y = source.pos.y + 1
        #                         if place_near_source.lookFor(LOOK_TERRAIN) != 'wall':
        #                             container.y = source.pos.y
        #                             container.createFlag('Container')
        #                     if container.y > source.pos.y:
        #                         place_near_source.y = source.pos.y - 1
        #                         if place_near_source.lookFor(LOOK_TERRAIN) != 'wall':
        #                             container.y = source.pos.y
        #                             container.createFlag('Container')
        #         else:
        #             place_near_source.y = source.pos.y
        #             if place_near_source.lookFor(LOOK_TERRAIN) != 'wall':
        #                 if container.y < source.pos.y:
        #                     place_near_source.y = source.pos.y + 1
        #                     if place_near_source.lookFor(LOOK_TERRAIN) != 'wall':
        #                         container.y = source.pos.y
        #                         container.createFlag('Container')
        #                 if container.y > source.pos.y:
        #                     place_near_source.y = source.pos.y - 1
        #                     if place_near_source.lookFor(LOOK_TERRAIN) != 'wall':
        #                         container.y = source.pos.y
        #                         container.createFlag('Container')

        # elif source.pos.x - path[1].pos.x == - 2:
        #     place1.x = place1.x + 1
        #     place2.x = place2.x - 1
        #     if place1 == place2:
        #         place2.y = place2.y + 1
        #         if place2.lookFor(LOOK_TERRAIN).type == 'wall':
        #             place2.y = place2.y - 2
        # elif source.pos.y - path[1].pos.y == 2:
        #     place1.y = place1.y - 1
        #     place2.y = place2.y + 1
        #     if place1 == place2:
        #         place2.x = place2.x + 1
        #         if place2.lookFor(LOOK_TERRAIN).type == 'wall':
        #             place2.x = place2.x - 2
        # elif source.pos.y - path[1].pos.y == - 2:
        #     place1.y = place1.y + 1
        #     place2.y = place2.y - 1
        #     if place1 == place2:
        #         place2.x = place2.x + 1
        #         if place2.lookFor(LOOK_TERRAIN).type == 'wall':
        #             place2.x = place2.x - 2
