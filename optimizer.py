import numpy as np

class EmailSubjectOptimizer:
    def __init__(self, factors, learning_rate=0.1, epsilon=0.1):
        self.factors = factors
        self.q_values = {}
        self.learning_rate = learning_rate
        self.epsilon = epsilon

    def get_state_key(self, state):
        return ''.join(str(state[factor]) for factor in self.factors)

    def choose_action(self, state):
        state_key = self.get_state_key(state)
        if state_key not in self.q_values:
            self.q_values[state_key] = {factor: 0 for factor in self.factors}

        if np.random.random() < self.epsilon:
            factor_to_change = np.random.choice(self.factors)
            new_state = state.copy()
            new_state[factor_to_change] = 1 - new_state[factor_to_change]
            return new_state
        else:
            best_factor = max(self.q_values[state_key], key=self.q_values[state_key].get)
            new_state = state.copy()
            new_state[best_factor] = 1 - new_state[best_factor]
            return new_state

    def update_q_values(self, state, action, reward, next_state):
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)

        if next_state_key not in self.q_values:
            self.q_values[next_state_key] = {factor: 0 for factor in self.factors}

        changed_factor = [f for f in self.factors if state[f] != action[f]][0]

        current_q = self.q_values[state_key][changed_factor]
        max_next_q = max(self.q_values[next_state_key].values())
        new_q = current_q + self.learning_rate * (reward + max_next_q - current_q)
        self.q_values[state_key][changed_factor] = new_q