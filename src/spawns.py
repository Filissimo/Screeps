from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def run_links(spawn):
    links = _.filter(spawn.room.find(FIND_STRUCTURES), lambda s: s.structureType == STRUCTURE_LINK)
    if len(links) > 1:
        sorted_links = _.sortBy(links, lambda l: l.store[RESOURCE_ENERGY])
        if sorted_links[len(sorted_links) - 1].cooldown == 0 and sorted_links[0].cooldown < 10:
            if sorted_links[len(sorted_links) - 1].store[RESOURCE_ENERGY] \
                    > sorted_links[0].store[RESOURCE_ENERGY] + 300:
                amount_to_transfer = (sorted_links[len(sorted_links) - 1].store[RESOURCE_ENERGY]
                                      - sorted_links[0].store[RESOURCE_ENERGY])
                sorted_links[len(sorted_links) - 1].transferEnergy(sorted_links[0], round(amount_to_transfer))


def spawning_creep(spawn, job_name, flag_name):
    if not spawn.spawning:
        creep_to_renew = spawn.pos.findClosestByRange(FIND_MY_CREEPS)
        if creep_to_renew:
            if creep_to_renew.pos.isNearTo(spawn) and creep_to_renew.ticksToLive < 1000:
                spawn.renewCreep(creep_to_renew)
        if job_name:
            if Memory.Number_of_creep is undefined:
                Memory.Number_of_creep = 0
            number_of_creep = Memory.Number_of_creep
            desired_body = define_body(spawn, job_name)
            result = spawn.spawnCreep(desired_body,
                                      job_name + '-' + str(number_of_creep),
                                      {'memory': {'job': job_name, 'home': spawn.id, 'flag': flag_name}})
            if result == OK:
                print(str(desired_body) + ' - job: ' + job_name + ' - spawning.       Capacity: '
                      + spawn.room.energyCapacityAvailable)
                number_of_creep = number_of_creep + 1
                Memory.Number_of_creep = number_of_creep


