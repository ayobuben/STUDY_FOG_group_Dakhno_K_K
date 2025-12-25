import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd

# Настройки стиля
plt.style.use('ggplot')

class IoTSimulator:
    def __init__(self, n_edge, n_fog, n_cloud, n_tasks=200, queue_cap=50, mobile_optimized=False):
        self.n_edge = n_edge
        self.n_fog = n_fog
        self.n_cloud = n_cloud
        self.n_tasks = n_tasks
        self.queue_cap = queue_cap
        self.mobile_optimized = mobile_optimized
        self.results = []

    def run(self):
        random.seed(42)
        np.random.seed(42)
        
        latencies = []
        types = []
        
        # Генерация нагрузки
        # Fog узлы имеют очередь. Распределяем задачи по Fog-узлам
        tasks_per_fog = [0] * self.n_fog
        
        for i in range(self.n_tasks):
            # 1. Тип устройства (30% мобильные, 70% стационарные)
            is_mobile = random.random() < 0.3
            types.append("Mobile" if is_mobile else "Stationary")
            
            # 2. Задержка Edge (генерация данных)
            if is_mobile:
                if self.mobile_optimized:
                    # Оптимизированные параметры (Эксперимент 2)
                    edge_delay = random.randint(20, 60)
                    net_jitter = random.randint(5, 15)
                else:
                    # Стандартные параметры
                    edge_delay = random.randint(25, 70)
                    net_jitter = random.randint(8, 20)
            else:
                edge_delay = random.randint(20, 60)
                net_jitter = random.randint(5, 15)
            
            # 3. Fog обработка + Очередь
            # Выбираем случайный Fog узел
            fog_id = random.randint(0, self.n_fog - 1)
            
            # Логика очереди: чем больше задач на узле, тем выше задержка
            current_load = tasks_per_fog[fog_id]
            if current_load < self.queue_cap:
                queue_delay = current_load * 0.5 # 0.5 мс на каждую задачу в очереди
                tasks_per_fog[fog_id] += 1 # Добавляем задачу
                # Имитация освобождения очереди со временем
                if random.random() > 0.5 and tasks_per_fog[fog_id] > 0:
                     tasks_per_fog[fog_id] -= 1
            else:
                queue_delay = 100 # Штраф за переполнение (Dropping/Retry)
            
            fog_process = random.randint(10, 30)
            fog_total = fog_process + queue_delay
            
            # 4. Cloud обработка
            cloud_process = random.randint(50, 100)
            
            # Сквозная задержка
            total_latency = edge_delay + net_jitter + fog_total + cloud_process
            latencies.append(total_latency)
            
        return latencies, types

def plot_experiment_1(variant_configs):
    """Эксперимент 1: Масштабирование"""
    means = []
    labels = []
    
    print("\n--- Эксперимент 1: Масштабирование (Чувствительность) ---")
    for cfg in variant_configs:
        sim = IoTSimulator(n_edge=cfg['edge'], n_fog=cfg['fog'], n_cloud=cfg['cloud'])
        lats, _ = sim.run()
        avg = np.mean(lats)
        means.append(avg)
        label = f"Edge: {cfg['edge']}"
        labels.append(label)
        print(f"Конфигурация {label}: Средняя задержка = {avg:.2f} мс")

    plt.figure(figsize=(10, 6))
    plt.plot(labels, means, marker='o', linestyle='-', color='b')
    plt.title("Эксперимент 1: Влияние количества Edge-устройств на задержку")
    plt.xlabel("Масштаб системы (при фиксированных Fog=5)")
    plt.ylabel("Средняя сквозная задержка (мс)")
    plt.grid(True)
    plt.show()

def plot_experiment_2():
    """Эксперимент 2: Мобильные vs Стационарные"""
    # До оптимизации
    sim_base = IoTSimulator(100, 5, 2, mobile_optimized=False)
    lats_base, types_base = sim_base.run()
    df_base = pd.DataFrame({'Latency': lats_base, 'Type': types_base})
    
    # После оптимизации
    sim_opt = IoTSimulator(100, 5, 2, mobile_optimized=True)
    lats_opt, types_opt = sim_opt.run()
    df_opt = pd.DataFrame({'Latency': lats_opt, 'Type': types_opt})

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # График 1
    df_base.boxplot(column='Latency', by='Type', ax=axes[0])
    axes[0].set_title("До оптимизации")
    axes[0].set_ylabel("Задержка (мс)")
    
    # График 2
    df_opt.boxplot(column='Latency', by='Type', ax=axes[1])
    axes[1].set_title("После оптимизации (Mobile)")
    
    plt.suptitle("Эксперимент 2: Сравнение типов устройств")
    plt.show()

def plot_experiment_3():
    """Эксперимент 3: Очереди Fog"""
    queues = [20, 50, 100, 200]
    results = []
    
    print("\n--- Эксперимент 3: Размер очереди ---")
    for q in queues:
        sim = IoTSimulator(100, 5, 2, queue_cap=q)
        lats, _ = sim.run()
        avg = np.mean(lats)
        results.append(avg)
        print(f"Queue: {q}, Avg Latency: {avg:.2f} мс")
        
    plt.figure(figsize=(8, 5))
    plt.bar([str(x) for x in queues], results, color='orange')
    plt.title("Эксперимент 3: Влияние размера очереди Fog-узла")
    plt.xlabel("Емкость очереди (queue_capacity)")
    plt.ylabel("Средняя сквозная задержка (мс)")
    plt.show()

# --- ЗАПУСК ---

# 1. Параметры для Варианта 1 (100 Edge, 5 Fog) + Чувствительность (+25%, +50%...)
configs_exp1 = [
    {'edge': 100, 'fog': 5, 'cloud': 2}, # База (100%)
    {'edge': 125, 'fog': 5, 'cloud': 2}, # +25%
    {'edge': 150, 'fog': 5, 'cloud': 2}, # +50%
    {'edge': 175, 'fog': 5, 'cloud': 2}, # +75%
    {'edge': 200, 'fog': 5, 'cloud': 2}  # +100%
]
plot_experiment_1(configs_exp1)
plot_experiment_2()
plot_experiment_3()