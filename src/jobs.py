
def run_starter(creep):
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


def run_miner(creep):
    if self.creep.memory.source and self.creep.memory.container and self.creep.memory.duty:
        if self.creep.memory.duty == 'mining':
            self.miner_mines()
        elif self.creep.memory.duty == 'to_closest_container':
            self.miner_delivers()
    else:
        self.define_miner_targets()


def run_worker(creep):
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


def run_lorry(creep):
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


def run_defender(creep):
    if self.creep.memory.duty:
        if self.creep.memory.duty == 'attacking':
            self.attacking()
        elif self.creep.memory.duty == 'defending':
            self.defending()
    else:
        self.define_defender_targets()


def run_reservator(creep):
    if self.creep.memory.duty:
        if self.creep.memory.duty == 'go_to_flag':
            self.going_to_flag()
        elif self.creep.memory.duty == 'reserving':
            self.reserving()
    else:
        self.define_reservator_targets()


def run_stealer(creep):
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


def job_runner(creep):
    job = creep.memory.job
    if job == 'starter':
        run_starter(creep)
    if job == 'miner':
        run_miner(creep)
    if job == 'worker':
        run_worker(creep)
    if job == 'lorry':
        run_lorry(creep)
    if job == 'defender':
        run_defender(creep)
    if job[:10] == 'reservator':
        run_reservator(creep)
    if job[:7] == 'stealer':
        run_stealer(creep)
