import random
from get_prompt import variables_prompt
from my_utils import get_response, clean_json, replace_bool
from graph_run import guard_extra

def mutate_bit_flip(individual, vars, mutation_rate):
    """基本位变异 - 随机翻转变量值"""
    mutated = individual.copy()
    for var in vars:
        if random.random() < mutation_rate:
            name = var["name"]
            if isinstance(mutated[name], bool):
                mutated[name] = not mutated[name]  # 布尔值取反
            elif isinstance(mutated[name], (int, float)):
                mutated[name] = -mutated[name]  # 数值取反
    return mutated

def mutate_uniform(individual, vars, mutation_rate):
    """均匀变异 - 随机重置变量值"""
    mutated = individual.copy()
    for var in vars:
        if random.random() < mutation_rate:
            name = var["name"]
            type_ = var["type"]
            if type_ == "bool":
                mutated[name] = random.choice([True, False])
            elif type_ == "int":
                mutated[name] = random.randint(-1000, 1000)
            elif type_ == "float":
                mutated[name] = random.uniform(-1000.0, 1000.0)
    return mutated

def mutate_gaussian(individual, vars, mutation_rate, sigma=0.1):
    """高斯变异 - 对数值变量添加高斯噪声"""
    mutated = individual.copy()
    for var in vars:
        if random.random() < mutation_rate:
            name = var["name"]
            type_ = var["type"]
            if type_ == "int":
                mutated[name] += int(random.gauss(0, sigma) * 100)
            elif type_ == "float":
                mutated[name] += random.gauss(0, sigma)
    return mutated

def mutate_swap(individual, vars, mutation_rate):
    """交换变异 - 随机交换两个变量的值"""
    if random.random() < mutation_rate and len(vars) >= 2:
        var1, var2 = random.sample(vars, 2)
        name1, name2 = var1["name"], var2["name"]
        if var1["type"] == var2["type"]:  # 只有类型相同才交换
            individual[name1], individual[name2] = individual[name2], individual[name1]
    return individual

def mutate_model(individual, mutation_rate, graph):
    """变异操作"""
    mutated = individual.copy()
    if random.random() < mutation_rate:
        guards = guard_extra(graph)
        mutition_promt = variables_prompt(guards)
        response = get_response(mutition_promt, api_type="zhipu")
        res = clean_json(response)
        if res is None:
            return mutated
        mutated = replace_bool(res)
    return mutated

def adaptive_directed_mutation(individual, vars, prev_fitness, prev_prev_fitness, 
                              prev_individual, prev_prev_individual, mutation_rate):
    """
    自适应定向变异操作
    
    参数:
        individual: dict - 当前个体(测试用例)
        vars: list - 变量信息列表
        prev_fitness: float - 上一代个体适应度
        prev_prev_fitness: float - 上上代个体适应度
        prev_individual: dict - 上一代个体
        prev_prev_individual: dict - 上上代个体
        mutation_rate: float - 变异概率
        
    返回值:
        dict - 变异后的个体
    """
    def sign(x):
        return 1 if x > 0 else (-1 if x < 0 else 0)

    mutated = individual.copy()
    
    # 计算适应度变化
    df1 = prev_fitness - prev_prev_fitness
    df2 = current_fitness - prev_fitness  # 需要从外部传入current_fitness
    
    for var in vars:
        if random.random() < mutation_rate:
            name = var["name"]
            type_ = var["type"]
            min_val = var.get("min", -1000)
            max_val = var.get("max", 1000)
            
            val = individual[name]
            prev_val = prev_individual[name]
            prev_prev_val = prev_prev_individual[name]
            
            dx1 = prev_val - prev_prev_val
            dx2 = val - prev_val
            
            if type_ in ["int", "float"]:
                if df1 * df2 > 0:
                    if dx1 * dx2 > 0:
                        new_val = val + sign(df2) * dx2 * mutation_rate
                    elif dx1 * dx2 < 0:
                        new_val = val + abs(dx2) * random.uniform(-1, 1) * mutation_rate
                    else:
                        new_val = val + val * random.uniform(-1, 1) * mutation_rate
                elif df1 * df2 < 0:
                    if current_fitness >= (prev_fitness + prev_prev_fitness + current_fitness)/3:
                        new_val = val + sign(df2) * dx2 * mutation_rate
                    elif dx1 * dx2 < 0:
                        new_val = val + abs(dx2) * random.uniform(-1, 1) * mutation_rate
                    else:
                        new_val = val + val * random.uniform(-1, 1) * mutation_rate
                else:
                    if df1 == 0 and df2 != 0:
                        new_val = val + sign(df2) * dx2 * mutation_rate
                    elif df1 != 0 and df2 == 0:
                        new_val = val + abs(dx2) * random.uniform(-1, 1) * mutation_rate
                    else:
                        if random.random() < 0.5:
                            new_val = val + (max_val - val) * random.uniform(-1, 1) * mutation_rate
                        else:
                            new_val = val + (val - min_val) * random.uniform(-1, 1) * mutation_rate
                
                # 确保值在合理范围内
                new_val = max(min_val, min(max_val, new_val))
                if type_ == "int":
                    new_val = int(new_val)
                mutated[name] = new_val
                
    return mutated

def run_mutation(individual, vars, graph, mutation_type, mutation_rate=0.01):
    """运行不同的变异方法"""
    if mutation_type == "bit_flip":
        return mutate_bit_flip(individual, vars, mutation_rate)
    elif mutation_type == "uniform":
        return mutate_uniform(individual, vars, mutation_rate)
    elif mutation_type == "gaussian":
        return mutate_gaussian(individual, vars, mutation_rate)
    elif mutation_type == "swap":
        return mutate_swap(individual, vars, mutation_rate)
    elif mutation_type == "model":
        return mutate_model(individual, mutation_rate, graph)
    # elif mutation_type == "adaptive_directed":
    #     return adaptive_directed_mutation(individual, vars, prev_fitness, 
    #                                 prev_prev_fitness, prev_individual,
    #                                 prev_prev_individual, mutation_rate)
