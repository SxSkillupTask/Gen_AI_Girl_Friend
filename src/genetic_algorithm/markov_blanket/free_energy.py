import numpy as np

def calculate_dkl(q_x, p_x_given_s):
    """
    KLダイバージェンス（DKL）を計算する関数
    - q_x: 推定確率分布
    - p_x_given_s: 条件付き確率分布
    """
    epsilon = 1e-10  # 小さな値を追加してゼロ除算を防ぐ
    q_x = np.clip(q_x, epsilon, None)  # q_xを小さな値にクリップ
    p_x_given_s = np.clip(p_x_given_s, epsilon, None)  # p_x_given_sを小さな値にクリップ
    return np.sum(q_x * np.log(q_x / p_x_given_s))

def calculate_variational_free_energy(q_x, p_x_given_s, p_s):
    """
    変分自由エネルギー（VFE）を計算する関数
    - q_x: 推定確率分布
    - p_x_given_s: 条件付き確率分布
    - p_s: 周辺確率
    """
    epsilon = 1e-10  # 小さな値を追加してゼロ除算を防ぐ
    p_s = max(p_s, epsilon)  # p_sを小さな値にクリップ
    D_KL = calculate_dkl(q_x, p_x_given_s)
    VFE = D_KL - np.log(p_s)
    return VFE
