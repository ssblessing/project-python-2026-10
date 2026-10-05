"""绘制不同阻尼比下的二阶系统阶跃响应曲线。"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties, findfont

from zhcontrol_sim.second_order import compute_settling_time, step_response


def _configure_chinese_font() -> str:
    """自动检测并配置 matplotlib 中文字体。

    按优先级依次尝试系统中常见的中文字体，找到第一个可用的即配置并返回。
    如果没有找到任何中文字体，返回空字符串并给出提示。

    Returns:
        使用的字体名称，未找到则返回空字符串
    """
    candidates = [
        "Microsoft YaHei",  # Windows 11 默认
        "SimHei",  # Windows 经典黑体
        "WenQuanYi Micro Hei",  # Linux 文泉驿微米黑
        "Noto Sans CJK SC",  # Linux Noto 字体
    ]
    for name in candidates:
        try:
            # 如果 findfont 返回的不是默认字体，说明找到了
            if findfont(FontProperties(family=name)) != findfont(FontProperties()):
                plt.rcParams["font.sans-serif"] = [name] + plt.rcParams[
                    "font.sans-serif"
                ]
                plt.rcParams["axes.unicode_minus"] = False
                return name
        except Exception:
            continue

    # 未找到中文字体，给出提示
    plt.rcParams["axes.unicode_minus"] = False
    print("⚠️  未找到中文字体，图表中的中文可能显示为方块。")
    print(
        "   Windows 用户通常无需担心；Linux 用户可执行：sudo apt install fonts-wqy-microhei"
    )
    return ""


def main() -> None:
    """主函数：计算并绘制阶跃响应曲线。"""
    # ===== 配置中文字体 =====
    font_name = _configure_chinese_font()
    if font_name:
        print(f"✓ 使用中文字体: {font_name}")

    # ===== 参数设置 =====
    omega_n = 2.0 * np.pi  # 自然频率：2π rad/s
    zeta_list = [0.2, 0.5, 0.707, 1.0, 1.5]  # 不同阻尼比
    t_end = 5.0  # 仿真时长

    # ===== 创建画布 =====
    fig, ax = plt.subplots(figsize=(12, 7), dpi=120)

    # ===== 逐个计算并绘图 =====
    for zeta in zeta_list:
        t, y = step_response(zeta, omega_n, t_end=t_end)

        # 构造图例标签
        label = f"ζ = {zeta}"
        if zeta < 1.0:
            label += "（欠阻尼）"
        elif abs(zeta - 1.0) < 1e-9:
            label += "（临界阻尼）"
        else:
            label += "（过阻尼）"

        ax.plot(t, y, linewidth=2, label=label)

        # 标注调节时间（仅对有稳态值的情况）
        if zeta > 0:
            ts = compute_settling_time(t, y, threshold=0.02)
            if ts is not None and ts < t_end:
                ax.axvline(
                    x=ts, color=ax.lines[-1].get_color(), linestyle="--", alpha=0.3
                )
                ax.annotate(
                    f"ts={ts:.1f}s",
                    xy=(ts, 1.0),
                    xytext=(ts + 0.15, 0.55 + zeta * 0.15),
                    fontsize=8,
                    color=ax.lines[-1].get_color(),
                    arrowprops=dict(arrowstyle="->", alpha=0.4),
                )

    # ===== 图形装饰 =====
    ax.axhline(y=1.0, color="gray", linestyle=":", linewidth=1, alpha=0.5)
    ax.text(t_end * 0.93, 1.02, "稳态值", fontsize=9, color="gray", ha="center")
    ax.set_title(
        f"二阶系统单位阶跃响应（ωₙ = {omega_n:.1f} rad/s）", fontsize=16, pad=15
    )
    ax.set_xlabel("时间 t (秒)", fontsize=13)
    ax.set_ylabel("输出 y(t)", fontsize=13)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=11, loc="right")
    ax.set_xlim(0, t_end)
    ax.set_ylim(bottom=-0.1)
    ax.tick_params(labelsize=11)
    fig.tight_layout()

    # ===== 保存并显示 =====
    output_path = "step_response.png"
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"✓ 图片已保存为 {output_path}")
    plt.show()


if __name__ == "__main__":
    main()
