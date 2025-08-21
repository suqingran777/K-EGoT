import json
from openai import OpenAI
from get_prompt import matching_crition_prompt

"""
匹配安全性准则
"""

def get_response(prompt):
    
    messages = [{"role": "user", "content": prompt}]
    api_key = ""
    base_url = "https://open.bigmodel.cn/api/paas/v4/"
    model = "glm-4-flash"

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    
    return completion.choices[0].message.content


def clean_json(json_str):
    json_str = json_str.strip()
    clean_json_str = json_str.replace("```json", "").replace("```", "")
    clean_json_str = clean_json_str.strip()
    try:
        return json.loads(clean_json_str)
    except:
        return None
    

def matching(state_graph):
    safety_data = []
    with open("./safety_criterion_number.txt", "r") as read_safety:
        for i, line in enumerate(read_safety):
            safety_data.append(line.strip())

    MAX_RETRIES = 3
    res = None
    for attempt in range(MAX_RETRIES):
        matching_prompt = matching_crition_prompt(state_graph, safety_data)
        res = clean_json(get_response(matching_prompt))
        if res is not None:
            break
    return res