def spawn_runner(spawn):
    run_links(spawn)
    create_extension(spawn)
    spawn_memory = spawn.memory
    need_restart = True
    if spawn_memory.miners >= spawn_memory.need_miners - 1 and spawn_memory.miners >= 1 and spawn_memory.lorries > 0:
        need_restart = False
    desired_job = undefined
    sources = spawn.room.find(FIND_SOURCES)
    if not need_restart:
        containers = _.filter(spawn.room.find(FIND_STRUCTURES),
                              lambda s: s.structureType == STRUCTURE_CONTAINER
                                        or s.structureType == STRUCTURE_LINK)
        container_fullest = _(containers) \
            .sortBy(lambda s: s.store[RESOURCE_ENERGY]).last()
        total_capacity = 0
        total_energy = 0
        for container in containers:
            total_capacity = total_capacity \
                             + container.store[RESOURCE_ENERGY] \
                             + container.store.getFreeCapacity(RESOURCE_ENERGY)
            total_energy = total_energy + container.store[RESOURCE_ENERGY]

        if containers:
            if not spawn_memory.need_workers:
                spawn_memory.need_workers = 1
            need_workers = spawn_memory.need_workers
            if total_capacity / total_energy > 1.5:
                if need_workers > 2:
                    need_workers = need_workers - 0.001
            else:
                need_workers = need_workers + 0.01
            storage = _(spawn.room.find(FIND_STRUCTURES)) \
                .filter(lambda s: s.structureType == STRUCTURE_STORAGE).sample()
            if storage:
                if storage.store.getFreeCapacity() < storage.store.getCapacity() / 2:
                    if need_workers < 10:
                        need_workers = need_workers + 0.005
            spawn_memory.need_workers = need_workers
            need_lorries = spawn_memory.need_lorries
            if container_fullest.store.getFreeCapacity(RESOURCE_ENERGY) * 4 \
                    < container_fullest.store[RESOURCE_ENERGY] \
                    and container_fullest.structureType == STRUCTURE_CONTAINER:
                need_lorries = need_lorries + 0.01
            elif container_fullest.store.getFreeCapacity(RESOURCE_ENERGY) == 0:
                need_lorries = need_lorries + 0.01
            else:
                if need_lorries > 1:
                    need_lorries = need_lorries - 0.001
            if spawn.spawning and spawn.room.energyAvailable >= spawn.room.energyCapacityAvailable:
                if need_lorries > 1:
                    need_lorries = need_lorries - 0.02
            spawn_memory.need_lorries = need_lorries

        # print('                ' + spawn.name + '. Containers and links: '
        #       + '    ' + total_capacity + '/' + total_energy)

    mines_near_container = 0
    if not spawn_memory.need_starters:
        spawn_memory.need_starters = len(sources)
    need_starters = spawn_memory.need_starters
    enough_miners = False
    if spawn_memory.miners >= spawn_memory.need_miners:
        enough_miners = True
        if not spawn_memory.need_lorries:
            spawn_memory.need_lorries = 1
    enough_lorries = False
    if spawn_memory.lorries >= spawn_memory.need_lorries:
        enough_lorries = True
    for source in sources:
        mine_near_container = _.filter(source.pos.findInRange(FIND_STRUCTURES, 2),
                                       lambda s: (s.structureType == STRUCTURE_CONTAINER
                                                  or s.structureType == STRUCTURE_LINK))

        if len(mine_near_container) == 0:
            create_container(source)
        else:
            mines_near_container = mines_near_container + 1

        starters = spawn_memory.starters
        if need_restart:
            if source.energy > source.ticksToRegeneration * 15 or source.energy >= 2800:
                if need_starters < len(sources) * 3:
                    need_starters = need_starters + 0.01
            if source.energy < source.ticksToRegeneration * 5:
                if need_starters >= starters - 2:
                    need_starters = need_starters - 0.03
    if not need_restart:
        need_starters = 0
    spawn_memory.need_starters = need_starters

    if need_restart:
        worker_to_starter = _(spawn.room.find(FIND_MY_CREEPS)
                              .filter(lambda c: c.memory != undefined)
                              .filter(lambda c: c.memory.job == 'worker')).sample()
        if worker_to_starter:
            if spawn_memory.workers > 1:
                worker_to_starter.memory.job = 'starter'
                del worker_to_starter.memory.duty
                del worker_to_starter.memory.target
                del worker_to_starter.memory.path

    if not need_restart:
        starter_to_worker = _(spawn.room.find(FIND_MY_CREEPS)
                              .filter(lambda c: c.memory != undefined)
                              .filter(lambda c: c.memory.job == 'starter')).sample()
        if starter_to_worker:
            starter_to_worker.memory.job = 'worker'
            del starter_to_worker.memory.duty
            del starter_to_worker.memory.target
            del starter_to_worker.memory.path

    defended = False
    if spawn_memory.defenders >= 2:
        defended = True

    spawn_jobs = ['defender', 'miner', 'lorry', 'worker', 'claimer', 'spawn_builder',
                  'reservator', 'stealer', 'starter', 'healer', 'truck', 'offender', 'steaminer']
    my_creeps = _.filter(Game.creeps, lambda c: c.memory != undefined)
    my_creeps_with_memory = _.filter(my_creeps, lambda c: c.memory.job != undefined)
    actual_spawn_builders = _.filter(my_creeps_with_memory,
                                     lambda c: c.memory.home == spawn.id and
                                               c.memory.flag == 'BS' and
                                               c.ticksToLive > 20)
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
                flag_name = None
                spawning_creep(spawn, job_name, flag_name)

        elif job_name == 'offender':
            if not need_restart and defended and enough_lorries and enough_miners:
                spawn_memory.offenders = number_of_creeps_filtered
                if spawn_memory.need_offenders > number_of_creeps_filtered:
                    desired_job = job_name
                    flag_name = None
                    spawning_creep(spawn, job_name, flag_name)

        elif job_name == 'healer':
            spawn_memory.healers = number_of_creeps_filtered
            if spawn_memory.healers < spawn_memory.defenders + spawn_memory.offenders:
                desired_job = job_name
                flag_name = None
                spawning_creep(spawn, job_name, flag_name)

        elif job_name == 'starter':
            spawn_memory.starters = number_of_creeps_filtered
            if spawn_memory.need_starters > number_of_creeps_filtered:
                desired_job = job_name
                flag_name = None
                spawning_creep(spawn, job_name, flag_name)

        elif job_name == 'miner':
            spawn_memory.miners = number_of_creeps_filtered
            need_miners = mines_near_container * 2
            spawn_memory.need_miners = need_miners
            if need_miners > number_of_creeps_filtered:
                desired_job = job_name
                flag_name = None
                spawning_creep(spawn, job_name, flag_name)

        elif job_name == 'lorry':
            if enough_miners:
                spawn_memory.lorries = number_of_creeps_filtered
                if spawn_memory.need_lorries > number_of_creeps_filtered:
                    desired_job = job_name
                    flag_name = None
                    spawning_creep(spawn, job_name, flag_name)

        elif job_name == 'worker':
            spawn_memory.workers = number_of_creeps_filtered
            if defended and not need_restart and enough_lorries and enough_miners:
                if spawn_memory.need_workers > number_of_creeps_filtered:
                    desired_job = job_name
                    flag_name = None
                    spawning_creep(spawn, job_name, flag_name)

        elif job_name == 'reservator':
            if not need_restart and defended and enough_lorries and enough_miners \
                    and spawn.room.energyCapacityAvailable >= 700:
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
                                    spawning_creep(spawn, job_name, flag_name)
                        flag.memory = flag_memory

        elif job_name == 'stealer':
            for flag_name in Object.keys(Game.flags):
                if flag_name[:6] == 'Steal' + spawn.name[5:6]:
                    flag = Game.flags[flag_name]
                    flag_memory = flag.memory
                    stealers_on_the_flag = _.filter(creeps_filtered, lambda c: c.memory.flag == flag_name)
                    flag.memory.stealers = len(stealers_on_the_flag)
                    if flag_memory.need_stealers > flag_memory.stealers and spawn_memory.workers > 1:
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

        elif job_name == 'steaminer':
            if not need_restart and defended and enough_lorries and enough_miners:
                for flag_name in Object.keys(Game.flags):
                    if flag_name[:6] == 'Steal' + spawn.name[5:6]:
                        flag = Game.flags[flag_name]
                        flag_memory = flag.memory
                        steaminers_on_the_flag = _.filter(creeps_filtered, lambda c: c.memory.flag == flag_name)
                        flag.memory.miners = len(steaminers_on_the_flag)
                        if flag_memory.need_miners > flag_memory.miners:
                            desired_job = job_name
                            spawning_creep(spawn, job_name, flag_name)

        elif job_name == 'truck':
            if not need_restart and defended and enough_lorries and enough_miners:
                for flag_name in Object.keys(Game.flags):
                    if flag_name[:7] == 'Energy' + spawn.name[5:6]:
                        flag = Game.flags[flag_name]
                        flag_memory = flag.memory
                        flag_memory.trucks = number_of_creeps_filtered
                        if 3 > number_of_creeps_filtered:
                            desired_job = job_name
                            spawning_creep(spawn, job_name, flag_name)

        elif job_name == 'claimer':
            flag_name = Memory.claim
            spawn_memory.claimers = number_of_creeps_filtered
            if flag_name == 'claim' + spawn.name[5:6]:
                if Memory.building_spawn:
                    flag = Game.flags[flag_name]
                    if flag:
                        flag.pos.createFlag('BS')
                        flag.remove()
                        del Memory.claim
                else:
                    if number_of_creeps_filtered < 1:
                        desired_job = job_name
                        spawning_creep(spawn, job_name, flag_name)

        elif job_name == 'spawn_builder':
            if enough_lorries and defended and enough_miners and not need_restart:
                flag = Game.flags['BS']
                if flag:
                    if Memory.building_spawn[5:6] == spawn.name[5:6]:
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

    spawn_memory.desired_job = desired_job

    print('    ' + spawn.name + ' - ' +
          'Starters:  ' + spawn_memory.starters + '/' + round(spawn_memory.need_starters, 3) +
          '. Miners:  ' + spawn_memory.miners + '/' + round(spawn_memory.need_miners, 3) +
          '. Lorries:  ' + spawn_memory.lorries + '/' + round(spawn_memory.need_lorries, 3) +
          ". Workers:  " + spawn_memory.workers + '/' + round(spawn_memory.need_workers, 3) +
          '.           Desired job: ' + spawn_memory.desired_job)

    for flag_name in Object.keys(Game.flags):
        if flag_name[:6] == 'Steal' + spawn.name[5:6]:
            flag = Game.flags[flag_name]
            if flag.room:
                enemies = flag.room.find(FIND_HOSTILE_CREEPS, {'filter': lambda e: e.owner.username != 'rep71Le'})
                if len(enemies) <= 0:
                    sources = flag.room.find(FIND_SOURCES)
                    mines_near_container = 0
                    for source in sources:
                        mine_near_container = _.filter(source.pos.findInRange(FIND_STRUCTURES, 2),
                                                       lambda s: (s.structureType == STRUCTURE_CONTAINER
                                                                  or s.structureType == STRUCTURE_LINK))

                        if len(mine_near_container) == 1:
                            mines_near_container = mines_near_container + 1
                    flag_memory = flag.memory
                    flag_memory.need_miners = mines_near_container * 2
                    if mines_near_container < len(sources):
                        if not flag_memory.need_stealers:
                            flag_memory.need_stealers = 3
                        need_stealers = flag_memory.need_stealers
                        stealers = flag_memory.stealers
                        for source in sources:
                            if source.energy >= 3000 or source.energy / source.ticksToRegeneration > 10:
                                if need_stealers < 10:
                                    need_stealers = need_stealers + 0.01
                                    if stealers == 0:
                                        need_stealers = 3
                            if source.energy / source.ticksToRegeneration < 8 or source.energy <= 0:
                                if need_stealers > 1:
                                    need_stealers = need_stealers - 0.001
                        flag_memory.need_stealers = need_stealers
                    else:
                        need_repairs = _(flag.room.find(FIND_STRUCTURES)) \
                            .filter(lambda s: (s.hits < s.hitsMax * 0.4) and
                                              s.structureType != STRUCTURE_WALL) \
                            .sortBy(lambda s: (s.hitsMax / s.hits)).last()
                        if need_repairs:
                            do_not_repairs = Memory.deconstructions
                            if do_not_repairs:
                                for do_not_repair in do_not_repairs:
                                    if need_repairs:
                                        if need_repairs.id == do_not_repair:
                                            flag_memory.need_repairs = False
                                            need_repairs = undefined
                                            flag_memory.need_stealers = 0
                                        else:
                                            flag_memory.need_repairs = True
                                            flag_memory.need_stealers = 1
                        else:
                            flag_memory.need_repairs = False
                            flag_memory.need_stealers = 0
                    controller = flag.room.controller
                    reservation = 0
                    if controller.reservation:
                        reservation = controller.reservation.ticksToEnd
                    flag_memory.reservation = reservation
                    if reservation < 2000:
                        flag_memory.need_reservators = 2
                    else:
                        flag_memory.need_reservators = 1
                    print('      ' + flag.name +
                          '  -  Stealers: ' +
                          str(flag_memory.stealers) + '/' + str(round(flag_memory.need_stealers, 3)) +
                          '.     << Reservation: ' + str(reservation) +
                          '. Reservators: ' +
                          str(flag_memory.reservators) + '/' + str(flag_memory.need_reservators) +
                          '. >>     Miners: ' +
                          str(flag_memory.miners) + '/' + str(flag_memory.need_miners) +
                          '.      Need repairs: ' + str(flag_memory.need_repairs)
                          )
                    flag.memory = flag_memory
                else:
                    defenders = _.sum(flag.room.find(FIND_MY_CREEPS), lambda c: c.memory.job == 'defender')
                    if len(defenders) < 1:
                        flag.pos.createFlag('A' + flag.name)
                        flag.remove()
            else:
                flag.memory.need_stealers = 3

    spawn.memory = spawn_memory

    return desired_job


