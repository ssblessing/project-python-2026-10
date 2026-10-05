"""
项目管理辅助工具
提供缓存清理、环境信息查询、帮助文档等功能。
"""

from __future__ import annotations

import platform
import shutil
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

# ==================== 配置定义 ====================


@dataclass
class CleanConfig:
    """缓存清理的配置项。"""

    max_display: int = 10
    venv_dir: str = ".venv"
    cache_patterns: set[str] = field(
        default_factory=lambda: {
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            ".ipynb_checkpoints",
            "htmlcov",
            ".tox",
            ".nox",
        }
    )


CLEAN_CONFIG = CleanConfig()


# ==================== 核心业务逻辑 ====================


def scan_cache_dirs(root: Path, config: CleanConfig) -> list[Path]:
    """扫描给定根目录下的所有缓存目录。"""
    targets = []
    patterns = config.cache_patterns
    venv_dir = config.venv_dir

    for pattern in patterns:
        for p in root.rglob(pattern):
            # 跳过虚拟环境目录中的缓存
            if any(part.casefold() == venv_dir.casefold() for part in p.parts):
                continue
            targets.append(p)
    return targets


def remove_paths(paths: list[Path]) -> int:
    """批量删除路径，并返回成功删除的数量。"""
    success = 0
    for p in paths:
        try:
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
            success += 1
        except Exception as e:  # noqa: BLE001
            print(f"  ⚠️ 无法删除 {p.name}: {e}")
    return success


# ==================== 功能函数 ====================


def clean() -> None:
    """清理项目缓存"""
    root = Path.cwd()
    targets = scan_cache_dirs(root, CLEAN_CONFIG)

    if not targets:
        print("✅ 未发现缓存目录，环境已是干净的。")
        return

    max_display = CLEAN_CONFIG.max_display
    targets.sort(key=lambda x: len(x.parts), reverse=True)

    print(f"📁 发现 {len(targets)} 个缓存目录：")
    for p in targets[:max_display]:
        print(f"  🗑️  {p.relative_to(root)}")
    if len(targets) > max_display:
        print(f"  ... 还有 {len(targets) - max_display} 个未显示")

    print("\n正在清理...")
    success_count = remove_paths(targets)
    print(f"✅ 成功清理 {success_count} 个目录。")


def info() -> None:
    """显示环境信息"""
    print("🖥️  环境信息：")
    print(f"  🐍 Python  : {platform.python_version()} ({sys.executable})")
    print(f"  📂 工作目录 : {Path.cwd()}")
    print(f"  💻 操作系统 : {platform.system()} {platform.release()}")
    print(f"  🏷️  主机名  : {platform.node()}")


def help_menu() -> None:
    """显示帮助菜单"""
    print("📋 可用命令：\n")
    max_len = max(len(k) for k in COMMANDS)
    for name, func in COMMANDS.items():
        desc = "无描述"
        if func.__doc__:
            desc = func.__doc__.strip().split("\n")[0]
        print(f"  {name.ljust(max_len)}  : {desc}")


# ==================== 路由注册 ====================

COMMANDS: dict[str, Callable] = {
    "clean": clean,
    "info": info,
    "list": help_menu,
}


# ==================== 程序入口 ====================


def main() -> None:
    """程序入口"""
    args = sys.argv[1:]
    cmd_name = args[0] if args else "list"

    if cmd_name in COMMANDS:
        COMMANDS[cmd_name]()
    else:
        print(f"❌ 未知命令: {cmd_name}\n")
        help_menu()
        sys.exit(1)


if __name__ == "__main__":
    main()
