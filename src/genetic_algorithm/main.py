from genetic_algorithm.genetic_algorithm import POETAlgorithm
import constant_values as const

def main():
    # 設定ファイルからパラメータを取得
    population_size = const.POPULATION_SIZE
    mutation_rate = const.MUTATION_RATE
    
    # POETアルゴリズムの初期設定とシミュレーションの実行
    ga = POETAlgorithm(population_size=population_size, mutation_rate=mutation_rate)
    
    for generation in range(const.NUM_GENERATIONS):
        ga.evolve()
        # 結果の可視化や保存など

if __name__ == "__main__":
    main()
