from markov_blanket.markov_blanket import MarkovBlanket
from markov_blanket.free_energy import calculate_free_energy

class SelfOrganizingSystem:
    def __init__(self):
        self.markov_blanket = MarkovBlanket(...)

    def step(self):
        self.markov_blanket.update_states()
        free_energy = calculate_free_energy(...)
        return free_energy
