import networkx as nx
import re

"""
状态图运行
"""

def change_guard(guard, transition_id):
    
    """
    根据给定的状态变迁 ID 为守卫条件中的变量添加别名。

    此函数会识别守卫条件中的变量，并为每个变量添加状态变迁 ID 作为后缀，
    以创建变量的别名，从而避免不同状态变迁中变量名的冲突。

    参数:
    - guard: str, 状态变迁的守卫条件，通常是一个逻辑表达式。
    - transition_id: str, 状态变迁的 ID，用于为变量生成别名。

    返回值:
    - str, 经过处理后的守卫条件，其中的变量已被替换为带别名的形式。

    示例:
    >>> change_guard("engine_start == true", "T1")
    "engine_start_T1 == true"
    """
    
    matches = re.findall(r"(\w+)\s*(==|>=|<=|>|<)\s*([\w.]+)", guard)
    alias_dict = {}
    for var, _, _ in matches:
        alias = var + "_" + transition_id
        alias_dict[var] = alias_dict.get(var, alias)
    for var, alias in alias_dict.items():
        guard = guard.replace(var, alias)
    return guard

def convert_to_networkx(data, add_id=False):
    """
    将给定的状态图数据转换为NetworkX有向图（DiGraph）对象。

    该函数接受一个包含状态和状态变迁的字典数据，并将其转换为NetworkX有向图。每个状态被转换为图中的一个节点，
    每个状态变迁被转换为图中的一条边。节点和边都包含从原始数据中提取的附加信息。

    参数:
    - data: dict, 包含状态图数据的字典。字典应包含以下键：
        - "states": list, 状态列表，每个状态是一个包含"id", "name", "description", "level", "out_action", "timing"等键的字典。
        - "transitions": list, 状态变迁列表，每个变迁是一个包含"from", "to", "id", "guard", "description", "guard_type", "timing"等键的字典。
    - add_id: bool, 如果为True，则将状态变迁的id添加到节点的属性中。默认为False。
    返回值:
    - graph: nx.DiGraph, 表示状态图的NetworkX有向图对象。图中的节点和边包含从原始数据中提取的附加信息。

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
        if add_id:
            guard = change_guard(transition["guard"], transition["id"])
        else:
            guard = transition["guard"]
        graph.add_edge(
            from_node,
            to_node,
            id=transition["id"],
            guard=guard,
            description=transition["description"],
            guard_type=transition["guard_type"],
            timing=transition["timing"],
        )

    return graph


def evaluate_guard(guard, vars):
    """
    评估状态变迁的守卫条件（guard）。

    将守卫条件中的布尔值表示方式（true/false）替换为Python的布尔值表示方式（True/False），
    并在传入的变量命名空间中评估守卫条件。如果评估成功，返回布尔值结果；如果评估失败，返回False。

    参数:
    - guard: str, 状态变迁的守卫条件，通常是一个逻辑表达式。
    - vars: dict, 包含变量及其值的字典，用于在评估守卫条件时提供上下文。

    返回值:
    - bool, 守卫条件的评估结果。如果评估失败，返回False。

    示例:
    >>> evaluate_guard("engine_start == true", {"engine_start": True})
    True
    >>> evaluate_guard("voltage_value > 250", {"voltage_value": 200})
    False
    >>> evaluate_guard("voltage_value > 250", {"voltage_value": 300})
    True
    >>> evaluate_guard("voltage_stable == true && frequency_error < 0.5",
                    {"voltage_stable": True, "frequency_error": 0.3})
    True
    """
    try:
        guard = guard.replace("true", "True").replace("false", "False")
        guard = guard.replace("&&", "and").replace("||", "or")
        namespace = vars.copy()
        return bool(eval(guard, {"__builtins__": None}, namespace))
    except Exception:
        return False

# 注释函数是返回最深的覆盖路径
# def dfs(graph, vars, current_state, current_path, visited_edges, max_path):
#     """
#     使用深度优先搜索（DFS）遍历状态图，寻找能够满足守卫条件的最长路径。

