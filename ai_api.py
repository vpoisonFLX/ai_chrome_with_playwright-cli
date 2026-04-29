import requests

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
    print(resp.json()["choices"][0]["message"]["reasoning_content"])
    return resp.json()["choices"][0]["message"]["content"]




