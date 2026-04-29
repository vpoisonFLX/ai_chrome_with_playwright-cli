import subprocess
import re
from pathlib import Path

def run_cmd(cmd):
    print(f"\n[执行] {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    output = (result.stdout or "") + (result.stderr or "")

    # 匹配 - [Snapshot](xxx.yml / yml)
    pattern = r"- \[Snapshot\]\(([^)]+\.(?:ya?ml))\)"

    def replace_snapshot(match):
        yml_path = match.group(1)

        try:
            content = Path(yml_path).read_text(encoding="utf-8")
        except Exception as e:
            return f"- Snapshot Content: [READ FAILED] {yml_path} | {e}"

        # 缩进展示 YAML 内容
        indented = "\n".join("    " + line for line in content.splitlines())
        return f"- Snapshot Content:\n{indented}"

    output = re.sub(pattern, replace_snapshot, output)

    return output

# a = run_cmd('playwright-cli open https://demo.playwright.dev/todomvc/ --headed')

a = run_cmd('playwright-cli snapshot')

# a = run_cmd('playwright-cli screenshot')

# a = run_cmd('playwright-cli fill e8 "洗衣服" --submit')


# a = run_cmd('playwright-cli tab-select 1')

print(a)

