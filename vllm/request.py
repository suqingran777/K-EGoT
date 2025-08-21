from openai import OpenAI

def extract_thoughts(text):
    thinking_content = ""
    thinking_content = text.split("<think>")[-1].split("</think>")[0].strip()
    content = text.split("</think>")[1].strip()
    return thinking_content, content

def request_finetue_model(content, enable_thinking=False):

    openai_api_key = "EMPTY"
    openai_api_base = "http://localhost:10062/v1"

    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_api_base,
    )

    model_name="../Qwen/Qwen3-8B"
    messages=[
        {"role": "user", "content": content},
    ]

    chat_response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=8192,
        temperature=0.7,
        top_p=0.8,
        presence_penalty=1.5,
        extra_body={
            "top_k": 20, 
            "chat_template_kwargs": {"enable_thinking": enable_thinking},
        },
    )
    if enable_thinking:
        return extract_thoughts(chat_response.choices[0].message.content)
    else:
        return chat_response.choices[0].message.content

if __name__ == "__main__":
    print(request_finetue_model("你好",True))