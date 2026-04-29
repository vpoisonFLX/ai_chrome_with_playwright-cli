import requests
import json

API_KEY = ""
URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def ask_glm(system_prompt, user_prompt):
    resp = requests.post(
        URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "glm-4.5-Air",  # glm-4.5-Air
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 4096,
            "temperature": 0.3  # 太低可能没有创造性导致陷入循环
        }
    )
    return resp.json()["choices"][0]["message"]["content"]

import subprocess
import re
from pathlib import Path

def run_cmd(cmd):
    # print(f"\n[执行] {cmd}")
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

def run_agent(total_goal, attention):
    # run_cmd('playwright-cli open https://demo.playwright.dev/todomvc/ --headed')

    system_prompt = open("prompt.txt", encoding="utf-8").read()
    output = run_cmd('playwright-cli snapshot')
    history = []

    for step in range(20):
        print(f"\n=== Step {step+1} ===")

        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        user_prompt = f"""
        当前时间：{current_time}
        总目标：{total_goal}
        注意：{attention}
        页面快照：{output}
        历史操作：{history}
        """

        result = json.loads(ask_glm(system_prompt, user_prompt).strip())

        print("LLM:", result)
        history.append(result)
        action = result["command"]

        final_result = result["describe"]
        if action == "DONE":
            print("✅ 完成")
            break

        if action == "FAIL":
            print("❌ 失败")
            break
        if action == "RETURN":
            print(result["describe"])
            break

        output = run_cmd(action)

    return final_result

if __name__ == "__main__":
    # 启动playwright-cli专用浏览器
    open_command = "playwright-cli open https://demo.playwright.dev/todomvc/ --headed"
    run_cmd(open_command)

    # 输入需要自动化做的事情和操作时的注意事项
    attention = "注意时间"
    total_goal = "今年五一假期怎么放？",

    # 执行
    run_agent(total_goal, attention)
    # attention = "此为待办事项网页，请准确区分代办和已办"
    # run_agent("添加一个洗车的代做任务", attention)
    # run_agent("我刚才洗过车了，之后我还要洗衣服和拿快递", attention)
    # run_agent("把已完成的任务清空一下，然后我已经洗了衣服，改为收衣服", attention)





