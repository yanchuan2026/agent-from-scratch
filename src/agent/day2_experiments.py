import os

import httpx
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"
QUESTION = "用一句话说明什么是 function calling。"

# 去平台「价格/计费」页面查当前单价，单位：元 / 百万 token
INPUT_PRICE_PER_MILLION = 0.1
OUTPUT_PRICE_PER_MILLION = 3.0

def call(question:str,temperature:float=0,max_tokens:int=200)->dict:
    api_key=os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("没有找到DEEPSEEK_API_KEY 检查项目根目录下的.env")

    response = httpx.post(
        API_URL,
        headers={"Authorization":f"Bearer {api_key}"},
        json={
            "model":MODEL,
            "messages":[{"role":"user","content":question}],
            "temperature":temperature,
            "max_tokens":max_tokens,
        },
        timeout=60.0,
    )
    response.raise_for_status()
    data=response.json()
    choice=data["choices"][0]
    return {
        "content":choice["message"]["content"],
        "finish_reason":choice.get("finish_reason"),
        "usage":data["usage"],
    }

def experiment_temperature() -> None:
    print("=== 实验 1/2：temperature 0 vs 1，各问 5 次 ===")
    for temp in (0, 1):
        answers = []
        for i in range(5):
            result = call(QUESTION, temperature=temp)
            answers.append(result["content"].strip())
            print(f"  temp={temp} #{i + 1}: {result['content'].strip()[:50]}")
        unique = len(set(answers))
        print(f"  → temp={temp}：5 次里有 {unique} 种不同回答")
        print()


def experiment_max_tokens() -> None:
    print("=== 实验 3：max_tokens 截断 ===")
    long_question = "用大约 300 字介绍什么是 RAG。"
    for limit in (10, 300):
        result = call(long_question, temperature=0, max_tokens=limit)
        print(f"  max_tokens={limit}")
        print(f"    finish_reason = {result['finish_reason']}")#这里的单引号里面的内容都是字典的下标索引
        print(f"    completion_tokens = {result['usage']['completion_tokens']}")
        print(f"    内容结尾: ...{result['content'].strip()[-40:]}")#只取后四十个字符
    print()


def experiment_cost() -> None:
    print("=== 实验 4：token 用量与成本 ===")
    result = call(QUESTION, temperature=0)
    usage = result["usage"]
    print(f"  usage = {usage}")

    prompt_tokens = usage["prompt_tokens"]
    completion_tokens = usage["completion_tokens"]

    per_call = (
        prompt_tokens / 1_000_000 * INPUT_PRICE_PER_MILLION
        + completion_tokens / 1_000_000 * OUTPUT_PRICE_PER_MILLION
    )
    print(f"  单次成本 ≈ {per_call:.6f} 元")
    print(f"  1000 次成本 ≈ {per_call * 1000:.4f} 元")
    if INPUT_PRICE_PER_MILLION == 0 and OUTPUT_PRICE_PER_MILLION == 0:
        print("  （单价还是 0，去平台查完填进脚本顶部两个变量再跑一次）")


def main() -> None:
    experiment_temperature()
    experiment_max_tokens()
    experiment_cost()


if __name__ == "__main__":
    main()