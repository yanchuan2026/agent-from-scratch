import os
import httpx
from dotenv import load_dotenv

#从项目根目录的.env读取键值，放进os.environ
load_dotenv()

API_URL="https://api.deepseek.com/chat/completions"
MODEL="deepseek-chat"

def main()->None:
    api_key=os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("没有找到DEEPSEEK_API_KEY检查项目根目录下的.env")
    response = httpx.post(
        API_URL,
        headers={"Authorization":f"Bearer {api_key}"},
        json={
            "model":MODEL,
            "messages":[
                {"role":"system","content":"你是一个简洁的助手,回答不超过三句话。"},
                {"role":"user","content":"用一句话解释什么是AI Agent。"},
            ],
            "temperature":0,
            "max_tokens":200,
        },
        timeout=30.0,
    )
    response.raise_for_status()
    data=response.json()

    print("【模型回复】")
    print(data["choices"][0]["message"]["content"])
    print()
    print("【用量】")
    print(data["usage"])

if __name__=="__main__":
    main()