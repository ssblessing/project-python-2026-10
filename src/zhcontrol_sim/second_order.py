"""二阶动力学系统仿真模块。

实现标准二阶系统的单位阶跃响应计算。
传递函数: G(s) = ω_n² / (s² + 2ζω_n s + ω_n²)

参考: https://en.wikipedia.org/wiki/Second-order_system
"""

from __future__ import annotations

import numpy as np


def step_response(
    zeta: float,
    omega_n: float,
    t_end: float = 10.0,
    num_points: int = 1000,
) -> tuple[np.ndarray, np.ndarray]:
    """计算二阶系统的单位阶跃响应。

    根据阻尼比的不同，使用对应的解析解公式。

    Args:
        zeta: 阻尼比 (无量纲)
        omega_n: 自然频率 (rad/s)
        t_end: 仿真结束时间 (秒)
        num_points: 时间采样点数

    Returns:
        time: 时间数组
        output: 系统输出数组（无量纲）
    """
    time = np.linspace(0, t_end, num_points)

    if zeta < 1.0:
        # 欠阻尼：振荡衰减
        omega_d = omega_n * np.sqrt(1 - zeta**2)  # 阻尼自然频率
        phi = np.arccos(zeta)  # 相位角
        output = 1.0 - (np.exp(-zeta * omega_n * time) / np.sqrt(1 - zeta**2)) * np.sin(
            omega_d * time + phi
        )
    elif abs(zeta - 1.0) < 1e-9:
        # 临界阻尼：快速无振荡
        output = 1.0 - np.exp(-omega_n * time) * (1.0 + omega_n * time)
    else:
        # 过阻尼：缓慢无振荡
        sqrt_term = np.sqrt(zeta**2 - 1.0)
        pole1 = -zeta * omega_n + omega_n * sqrt_term
        pole2 = -zeta * omega_n - omega_n * sqrt_term
        A = omega_n**2 / (pole1 * pole2)
        B = omega_n**2 / (pole1 * (pole1 - pole2))
        C = omega_n**2 / (pole2 * (pole2 - pole1))
        output = A + B * np.exp(pole1 * time) + C * np.exp(pole2 * time)

    return time, output


def compute_settling_time(
    t: np.ndarray,
    y: np.ndarray,
    threshold: float = 0.02,
) -> float | None:
    """计算调节时间。

    调节时间定义为：系统响应进入并保持在稳态值 ±threshold 范围内的时间。
    这是评价控制系统性能的重要指标之一。

    Args:
        t: 时间数组
        y: 响应数组
        threshold: 稳态误差带（默认 2%，即 ±2%）

    Returns:
        调节时间（秒），如果从未进入误差带则返回 None
    """
    steady_state = y[-1]
    lower = steady_state * (1 - threshold)
    upper = steady_state * (1 + threshold)

    # 从后向前搜索，找到最后一个超出误差带的时刻
    for i in range(len(t) - 1, -1, -1):
        if y[i] < lower or y[i] > upper:
            if i < len(t) - 1:
                return t[i + 1]
            return None
    return t[0]
