import random

def roulette_wheel_selection(population, fitnesses):
    """轮盘赌选择"""
    total_fitness = sum(fitnesses)
    probs = [f/total_fitness for f in fitnesses]
    selected = []
    for _ in range(len(population)):
        r = random.random()
        cumulative_prob = 0
        for i, prob in enumerate(probs):
            cumulative_prob += prob
            if r <= cumulative_prob:
                selected.append(population[i])
                break
    return selected

def tournament_selection(population, fitnesses, tournament_size=2):
    """锦标赛选择"""
    selected = []
    for _ in range(len(population)):
        candidates = random.choices(list(zip(population, fitnesses)), k=tournament_size)
        best = max(candidates, key=lambda x: x[1])[0]
        selected.append(best)
    return selected

def stochastic_universal_sampling(population, fitnesses):
    """
    随机通用抽样(SUS)算法 - 一种改进的轮盘赌选择方法
    
    参数:
        population: list - 种群个体列表
        fitnesses: list - 对应每个个体的适应度值列表
        
    返回值:
        list - 新选择的个体列表，大小与原始种群相同
        
    算法说明:
        1. 计算总适应度和指针间距
        2. 随机生成起始点
        3. 创建等间距的指针列表
        4. 遍历每个指针，累积适应度值直到超过指针位置
        5. 选择当前对应的个体
    """
    total_fitness = sum(fitnesses)
    point_distance = total_fitness / len(population)
    start_point = random.uniform(0, point_distance)
    pointers = [start_point + i*point_distance for i in range(len(population))]
    
    cumulative_fitness = 0
    selected = []
    for p in pointers:
        i = 0
        cumulative_fitness += fitnesses[i]
        while cumulative_fitness < p:
            i += 1
            cumulative_fitness += fitnesses[i]
        selected.append(population[i])
    return selected

def elitism_selection(population, fitnesses, elite_size=1):
    """
    精英选择算法 - 保留适应度最高的elite_size个个体直接进入下一代
    
    参数:
        population: list - 种群个体列表
        fitnesses: list - 对应每个个体的适应度值列表
        elite_size: int - 保留的精英个体数量
        
    返回值:
        list - 新种群列表，包含精英个体和随机选择的普通个体
        
    算法说明:
        1. 将种群个体按适应度值降序排序
        2. 选取前elite_size个精英个体
        3. 从整个种群中随机选择剩余个体
        4. 组合精英个体和随机个体形成新种群
    """
    combined = list(zip(population, fitnesses))
    combined.sort(key=lambda x: x[1], reverse=True)
    elites = [ind for ind, fit in combined[:elite_size]]
    return elites + random.choices(population, k=len(population)-elite_size)


def rank_selection(population, fitnesses):
    """
    排序选择算法 - 基于个体排名而非绝对适应度值进行选择
    
    参数:
        population: list - 种群个体列表
        fitnesses: list - 对应每个个体的适应度值列表
        
    返回值:
        list - 新选择的个体列表，大小与原始种群相同
        
    算法说明:
        1. 将种群个体按适应度值升序排序(最差到最好)
        2. 为每个个体分配排名(1为最差，N为最好)
        3. 计算每个个体的选择概率(排名/总排名)
        4. 根据排名概率进行加权随机选择
        
    """
    ranked = sorted(zip(population, fitnesses), key=lambda x: x[1])
    ranks = [i+1 for i in range(len(ranked))]  # 1为最差，N为最好
    total_rank = sum(ranks)
    probs = [r/total_rank for r in ranks]
    selected = random.choices([ind for ind, fit in ranked], weights=probs, k=len(population))
    return selected


def truncation_selection(population, fitnesses, threshold=0.3):
    """
    截断选择算法 - 从适应度最高的前threshold比例个体中进行选择
    
    参数:
        population: list - 种群个体列表
        fitnesses: list - 对应每个个体的适应度值列表
        threshold: float - 截断阈值(0-1)，表示选择前多少比例的个体
        
    返回值:
        list - 新选择的个体列表，大小与原始种群相同
        
    算法说明:
        1. 将种群和适应度值组合并排序(降序)
        2. 计算截断点，保留前threshold比例的个体
        3. 从保留的个体中有放回地随机抽样，直到填满原始种群大小
    """
    combined = list(zip(population, fitnesses))
    combined.sort(key=lambda x: x[1], reverse=True)
    
    # 确保至少选择1个个体
    cutoff = max(1, int(len(population) * threshold))
    
    # random.choices函数能够实现有放回的随机抽样，也就是在抽样时，同一个个体可以被多次选中
    selected = random.choices([ind for ind, fit in combined[:cutoff]], k=len(population))
    return selected

def run_selection(population, fitnesses, select):
    if select == "roulette_wheel":
        selected = roulette_wheel_selection(population, fitnesses)
    elif select == "tournament":
        selected = tournament_selection(population, fitnesses)
    elif select == "stochastic_universal_sampling":
        selected = stochastic_universal_sampling(population, fitnesses)
    elif select == "elitism":
        selected = elitism_selection(population, fitnesses)
    elif select == "rank":
        selected = rank_selection(population, fitnesses)
    elif select == "truncation":
        selected = truncation_selection(population, fitnesses)
    return selected