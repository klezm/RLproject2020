class Memory:
    # TODO: talk about depth convention here
    def __init__(self):
        self.memory = []

    def append_state_action_reward(self, S_A_R_triple):
        self.memory.insert(0, S_A_R_triple)

    def get_size(self):
        return len(self.memory)

    def get_state(self, depth=1):
        return self.memory[depth-1][0]

    def get_action(self, depth=1):
        return self.memory[depth-1][1]

    def get_reward(self, depth=1):
        return self.memory[depth-1][2]

    def forget_state_action_reward(self, depth=1):
        del self.memory[-depth:]
