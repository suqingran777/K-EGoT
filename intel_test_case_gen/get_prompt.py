def graph_extension_prompt(state_graph, crition):
    template = f"""
你的任务是根据给定的不匹配的安全性准则和对应原因，对json格式的状态图进行扩展，使其满足这些安全性准则，并将扩展后的状态图以原有json格式输出（在新扩展的状态上添加crition字段，表示符合某个安全性准则）。
原始状态图的json数据如下：
{state_graph}
不匹配的安全性准则和原因如下：
<crition_reason>
{crition}
</crition_reason>
在扩展状态图时，请按照以下步骤进行：
1. 仔细分析不匹配的安全性准则和原因，明确需要改进的方向。
2. 针对每个不匹配的情况，在状态图中添加或修改相应的状态、转换或属性，以满足安全性准则。
3. 确保扩展后的状态图仍然符合json格式，并且结构清晰、逻辑合理。
4. 注意字段timing中，duration、start_time、trigger_time的合理性，确保上下时间的逻辑

<results>
```json
[在此输出扩展后的状态图的json数据]
```
</results>
在新扩展的状态上添加crition字段(例如："crition":"74. 同一状态向多个状态的转移条件同时满足")，表示符合某个安全性准则
"""
    return template


def matching_crition_prompt(state_graph, crition):
    template = f"""
你的任务是分析给定的状态图，找出它不满足安全性准则的地方，并取出最不满足的三条，同时给出不满足的原因，最终以json格式返回结果。
请仔细阅读以下状态图：
<state_graph>
{state_graph}
</state_graph>
以及以下安全性准则：
<安全性准则>
{crition}
</安全性准则>
在分析状态图时，请按照以下步骤进行：
1. 仔细研究状态图和安全性准则。
2. 逐一检查状态图中的各个元素是否满足安全性准则，记录不满足的情况及对应的准则。
3. 对不满足的情况进行评估，确定不满足程度，选出最不满足的三条。
4. 针对选出的三条不满足情况，详细分析不满足的原因。
在<think>标签中详细分析状态图不满足安全性准则的情况，包括筛选出最不满足的三条的过程以及每条不满足的原因。然后在<回答>标签中以json格式输出结果，json的结构如下：
{{
    "critions": ["准则1", "准则2", "准则3"],
    "reason": ["不满足准则1的原因", "不满足准则2的原因", "不满足准则3的原因"]
}}
<result>
```json
{{
    "critions": [],
    "reason": []
}}
```
</result>
请确保分析客观准确，输出格式符合要求。
"""
    return template