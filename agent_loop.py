import requests
import json

API_KEY = "75bfa8d5d859496faafa32c510c770f8.Rjl161QeXMWWGWlU"
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
    print(resp.json()["choices"][0]["message"]["reasoning_content"])
    return resp.json()["choices"][0]["message"]["content"]

from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="sk-no-key"
)

def ask_glm_openai(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model="model",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content


import subprocess

def run_cmd(cmd):
    print(f"\n[执行] {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8")
    return (result.stdout or "") + (result.stderr or "")


def run_agent(total_goal):
    # run_cmd('playwright-cli open https://demo.playwright.dev/todomvc/ --headed')

    system_prompt = open("prompt.txt", encoding="utf-8").read()

    current_snapshot = run_cmd('playwright-cli snapshot')
    history = []

    for step in range(20):
        print(f"\n=== Step {step+1} ===")

        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        user_prompt = f"""
        当前时间：{current_time}
        总目标：{total_goal}
        页面快照：{current_snapshot}
        历史操作记录：{history}
        """

        result = json.loads(ask_glm(system_prompt, user_prompt).strip())

        print("LLM:", result)
        history.append(result)
        action = result["command"]

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

        if "snapshot" in action:
            current_snapshot = output
        else:
            current_snapshot = run_cmd('playwright-cli snapshot')
    print(history)

if __name__ == "__main__":
    # 先手动打开
    # playwright-cli open https://demo.playwright.dev/todomvc/ --headed

    run_agent("添加一个洗车的代做任务")
    run_agent("我刚才洗过车了，之后我还要洗衣服和拿快递")
    run_agent("把已完成的任务清空一下，然后我已经洗了衣服，改为收衣服")
    # run_agent("今年五一假期怎么放？")



