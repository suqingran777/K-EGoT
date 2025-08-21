import json
from get_prompt import graph_extension_prompt
from matching_crition import matching, clean_json, get_response
from correction_time import change_states_time

"""
状态图扩展
"""

def merge_crition(res):
    """
    合并匹配的安全性准则及其原因

    参数:
        res (dict): 包含安全性准则和原因的字典，格式如下：
                    {
                        "critions": ["准则1", "准则2", ...],
                        "reason": ["原因1", "原因2", ...]
                    }

    功能:
        1. 检查输入的 `res` 是否为 `None`。
        2. 如果 `res` 不为 `None`，提取 `critions` 和 `reason` 列表。
        3. 将每个准则与其对应的原因合并成一个字符串，格式为 "准则：原因\n"。
        4. 返回合并后的字符串。

    返回值:
        str 或 None: 合并后的准则及其原因字符串，或者在输入为 `None` 时返回 `None`。
    """
    crition_reason = ""
    if res is not None:
        critions = res["critions"]
        reasons = res["reason"]
        for i in range(min(len(critions), len(reasons))):
            crition_reason += f"{critions[i]}：{reasons[i]}\n"
        return crition_reason
    return None


def data_fileter():
    
    graph_data = {"name": "燃油系统状态图", "func_desc": "管理飞机燃油存储、供给和应急处理", "states": [{"id": "S1", "name": "正常供油状态", "description": "燃油量充足，主副油箱正常工作", "level": 1, "out_action": "启动流量监控", "timing": {"duration": 3600, "start_time": 0}}, {"id": "S2", "name": "低油量警告状态", "description": "剩余燃油低于标准阈值", "level": 3, "out_action": "激活备用泵", "timing": {"duration": 600, "start_time": 3600}}, {"id": "S3", "name": "紧急储备状态", "description": "仅保留应急燃油供应", "level": 4, "out_action": "发送迫降信号", "timing": {"duration": 300, "start_time": 4200}}, {"id": "S4", "name": "系统故障状态", "description": "燃油泄漏或泵体失效", "level": 4, "out_action": "切断供油管路", "timing": {"duration": 0, "start_time": 0}}], "transitions": [{"id": "T1", "from": "S1", "to": "S2", "guard": "fuel_quantity <= 300", "description": "燃油量低于300升触发告警", "guard_type": {"fuel_quantity": "float"}, "timing": {"trigger_time": 3600}}, {"id": "T2", "from": "S2", "to": "S3", "guard": "fuel_quantity <= 50", "description": "燃油量低于50升进入紧急模式", "guard_type": {"fuel_quantity": "float"}, "timing": {"trigger_time": 4200}}, {"id": "T3", "from": "S1", "to": "S4", "guard": "leak_detected == true", "description": "检测到燃油泄漏立即隔离系统", "guard_type": {"leak_detected": "bool"}, "timing": {"trigger_time": 0}}, {"id": "T4", "from": "S4", "to": "S1", "guard": "maintenance_done == true", "description": "完成维修后重置系统", "guard_type": {"maintenance_done": "bool"}, "timing": {"trigger_time": 0}}], "graph_id": "8121f8fd"}
    
    return graph_data


def graph_extension(graph_extention_file_path):
        state_graph = data_fileter()
        state_graph = json.dumps(state_graph, ensure_ascii=False)
        
        MAX_RETRIES = 3
        extention_graph = None
        
        for attempt in range(MAX_RETRIES):
            crition_reason_dict = matching(state_graph)
            if crition_reason_dict is None:
                continue
                
            crition_reason = merge_crition(crition_reason_dict)
            extention_prompt = graph_extension_prompt(state_graph, crition_reason)
            results = get_response(extention_prompt)
            extention_graph = clean_json(results)
            if extention_graph is not None:
                break
        
        if extention_graph is not None:
            start_id = extention_graph["states"][0]["id"]
            extention_graph = change_states_time(extention_graph, start_id)
            with open(graph_extention_file_path, "w") as extention_file:
                extention_file.write(json.dumps(extention_graph, ensure_ascii=False) + "\n")
        else:
            print("状态图生成失败")

if __name__ == "__main__":
    graph_extention_file_path = "graph_extention.jsonl"
    graph_extension(graph_extention_file_path)
