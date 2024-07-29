import numpy as np

class MarkovBlanket:
    def __init__(self, internal_states, external_states, sensory_states, active_states):
        """
        マルコフブランケットの初期化
        """
        self.internal_states = internal_states
        self.external_states = external_states
        self.sensory_states = sensory_states
        self.active_states = active_states

    def update_states(self):
        """
        状態の更新ルールを定義
        - 内部状態と感覚状態をランダムに少しずつ変化させる。
        """
        self.internal_states += np.random.randn(*self.internal_states.shape) * 0.01
        self.sensory_states += np.random.randn(*self.sensory_states.shape) * 0.01

        # 内部状態と外部状態の範囲を制限
        self.internal_states = np.clip(self.internal_states, 0, 1)
        self.external_states = np.clip(self.external_states, 0, 1)