#     该函数从当前状态开始，递归地遍历每个状态的所有出边，评估守卫条件，并记录最长的路径。
#     如果某个状态没有满足守卫条件的变迁，则停止当前路径的探索。

#     参数:
#     - graph: nx.DiGraph, 表示状态图的NetworkX有向图对象。该图包含多个节点（状态）和边（状态变迁），每个节点和边都包含附加信息。
#     - vars: dict, 包含变量及其值的字典，用于在评估守卫条件时提供上下文。这些变量将用于替换守卫条件中的占位符。
#     - current_state: str, 当前状态的ID。
#     - current_path: list, 当前路径中的状态变迁ID列表。
#     - visited_edges: set, 已访问的状态变迁ID集合，用于避免重复访问。
#     - max_path: list of list, 存储最长路径的列表。由于Python的可变对象特性，使用列表的列表来传递和更新最长路径。

#     返回值:
#     - 无返回值。函数通过修改 `max_path` 列表来记录最长路径。
#     """
#     found_transition = False

#     for _, next_state, edge_data in graph.edges(current_state, data=True):
#         guard = edge_data["guard"]
#         edge_id = edge_data["id"]

#         if edge_id not in visited_edges and evaluate_guard(guard, vars):
#             found_transition = True
#             new_path = current_path + [edge_id]
#             new_visited = visited_edges.copy()
#             new_visited.add(edge_id)
#             dfs(graph, vars, next_state, new_path, new_visited, max_path)

#     if not found_transition:
#         if len(current_path) > len(max_path[0]):
#             max_path[0] = current_path


# def graph_cover(graph, vars):
#     """
#     计算状态图中从初始状态出发能够满足守卫条件的最长路径。

#     该函数通过调用深度优先搜索（DFS）算法，遍历状态图的所有可能路径，并返回其中满足守卫条件的最长路径及其长度。

#     参数:
#     - graph: nx.DiGraph, 表示状态图的NetworkX有向图对象。包含多个节点（状态）和边（状态变迁），每个节点和边都包含附加信息。
#     - vars: dict, 包含变量及其值的字典，用于在评估守卫条件时提供上下文。

#     返回值:
#     - tuple: 
#       - 第一个元素为列表，表示最长路径中的状态变迁ID序列。
#       - 第二个元素为整数，表示最长路径的长度。
#     """
#     max_path = [[]]
#     initial_state = list(graph.nodes())[0]
#     dfs(graph, vars, initial_state, [], set(), max_path)
#     print(max_path)
#     return max_path[0], len(max_path[0])

def dfs(graph, vars, current_state, visited_edges, covered_edges):
    """
    使用深度优先搜索(DFS)遍历状态图，统计能够满足守卫条件的变迁数量。

    参数:
    - graph: nx.DiGraph, 表示状态图的NetworkX有向图对象
    - vars: dict, 包含变量及其值的字典，用于评估守卫条件
    - current_state: str, 当前状态的ID
    - visited_edges: set, 已访问的状态变迁ID集合
    - covered_edges: set, 已覆盖的状态变迁ID集合(会被修改)

    返回值:
    - 无返回值。函数通过修改covered_edges集合来记录覆盖的变迁
    """
    for _, next_state, edge_data in graph.edges(current_state, data=True):
        guard = edge_data["guard"]
        edge_id = edge_data["id"]

        if edge_id not in visited_edges and evaluate_guard(guard, vars):
            covered_edges.add(edge_id)
            new_visited = visited_edges.copy()
            new_visited.add(edge_id)
            dfs(graph, vars, next_state, new_visited, covered_edges)

