from openai import OpenAI
import json
import re

def get_response(prompt, api_type="huoshan", reason=False):

    """
    根据给定的提示信息和 API 类型，从指定的模型获取响应。

    参数:
        prompt (str): 发送给模型的提示信息。
        api_type (str, 可选): API 的类型，默认为 "huoshan"。支持的类型有 "huoshan" 和 "zhipu"。
        reason (bool, 可选): 是否为推理，默认为 False。

    返回:
        str: 模型生成的响应内容。

    说明:
        此函数根据 `api_type` 参数选择不同的 API 配置，使用 OpenAI 客户端与相应的模型进行交互，
        并返回模型生成的响应。目前支持的 API 类型有 "huoshan" 和 "zhipu"，分别对应不同的 API 密钥、
        基础 URL 和模型名称。
    """
    
    messages = [{"role": "user", "content": prompt}]
    if api_type == "huoshan":
        api_key = ""
        base_url = "https://ark.cn-beijing.volces.com/api/v3"
        model = "ep-20250225100445-2mvwq"
    elif api_type == "zhipu":
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
    if reason:
        return completion.choices[0].message
    else:
        return completion.choices[0].message.content

def clean_json(json_str):
    """
    清理和解析 JSON 字符串

    参数:
        json_str (str): 需要清理和解析的 JSON 字符串。

    功能:
        1. 去除字符串两端的空白字符。
        2. 移除字符串中的 ```json 和 ``` 标记。
        3. 再次去除清理后的字符串两端的空白字符。
        4. 尝试将清理后的字符串解析为 JSON 对象。
        5. 如果解析成功，返回解析后的 JSON 对象。
        6. 如果解析失败，捕获异常并返回 `None`。

    返回值:
        dict 或 None: 解析后的 JSON 对象，或者在解析失败时返回 `None`。
    """
    # 使用正则表达式提取 JSON 内容
    match = re.search(r'```json(.*?)```', json_str, re.DOTALL)
    if match:
        clean_json_str = match.group(1).strip()
    else:
        clean_json_str = json_str.strip()
    try:
        return json.loads(clean_json_str)
    except:
        return None


def replace_bool(variables):
    """
    将字典中的字符串形式的布尔值转换为Python布尔类型
    
    参数:
        variables (dict): 包含键值对的字典，其中值可能是字符串形式的布尔值("True"/"False")
        
    返回:
        dict: 处理后的字典，其中字符串形式的布尔值已被转换为对应的Python布尔类型
        
    示例:
        >>> replace_bool({"flag": "True", "enabled": "False"})
        {'flag': True, 'enabled': False}
    """
    for key, value in variables.items():
        if value == "True":
            variables[key] = True
        elif value == "False":
            variables[key] = False
    return variables