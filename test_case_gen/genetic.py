from pdb import run
from path_var_exa import path_var_exa
from graph_run import graph_cover, convert_to_networkx, guard_extra
from genetic_mutate import run_mutation
from genetic_select import run_selection
import random
import json

"""
遗传算法生成测试用例
"""

def create_individual_rule(vars):
    """
    初始化单个个体（测试用例）。

    根据变量的类型和取值范围，随机生成一个测试用例。支持布尔值、整数和浮点数类型的变量。
    如果变量的最小值大于最大值，则随机选择一种方式调整取值范围，确保生成的测试用例在合理范围内。

    参数:
    - vars: list, 包含变量信息的列表，每个变量是一个字典，包含变量名、类型、最小值和最大值。

    返回值:
    - individual: dict, 生成的测试用例，键为变量名，值为随机生成的变量值。{'bool_var': True, 'int_var': 42, 'float_var': 0.75}
    """
    individual = {}
    for var in vars:
        name = var["name"]
        type_ = var["type"]

        if type_ == "bool":
            individual[name] = random.choice([True, False])
        elif type_ == "int":
            min_val = var["min"]
            max_val = var["max"]
            if min_val > max_val:
                if random.choice([True, False]):
                    min_val, max_val = min_val, 1000
                else:
                    min_val, max_val = -1000, max_val
            individual[name] = random.randint(min_val, max_val)
        elif type_ == "float":
            min_val = var["min"]
            max_val = var["max"]
            if min_val > max_val:
                if random.choice([True, False]):
                    min_val, max_val = min_val, 1000.0
                else:
                    min_val, max_val = -1000.0, max_val
            individual[name] = random.uniform(min_val, max_val)
    return individual


def create_individual_random(vars):
    """
    初始化单个个体（测试用例）。

    根据变量的类型，随机生成一个测试用例。支持布尔值、整数和浮点数类型的变量。

    参数:
    - vars: list, 包含变量信息的列表，每个变量是一个字典，包含变量名、类型。

    返回值:
    - individual: dict, 生成的测试用例，键为变量名，值为随机生成的变量值。{'bool_var': True, 'int_var': 42, 'float_var': 0.75}
    """
    individual = {}
    for var in vars:
        name = var["name"]
        type_ = var["type"]

        if type_ == "bool":
            individual[name] = random.choice([True, False])
        elif type_ == "int":
            # 为 int 类型随机赋值
            individual[name] = random.randint(-1000, 1000)
        elif type_ == "float":
            # 为 float 类型随机赋值
            individual[name] = random.uniform(-1000.0, 1000.0)
    return individual

# 适应度函数应该和路径的执行结果相适应，这里需要改进
def calculate_fitness(individual, graph):
    
    _, covered_len = graph_cover(graph, individual)
    #  加一避免除以0
    return covered_len + 1


def crossover(parent1, parent2, vars, crossover_rate):
    
    # 不进行交叉操作
    if random.random() > crossover_rate:
        return parent1.copy(), parent2.copy()

    child1 = parent1.copy()
    child2 = parent2.copy()

    # 随机选择两个变量的值进行交换
    for var in vars:
        if random.random() < 0.5:
            try:
                name = var["name"]
                child1[name], child2[name] = child2[name], child1[name]
            except:
                print(f"error:{child1}\n{child2}")
    return child1, child2


def genetic_algorithm(vars, pop_size, max_gens, cross_rate, mut_rate, graph, select="tournament", mutation="model"):
    """主遗传算法"""
    # 初始化种群
    population = [create_individual_random(vars) for _ in range(pop_size)]
    best_ever = None
    best_fitness = -float("inf")

    for gen in range(max_gens):
        # 计算适应度
        fitnesses = [calculate_fitness(ind, graph) for ind in population]

        # 更新历史最佳
        current_best = max(fitnesses)
        if current_best > best_fitness:
            best_index = fitnesses.index(current_best)
            best_ever = population[best_index]
            best_fitness = current_best
        
        # print(f"gen number:{gen+1} current best:{current_best}")
        if current_best == graph.number_of_edges() + 1:
            return best_ever, gen+1

        # 选择父代
        parents = run_selection(population, fitnesses, select)

        # 生成子代
        new_pop = []
        for i in range(0, pop_size, 2):
            p1 = parents[i]
            p2 = parents[i + 1] if (i + 1) < len(parents) else parents[0]
            c1, c2 = crossover(p1, p2, vars, cross_rate)
            # new_pop.extend([mutate(c1, vars, mut_rate), mutate(c2, vars, mut_rate)])
            new_pop.extend([run_mutation(c1, vars, graph, mutation), run_mutation(c2, vars, graph, mutation)])

        # 精英保留（确保不丢失最佳个体）
        if best_ever is not None:
            new_pop[0] = best_ever

        population = new_pop[:pop_size]

    # 返回最佳个体和进化次数
    return best_ever, max_gens

def run_gentic(selections, mutations):
    
    # 遗传算法参数
    POP_SIZE = 3
    MAX_GENERATIONS = 50
    CROSSOVER_RATE = 0.8
    MUTATION_RATE = 0.1
    rounds = 10
    
    with open("../data/graph_data/graph_time_id.jsonl", "r") as graphs_file:
        for graph_line in graphs_file:
            try :
                graph_line = graph_line.strip()
                graph_json = json.loads(graph_line)
                
                variables = path_var_exa(graph_json)
                graph = convert_to_networkx(graph_json, add_id=True)
                
                with open("../data/genetic_exp_data/mutation_data.jsonl", "a") as exp_file:
                    for selection in selections:
                        try:
                            for mutation in mutations:
                                gen_avg = 0
                                for _ in range(rounds):
                                    _, gen_num = genetic_algorithm(
                                        vars=variables,
                                        pop_size=POP_SIZE,
                                        max_gens=MAX_GENERATIONS,
                                        cross_rate=CROSSOVER_RATE,
                                        mut_rate=MUTATION_RATE,
                                        graph=graph,
                                        select=selection,
                                        mutation=mutation
                                    )
                                    gen_avg += gen_num
                                exp_data = {
                                    "graph_id": graph_json["graph_id"],
                                    "selection": selection,
                                    "mutation": mutation,
                                    "avg_gen": gen_avg/rounds
                                }
                                exp_file.write(json.dumps(exp_data, ensure_ascii=False) + "\n")
                                print(exp_data)
                        except:
                            continue
            except:
                continue
                    
if __name__ == "__main__":
    
    selections = ["roulette_wheel", "tournament", "stochastic_universal_sampling", "elitism", "rank", "truncation"]
    mutations = ["bit_flip", "uniform", "gaussian", "swap", "model"]
    
    run_gentic(selections, mutations)
    # 3429104
    
    
        
