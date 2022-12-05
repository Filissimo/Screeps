from defs import *
from src.objects import SpawnRunner, CreepRunner, FlagRunner

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def main():
    if Game.cpu.bucket >= 10000:
        Game.cpu.generatePixel()

    list_of_jobs = ['defender-', 'miner-', 'lorry-', 'worker-', 'claimer-', 'spawn_builder-',
                    'reservator-', 'stealer-', 'starter-', 'healer-', 'truck-']
    for i in range(Memory.Number_of_creep - 410, Memory.Number_of_creep - 400):
        for j in list_of_jobs:
            c_name = j + str(i)
            if Memory.creeps[c_name]:
                if not Game.creeps[c_name]:
                    del Memory.creeps[c_name]

    if not Memory.countdown:
        Memory.countdown = 0
    countdown = Memory.countdown
    countdown = countdown + 1
    Memory.countdown = countdown
    spaces = '  ' + str(countdown)
    for i in range(countdown):
        spaces = '>-' + spaces
    print('-  NEW TICK -' + spaces)
    if countdown >= 100:
        Memory.countdown = 0
    r_i_m_to_remove = None
    message_about_removing = undefined
    roads_in_memory = Memory.roads
    if roads_in_memory:
        print('Roads in memory: ' + str(len(roads_in_memory)))
        for r_i_m in roads_in_memory:
            for i in range(23, 26):
                if r_i_m[str(r_i_m)[2:i]] != undefined:
                    new_counter = r_i_m[str(r_i_m)[2:i]] - 1
                    if new_counter <= 0:
                        r_i_m_to_remove = r_i_m
                        message_about_removing = (str(r_i_m)[2:25] +
                                                  ' removed from memory, because: ' +
                                                  r_i_m[str(r_i_m)[2:i]])
                    elif new_counter > 0:
                        roads_in_memory.remove(r_i_m)
                        roads_in_memory.append({str(r_i_m)[2:i]: new_counter})
        if r_i_m_to_remove:
            roads_in_memory.remove(r_i_m_to_remove)
        if message_about_removing:
            print(message_about_removing)
    for spawn_name in Object.keys(Game.spawns):
        spawn = Game.spawns[spawn_name]
        s = SpawnRunner(spawn)
        s.spawning_spawn()
        s.towering_towers(spawn)

    for creep_name in Object.keys(Game.creeps):
        creep = Game.creeps[creep_name]
        c = CreepRunner(creep)
        if not creep.spawning:
            target_before = creep.memory.target
            c.creeping_creep()
            target_after = creep.memory.target
            if target_before != target_after:
                c.creeping_creep()
    for flag_name in Object.keys(Game.flags):
        flag = Game.flags[flag_name]
        s = FlagRunner(flag)
        s.flagging_flag()

    if not Memory.cpu_averaged:
        Memory.cpu_averaged = 100
    cpu_used = Memory.cpu
    cpu_averaged = Memory.cpu_averaged
    cpu_averaged_processed = cpu_averaged + ((cpu_used - cpu_averaged) / 25)

    print('                                                       Average CPU used = '
          + str(round(cpu_averaged, 3)))
    Memory.cpu_averaged = cpu_averaged_processed
    Memory.cpu = Game.cpu.getUsed()
    print('                                                       Used CPU at this tick: '
          + str(round(Game.cpu.getUsed(), 3)))


module.exports.loop = main