def define_body(spawn, job_name):
    desired_body = []
    if job_name == 'defender' or job_name == 'offender':
        for a in range(1, 5):
            if spawn.room.energyAvailable >= a * 380:
                desired_body.extend([TOUGH, TOUGH, TOUGH, MOVE, MOVE])
        for a in range(1, 5):
            if spawn.room.energyAvailable >= a * 380:
                desired_body.extend([MOVE, MOVE, RANGED_ATTACK])
    if job_name == 'healer':
        for a in range(1, 4):
            if spawn.room.energyAvailable >= a * 480:
                desired_body.extend([TOUGH, TOUGH, TOUGH, MOVE, MOVE])
        for a in range(1, 4):
            if spawn.room.energyAvailable >= a * 480:
                desired_body.extend([MOVE, MOVE, HEAL])
    elif job_name == 'starter':
        for a in range(1, 8):
            if spawn.room.energyAvailable >= a * 200:
                desired_body.extend([WORK, CARRY, MOVE])
    elif job_name == 'worker':
        for a in range(1, 8):
            if spawn.room.energyCapacityAvailable >= a * 200:
                desired_body.extend([WORK, CARRY, MOVE])
    elif job_name == 'miner' or job_name == 'steaminer':
        if spawn.room.energyCapacityAvailable == 550:
            desired_body.extend([WORK, WORK, WORK, WORK, CARRY, CARRY, MOVE])
        if spawn.room.energyCapacityAvailable >= 600:
            desired_body.extend([WORK, WORK, WORK, WORK, CARRY, CARRY, MOVE, MOVE])
    elif job_name == 'lorry':
        for a in range(1, 6):
            if spawn.room.energyCapacityAvailable >= a * 150:
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
        deconstructions = Memory.deconstructions
        have_to_dismantle_in_the_room = False
        if deconstructions:
            for deconstruction in deconstructions:
                deconstruction_site = Game.getObjectById(deconstruction)
                if deconstruction_site:
                    if deconstruction_site.room == spawn.room:
                        have_to_dismantle_in_the_room = True
        if not have_to_dismantle_in_the_room:
            controller_lvl = spawn.room.controller.level
            extensions = _.filter(spawn.room.find(FIND_STRUCTURES), lambda s: s.structureType == STRUCTURE_EXTENSION)
            if controller_lvl == 2:
                if len(extensions) < 5:
                    if verify_square_and_place_extension(spawn.pos):
                        return
                    for extension in extensions:
                        if verify_square_and_place_extension(extension.pos):
                            return
            elif controller_lvl > 2:
                if len(extensions) < (controller_lvl - 2) * 10:
                    if verify_square_and_place_extension(spawn.pos):
                        return
                    for extension in extensions:
                        if verify_square_and_place_extension(extension.pos):
                            return


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
                        return extension_placed
                if direction == 2:
                    position.x = position.x + 1
                    position.y = position.y + 1
                    extension_placed = place_extension(position)
                    if extension_placed:
                        return extension_placed
                if direction == 3:
                    position.x = position.x - 1
                    position.y = position.y + 1
                    extension_placed = place_extension(position)
                    if extension_placed:
                        return extension_placed
                if direction == 4:
                    position.x = position.x - 1
                    position.y = position.y - 1
                    extension_placed = place_extension(position)
                    if extension_placed:
                        return extension_placed


def place_extension(position):
    if 4 < position.x < 45 and 4 < position.y < 45:
        terrain = position.lookFor(LOOK_TERRAIN)
        structures = position.lookFor(LOOK_STRUCTURES)
        roads = _.filter(position.lookFor(LOOK_STRUCTURES), lambda s: s.structureType == STRUCTURE_ROAD)
        if terrain != 'wall' and len(roads) > 0:
            position.createFlag('dc' + roads[0].id)
            extension_placed = True
            return extension_placed
        elif terrain != 'wall' and len(structures) == 0:
            extensions = _.sum(position.findInRange(FIND_STRUCTURES, 1),
                               lambda s: s.structureType == STRUCTURE_EXTENSION or
                                         s.structureType == STRUCTURE_SPAWN)
            if extensions > 0:
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
    if source.room.energyCapacityAvailable >= 550:
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
