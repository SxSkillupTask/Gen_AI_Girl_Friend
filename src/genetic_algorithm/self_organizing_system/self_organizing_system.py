import numpy as np
from markov_blanket.markov_blanket import MarkovBlanket
from markov_blanket.free_energy import calculate_variational_free_energy

class SelfOrganizingSystem:
    def __init__(self):
        """
        自己組織化システムの初期化
        - マルコフブランケットを初期化し、初期状態を設定する。
        """
        self.markov_blanket = MarkovBlanket(
            internal_states=np.random.rand(4),
            external_states=np.random.rand(4),
            sensory_states=np.random.rand(4),
            active_states=np.random.rand(4)
        )

    def step(self):
        """
        マルコフブランケットの状態を更新し、自由エネルギーを計算
        - マルコフブランケットの状態を更新
        - 内部状態、外部状態、感覚状態を使って自由エネルギーを計算
        """
        self.markov_blanket.update_states()
        q_x = self.markov_blanket.internal_states
        p_x_given_s = self.markov_blanket.external_states
        p_s = np.sum(self.markov_blanket.sensory_states) / len(self.markov_blanket.sensory_states)
        print(f"q_x: {q_x}, p_x_given_s: {p_x_given_s}, p_s: {p_s}")  # デバッグ用出力
        VFE = calculate_variational_free_energy(q_x, p_x_given_s, p_s)
        print(f"VFE: {VFE}")  # デバッグ用出力
        return VFE

