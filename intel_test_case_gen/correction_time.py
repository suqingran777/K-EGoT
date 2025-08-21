import networkx as nx
import json

def setup_initial_state_and_duration(json_data, start_id):

    for state in json_data['states']:
        if state['id'] == start_id:
            state['timing']['start_time'] = 0
        if state['timing']['duration'] == 0:
            state['timing']['duration'] = 1000

def convert_to_networkx(data):
    """
    将给定的状态图数据转换为NetworkX有向图（DiGraph）对象。
    """

    graph = nx.DiGraph()

    # 添加节点
    for state in data["states"]:
        node_id = state["id"]
        graph.add_node(
            node_id,
            name=state["name"],
            description=state["description"],
            level=state["level"],
            out_action=state["out_action"],
            timing=state["timing"],
        )

    # 添加边
    for transition in data["transitions"]:
        from_node = transition["from"]
        to_node = transition["to"]
        graph.add_edge(
            from_node,
            to_node,
            id=transition["id"],
            guard=transition["guard"],
            description=transition["description"],
            guard_type=transition["guard_type"],
            timing=transition["timing"],
        )

    return graph

def get_all_paths(graph, start, end):
    paths = list(nx.all_simple_paths(graph, start, end))
    return paths


def get_timing_duration(graph, state_id):
    """
    获取指定状态中timing对应的duration字段值
    """
    node_attributes = graph.nodes.get(state_id)
    if node_attributes and 'timing' in node_attributes and 'duration' in node_attributes['timing']:
        return node_attributes['timing']['duration']
    return None


def cal_min_time(paths, graph):
    times = []
    for path in paths:
        start_time = 0
        for state_id in path[:-1]:
            duration = get_timing_duration(graph, state_id)
            start_time += duration
        times.append(start_time)
    return min(times)

def change_states_time(graph_data, start_id):
    
    states = graph_data["states"]
    for state in states:
        state_id = state["id"]
        if state_id == start_id:
            continue
        setup_initial_state_and_duration(graph_data, start_id)
        graph_nex = convert_to_networkx(graph_data)
        paths = get_all_paths(graph_nex, start_id, state_id)
        state_min_time = cal_min_time(paths, graph_nex)
        state['timing']['start_time'] = state_min_time
    return graph_data

# 示例用法
if __name__ == "__main__":
    graph_data = {"name": "燃油系统状态图(安全扩展)", "func_desc": "管理飞机燃油存储、供给和应急处理", "states": [{"id": "S1", "name": "正常供油状态", "description": "燃油量充足，主副油箱正常工作", "level": 1, "out_action": "启动流量监控", "timing": {"duration": 3600, "start_time": 0}}, {"id": "S2", "name": "低油量警告状态", "description": "剩余燃油低于标准阈值", "level": 3, "out_action": "激活备用泵", "timing": {"duration": 600, "start_time": 3600}}, {"id": "S3", "name": "紧急储备状态", "description": "仅保留应急燃油供应", "level": 4, "out_action": "发送迫降信号", "timing": {"duration": 300, "start_time": 4200}}, {"id": "S4", "name": "系统故障状态", "description": "燃油泄漏或泵体失效", "level": 4, "out_action": "切断供油管路", "timing": {"duration": 0, "start_time": 0}}, {"id": "S5", "name": "低油量超时处理状态", "description": "处理S2超时后的燃油量检查，决定后续状态", "level": 3, "out_action": "检查剩余燃油量并执行相应操作", "timing": {"duration": 0, "start_time": 0}, "crition": "68. 工作状态运行超时,导致功能执行异常"}], "transitions": [{"id": "T1", "from": "S1", "to": "S2", "guard": "fuel_quantity <= 300", "description": "燃油量低于300升触发告警", "guard_type": {"fuel_quantity": "float"}, "timing": {"trigger_time": 3600}, "priority": 2, "crition": "74. 同一状态向多个状态的转移条件同时满足"}, {"id": "T2", "from": "S2", "to": "S3", "guard": "fuel_quantity <= 50", "description": "燃油量低于50升进入紧急模式", "guard_type": {"fuel_quantity": "float"}, "timing": {"trigger_time": 0}}, {"id": "T3", "from": "S1", "to": "S4", "guard": "leak_detected == true", "description": "检测到燃油泄漏立即隔离系统", "guard_type": {"leak_detected": "bool"}, "timing": {"trigger_time": 0}, "priority": 1, "crition": "74. 同一状态向多个状态的转移条件同时满足"}, {"id": "T4", "from": "S4", "to": "S1", "guard": "maintenance_done == true", "description": "完成维修后重置系统", "guard_type": {"maintenance_done": "bool"}, "timing": {"trigger_time": 0}}, {"id": "T5", "from": "S2", "to": "S5", "guard": "timeout == true", "description": "S2超时后强制进入处理状态", "guard_type": {"timeout": "bool"}, "timing": {"trigger_time": 4200}, "crition": "68. 工作状态运行超时,导致功能执行异常"}, {"id": "T6", "from": "S5", "to": "S3", "guard": "fuel_quantity <= 50", "description": "超时处理后燃油量仍低于50升，进入紧急模式", "guard_type": {"fuel_quantity": "float"}, "timing": {"trigger_time": 0}}, {"id": "T7", "from": "S5", "to": "S1", "guard": "fuel_quantity > 50", "description": "超时处理后燃油量恢复，返回正常供油", "guard_type": {"fuel_quantity": "float"}, "timing": {"trigger_time": 0}}, {"id": "T8", "from": "S3", "to": "S1", "guard": "fuel_quantity > 50 && leak_detected == false", "description": "燃油量恢复且无泄漏，返回正常供油状态", "guard_type": {"fuel_quantity": "float", "leak_detected": "bool"}, "timing": {"trigger_time": 0}, "crition": "43. 某个判定分支缺少相应的处理逻辑"}]}

    graph_data = change_states_time(graph_data, "S1")
    print(graph_data)
    