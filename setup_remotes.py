#!/usr/bin/env python3
"""确保 origin 已配置双 push 地址（Gitee + GitHub）。

先检查，仅在未完整配置时才设置；幂等、可重复运行。

用法：
    python setup_remotes.py
"""

import subprocess
import sys

GITHUB = "https://github.com/chianjin/PDFeXpress.git"
GITEE = "https://gitee.com/jinchian/PDFeXpress.git"


def git(args):
    return subprocess.run(["git"] + args, capture_output=True, text=True)


def current_pushurls():
    out = git(["config", "--get-all", "remote.origin.pushurl"]).stdout
    return [u.strip() for u in out.splitlines() if u.strip()]


def print_state(urls):
    if urls:
        for u in urls:
            print(f"  - {u}")
    else:
        print("  （无自定义 pushurl，推送回退到 remote.origin.url）")


def main():
    if git(["rev-parse", "--is-inside-work-tree"]).returncode != 0:
        print("错误：当前目录不是 git 工作树。", file=sys.stderr)
        return 1

    urls = current_pushurls()
    print("当前 pushurl：")
    print_state(urls)

    if GITHUB in urls and GITEE in urls:
        print("✓ 双 push 已配置，无需改动。")
        return 0

    print("双 push 未完整配置，正在修复...")

    # 1) 清掉所有现有 pushurl，回到 git 默认（按 url 推送）状态
    for u in list(current_pushurls()):
        git(["remote", "set-url", "--delete", "--push", "origin", u])

    # 2) 按顺序加回：GitHub 先于 Gitee。
    #    首个 --add 会覆盖默认 url-based push，故先放 GitHub，
    #    再追加 Gitee，最终顺序 [GitHub, Gitee]。
    for u in (GITHUB, GITEE):
        git(["remote", "set-url", "--add", "--push", "origin", u])

    print("✓ 已设置双 push：")
    print_state(current_pushurls())
    return 0


if __name__ == "__main__":
    sys.exit(main())
