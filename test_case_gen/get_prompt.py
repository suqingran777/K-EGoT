from re import template


def good_mutition_prompt(state_graph, variables):
    template = f"""
根据提供的json格式的状态图和遗传算法生成的状态图中每个变迁guard条件变量对应的变量值，使用大模型去替代遗传算法的变异过程，将遗传算法生成的变量值朝好的方向变异。
尽可能的使变量符合变迁上的守卫条件，使状态图中的每个变迁都能得到满足，对于数值变量类型的，尽量不要选取边界值，例如fuel_quantity < 300，fuel_quantity选值为285。
最后以json格式输出变异后的变量名和其对应的值。
json格式的状态图如下：
<state>
{state_graph}
</state>
然后，查看以下已有的状态图中每个变迁变量对应的变量值：
<variables>
{variables}
</variables>
在使用大模型进行变异时，请按照以下步骤操作：
1. 分析状态图，理解每个变迁变量的含义和作用。
2. 基于状态图和现有遗传算法的变量值，使用大模型评估每个变量当前取值对整体状态的影响。
3. 利用大模型的能力，尝试对变量值进行调整，使得状态朝更好的方向发展。这里的“更好”可以理解为更符合状态图所代表的系统的预期目标或性能要求。
4. 多次尝试不同的调整，通过大模型评估每次调整后的效果，选择最优的变异结果。
5. 最后，以json格式输出变异后的变量名和其对应的值，其中对于True和False使用字符串替代。

<results>
```json
{{"variable1": "value1", "variable2": "value2", ...}}
</results>
    注意：不要给出解释，只给出json格式的结果。
    """
    return template

def variables_prompt(condition):
    template = f"""
你的任务是根据给出的条件，给出符合变量范围内的值，并以JSON格式输出。
首先，请仔细阅读以下变量的取值条件：
<condition>
{condition}
</condition>
取值时，请按照以下方法进行：
1. 仔细分析条件，确定变量的取值范围。
2. 根据变量类型，在取值范围内选取合适的值。
3. 以JSON格式输出符合条件的值，JSON对象的键为变量名，变量名严格从给定的条件中提取，不要更改变量名称，值为符合条件的变量值。
<results>
```json
{{"variable1": "value1", "variable2": "value2", ...}}
</results>
举例如下：
<condition>
fuel_quantity_T1 <= 300 {{'fuel_quantity': 'float'}}
leak_detected_T3 == true {{'leak_detected': 'bool'}}
fuel_quantity_T2 <= 50 {{'fuel_quantity': 'float'}}
timeout_T5 == true {{'timeout': 'bool'}}
fuel_quantity_T8 > 50 && leak_detected_T8 == false {{'fuel_quantity': 'float', 'leak_detected': 'bool'}}
maintenance_done_T4 == true {{'maintenance_done': 'bool'}}
fuel_quantity_T6 <= 50 {{'fuel_quantity': 'float'}}
fuel_quantity_T7 > 50 {{'fuel_quantity': 'float'}}
</condition>
输出为：
```json
{{"fuel_quantity_T1": 100.0, "leak_detected_T3": "True", "fuel_quantity_T2": 30.0, "timeout_T5": "True", "fuel_quantity_T8": 60.0, "leak_detected_T8": "False", "maintenance_done_T4": "True", "fuel_quantity_T6": 20.0, "fuel_quantity_T7": 70.0}}
```
    注意：不要给出解释，只给出json格式的结果，变量名严格从给定的条件中提取，不要更改变量名称。
"""
    return template

if __name__ == "__main__":
    print(good_mutition_prompt(None, None))