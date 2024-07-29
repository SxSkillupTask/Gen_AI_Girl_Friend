import numpy as np
from self_organizing_system.self_organizing_system import SelfOrganizingSystem
import constant_values as const

class POETAlgorithm: #POETアルゴリズムの実装
    # def __init__(self, population_size, mutation_rate):
    #     """
    #     POETアルゴリズムの初期化
    #     - 初期集団と環境を生成
    #     """
    #     self.population_size = population_size
    #     self.mutation_rate = mutation_rate
    #     self.population = [SelfOrganizingSystem() for _ in range(population_size)]
    #     self.environments = [self.create_initial_environment()]

    # def evolve(self):
    #     """
    #     エージェントと環境の進化
    #     - 各環境に対して、エージェントを評価し進化させる。
    #     """
    #     for env in self.environments:
    #         for agent in self.population:
    #             VFE = agent.step()
    #             if VFE < self.get_threshold(env):
    #                 self.save_agent(agent, env)
    #     self.create_new_environment()

    # def create_initial_environment(self):
    #     """
    #     初期環境の生成
    #     - ランダムな環境を生成
    #     """
    #     return np.random.rand(4)

    # def create_new_environment(self):
    #     """
    #     新しい環境の生成ロジック
    #     - 新しい環境をランダムに生成し追加
    #     """
    #     new_env = np.random.rand(4)
    #     self.environments.append(new_env)

    # def get_threshold(self, env):
    #     """
    #     環境に応じた自由エネルギーの閾値を設定
    #     - 環境ごとに自由エネルギーの閾値を設定
    #     """
    #     return 1.0

    # def save_agent(self, agent, env):
    #     """
    #     エージェントと環境のペアを保存
    #     - 良好なエージェントと環境のペアを保存
    #     """
    #     pass

    def __init__(self, population_size, mutation_rate):
        """
        POETアルゴリズムの初期化
        - 初期集団と環境を生成
        """
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.population = [SelfOrganizingSystem() for _ in range(population_size)]
        self.environments = [self.create_initial_environment()]

    def evolve(self):
        """
        エージェントと環境の進化
        - 各環境に対して、エージェントを評価し進化させる。
        """
        for env in self.environments:
            for agent in self.population:
                VFE = agent.step()
                if VFE < self.get_threshold(env):
                    self.save_agent(agent, env)
        self.create_new_environment()

    def create_initial_environment(self):
        """
        初期環境の生成
        - ランダムな環境を生成
        """
        return np.random.rand(4)

    def create_new_environment(self):
        """
        新しい環境の生成ロジック
        - 新しい環境をランダムに生成し追加
        """
        new_env = np.random.rand(4)
        self.environments.append(new_env)

    def get_threshold(self, env):
        """
        環境に応じた自由エネルギーの閾値を設定
        - 環境ごとに自由エネルギーの閾値を設定
        """
        return 1.0

    def save_agent(self, agent, env):
        """
        エージェントと環境のペアを保存
        - 良好なエージェントと環境のペアを保存
        """
        pass
