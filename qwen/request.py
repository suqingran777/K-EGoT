import requests
import json

def request(prompt, enable_thinking=False):
    api_url = "http://127.0.0.1:10062/generate"

    payload_simple = {
        "prompt": prompt,
        "enable_thinking": enable_thinking,
    }

    try:
        response_simple = requests.post(api_url, json=payload_simple)
        response_data_simple = response_simple.json()

        if enable_thinking:
            thinking_content = response_data_simple["thinking_content"]
            content = response_data_simple["content"]
            return thinking_content, content
        else:
            content = response_data_simple["content"]
            return content

    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")

if __name__ == "__main__":
    print(request("请写一首关于秋天的五言绝句。"))

# from openai import OpenAI
# # Set OpenAI's API key and API base to use vLLM's API server.
# openai_api_key = "EMPTY"
# openai_api_base = "http://localhost:8000/v1"

# client = OpenAI(
#     api_key=openai_api_key,
#     base_url=openai_api_base,
# )

# chat_response = client.chat.completions.create(
#     model="Qwen/Qwen3-8B",
#     messages=[
#         {"role": "user", "content": "Give me a short introduction to large language models."},
#     ],
#     max_tokens=32768,
#     temperature=0.6,
#     top_p=0.95,
#     extra_body={
#         "top_k": 20,
#     },
# )
# print("Chat response:", chat_response)
