import re

"""
图变迁中变量提取
同一变量中，min有可能比max还大
"""


def update_min_max(variables, var, op, value):

    """
    更新变量的最小值和最大值。

    根据操作符和值，更新变量字典中指定变量的最小值和最大值。
    如果操作符是"=="，则将最小值和最大值都设置为该值。
    如果操作符是">"、">="、"<"或"<="，则根据操作符更新最小值或最大值。

    参数:
    - variables: dict, 包含变量信息的字典，每个变量包含类型、最小值和最大值。
    - var: str, 需要更新的变量名。
    - op: str, 操作符，支持"=="、">"、">="、"<"、"<="。
    - value: str, 操作符右侧的值，可以是整数或浮点数。

    返回值:
    - 无返回值，直接修改传入的variables字典。
    """

    if op == "==":
        # max和min相等取固定值
        if variables[var]["type"] == "int":
            variables[var]["min"] = int(value)
            variables[var]["max"] = int(value)
        elif variables[var]["type"] == "float":
            variables[var]["min"] = float(value)
            variables[var]["max"] = float(value)
    else:
        if variables[var]["type"] == "float":
            value = float(value)
            if op in (">", ">="):
                if (
                    variables[var]["min"] is None
                    or (op == ">" and value > variables[var]["min"])
                    or (op == ">=" and value >= variables[var]["min"])
                ):
                    variables[var]["min"] = value
            elif op in ("<", "<="):
                if (
                    variables[var]["max"] is None
                    or (op == "<" and value < variables[var]["max"])
                    or (op == "<=" and value <= variables[var]["max"])
                ):
                    variables[var]["max"] = value
        else:
            value = int(value)
            if op in (">", ">="):
                if (
                    variables[var]["min"] is None
                    or (op == ">" and value > variables[var]["min"])
                    or (op == ">=" and value >= variables[var]["min"])
                ):
                    variables[var]["min"] = value
            elif op in ("<", "<="):
                if (
                    variables[var]["max"] is None
                    or (op == "<" and value < variables[var]["max"])
                    or (op == "<=" and value <= variables[var]["max"])
                ):
                    variables[var]["max"] = value


def formula_extra(formula, guard_type, tansition_id):

    """
    从公式中提取变量并更新其最小值和最大值。

    使用正则表达式匹配公式中的变量、操作符和值，并根据操作符和值更新变量的最小值和最大值。
    如果变量未在guard_type中定义，则抛出ValueError异常。

    参数:
    - formula: str, 包含变量、操作符和值的公式字符串。
    - guard_type: dict, 包含变量及其类型的字典。

    返回值:
    - variables: dict, 包含提取的变量及其类型、最小值和最大值的字典。

    异常:
    - ValueError: 如果公式中的变量未在guard_type中定义，则抛出此异常。
    """

    variables = {}
    # 匹配变量和值
    matches = re.findall(r"(\w+)\s*(==|>=|<=|>|<)\s*([\w.]+)", formula)
    for var, op, value in matches:
        if var not in guard_type:
            raise ValueError(f"Variable {var} is not defined in guard_type.")
        if var not in variables:
            alias = var + "_" + tansition_id
            variables[var] = {"type": guard_type[var], "min": -1000, "max": 1000, "alias": alias}

        update_min_max(variables, var, op, value)

    return variables


def path_var_exa(data):
    results = []
    transitions = data["transitions"]
    # 遍历每个变迁
    for transition in transitions:
        formula = transition["guard"]
        guard_type = transition["guard_type"]
        transition_id = transition["id"]
        variables = formula_extra(formula, guard_type, transition_id)
        for var, info in variables.items():
            results.append(
                {
                    "ori_name": var,
                    "name": info["alias"],
                    "type": info["type"],
                    "min": info["min"],
                    "max": info["max"],
                }
            )
    return results


if __name__ == "__main__":
    data = {"name": "机载电力系统状态图", "func_desc": "控制飞机电力生成、分配与故障保护", "states": [{"id": "S1", "name": "关闭状态", "description": "主电源未激活，备用电池维持基本系统", "level": 3, "out_action": "None", "timing": {"duration": 0, "start_time": 0}}, {"id": "S2", "name": "启动预热", "description": "APU或主引擎发电机启动预热过程", "level": 2, "out_action": "激活电压检测电路", "timing": {"duration": 30, "start_time": 0}}, {"id": "S3", "name": "正常运行", "description": "稳定输出400Hz 115/200V三相交流电", "level": 1, "out_action": "None", "timing": {"duration": 9999, "start_time": 30}}, {"id": "S4", "name": "故障保护", "description": "检测到电压异常时切断电路", "level": 4, "out_action": "激活备用电源", "timing": {"duration": 15, "start_time": 0}}], "transitions": [{"id": "T1", "from": "S1", "to": "S2", "guard": "engine_start == true", "description": "引擎启动信号触发电力系统初始化", "guard_type": {"engine_start": "bool"}, "timing": {"trigger_time": 0}}, {"id": "T2", "from": "S2", "to": "S3", "guard": "voltage_stable == true && frequency_error < 0.5", "description": "电压稳定后进入正常工作模式", "guard_type": {"voltage_stable": "bool", "frequency_error": "float"}, "timing": {"trigger_time": 30}}, {"id": "T3", "from": "S3", "to": "S4", "guard": "voltage_value > 250 || voltage_value < 80", "description": "电压超限触发保护机制", "guard_type": {"voltage_value": "float"}, "timing": {"trigger_time": 0}}, {"id": "T4", "from": "S4", "to": "S2", "guard": "manual_reset == true", "description": "地面维护人员执行系统重置", "guard_type": {"manual_reset": "bool"}, "timing": {"trigger_time": 15}}]}
    print(path_var_exa(data))
