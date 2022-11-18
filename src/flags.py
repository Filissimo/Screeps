from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


def define_deconstructions(flag):
    if not Memory.deconstructions:
        Memory.deconstructions = []
    deconstructions = Memory.deconstructions
    structures = flag.pos.lookFor(LOOK_STRUCTURES)
    if len(structures) == 0:
        flag.remove()
    else:
        for s in structures:
            deconstructions.append(s.id)
        flag.remove()
        Memory.deconstructions = deconstructions


def flag_runner(flag):
    if flag.name[:2] == 'dc':
        define_deconstructions(flag)
    if flag.name[:5] == 'claim':
        Memory.claim = flag.name
    if flag.name == 'BS':
        if flag.room.energyCapacityAvailable > 0:
            flag.remove()