def graph_cover(graph, vars):
    """
    计算状态图中从初始状态出发能够满足守卫条件的变迁覆盖数量。

    参数:
    - graph: nx.DiGraph, 表示状态图的NetworkX有向图对象
    - vars: dict, 包含变量及其值的字典，用于评估守卫条件

    返回值:
    - tuple: 
      - 第一个元素为集合，表示被覆盖的变迁ID集合
      - 第二个元素为整数，表示被覆盖的变迁数量
    """
    covered_edges = set()
    initial_state = list(graph.nodes())[0]
    dfs(graph, vars, initial_state, set(), covered_edges)
    return covered_edges, len(covered_edges)

def guard_extra(graph):
    """
    提取状态图中所有的守卫条件，并将其组合成一个字符串。
    该函数遍历状态图的所有边，提取每条边的守卫条件，并将其组合成一个字符串。
    守卫条件之间使用空格分隔。
    """
    guards = []
    for _, _, edge_data in graph.edges(data=True):
        transition_id = edge_data["id"]
        guard = edge_data["guard"]
        # guard = change_guard(guard, transition_id)
        if edge_data["guard_type"]:
            guard_type = {f"{k}_{transition_id}": v for k, v in edge_data["guard_type"].items()}
        else:
            guard_type = {}
        guard = guard + " 变量类型为：" + str(guard_type)
        guards.append(guard)
    return "\n".join(guards)



if __name__ == "__main__":

    data = {
        "name": "机载电力系统状态图",
        "func_desc": "控制飞机电力生成、分配与故障保护",
        "states": [
            {
                "id": "S1",
                "name": "关闭状态",
                "description": "主电源未激活",
                "level": 3,
                "out_action": "None",
                "timing": {"duration": 0, "start_time": 0},
            },
            {
                "id": "S2",
                "name": "启动预热",
                "description": "APU或主引擎发电机启动预热过程",
                "level": 2,
                "out_action": "激活电压检测电路",
                "timing": {"duration": 30, "start_time": 0},
            },
            {
                "id": "S3",
                "name": "正常运行",
                "description": "稳定输出400Hz 115/200V三相交流电",
                "level": 1,
                "out_action": "None",
                "timing": {"duration": 9999, "start_time": 30},
            },
            {
                "id": "S4",
                "name": "故障保护",
                "description": "检测到电压异常时切断电路",
                "level": 4,
                "out_action": "激活备用电源",
                "timing": {"duration": 15, "start_time": 0},
            },
        ],
        "transitions": [
            {
                "id": "T1",
                "from": "S1",
                "to": "S2",
                "guard": "engine_start == true",
                "description": "引擎启动信号触发电力系统初始化",
                "guard_type": {"engine_start": "bool"},
                "timing": {"trigger_time": 0},
            },
            {
                "id": "T2",
                "from": "S2",
                "to": "S3",
                "guard": "voltage_stable == true && frequency_error < 0.5",
                "description": "电压稳定后进入正常工作模式",
                "guard_type": {"voltage_stable": "bool", "frequency_error": "float"},
                "timing": {"trigger_time": 30},
            },
            {
                "id": "T3",
                "from": "S3",
                "to": "S4",
                "guard": "voltage_value > 250 || voltage_value < 80",
                "description": "电压超限触发保护机制",
                "guard_type": {"voltage_value": "float"},
                "timing": {"trigger_time": 0},
            },
            {
                "id": "T4",
                "from": "S4",
                "to": "S2",
                "guard": "manual_reset == true",
                "description": "地面维护人员执行系统重置",
                "guard_type": {"manual_reset": "bool"},
                "timing": {"trigger_time": 15},
            },
            {
                "id": "T5",
                "from": "S2",
                "to": "S4",
                "guard": "voltage_value > 150 || voltage_value < 80",
                "description": "预热阶段电压异常触发故障保护",
                "guard_type": {"voltage_value": "float"},
                "timing": {"trigger_time": 0},
            },
        ],
    }

    vars = {
        "engine_start": True,
        "voltage_stable": True,
        "frequency_error": 0.3,
        "voltage_value": 200,
        "manual_reset": True,
    }
    graph = convert_to_networkx(data, add_id=False)

    print(guard_extra(graph))
    