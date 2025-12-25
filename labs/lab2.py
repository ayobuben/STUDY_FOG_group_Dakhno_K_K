import random
import matplotlib.pyplot as plt

# Настройка стиля графиков
plt.style.use('ggplot')

def simulate_delay(n_tasks=30, fog_min=30, fog_max=80, title=""):
    """Эксперимент 1: Сквозная задержка"""
    random.seed(42) # Фиксируем seed для воспроизводимости
    
    # Генерация задержек (как в методичке)
    sensor = [random.randint(20, 60) for _ in range(n_tasks)]
    fog = [random.randint(fog_min, fog_max) for _ in range(n_tasks)]
    courier = [random.randint(10, 40) for _ in range(n_tasks)]
    
    # Расчет сквозной задержки (End-to-End)
    latencies = [s + f + c for s, f, c in zip(sensor, fog, courier)]
    avg_latency = sum(latencies) / len(latencies)
    
    # Построение графика
    plt.figure(figsize=(10, 5))
    plt.plot(range(1, n_tasks + 1), latencies, marker='o', linestyle='-', color='b')
    plt.title(f"{title}\nСредняя задержка: {avg_latency:.2f} мс")
    plt.xlabel("Номер задачи (Task #)")
    plt.ylabel("Задержка, мс")
    plt.grid(True)
    plt.show()
    
    return avg_latency

def simulate_buffer(n_tasks=30, read_interval_ms=120, title=""):
    """Эксперимент 2: Буфер смартфона"""
    random.seed(42)
    
    # Генерация времени прихода задач (имитация)
    # Предположим, задачи приходят каждые ~100 мс + случайность
    arrival_times = []
    current_time = 0
    for _ in range(n_tasks):
        current_time += random.randint(80, 120) 
        arrival_times.append(current_time)
        
    buffer_sizes = []
    current_buffer = 0
    next_read_time = read_interval_ms
    
    # Проходим по временной шкале прибытия задач
    # Это упрощенная модель для визуализации, как в лабе
    processed_tasks = 0
    task_idx = 0
    
    # Эмуляция проверки буфера по задачам (как на рис. 6 методички)
    # Ось X - номер задачи. Ось Y - размер буфера в момент прихода задачи.
    
    # Логика:
    # 1. Задача пришла. Буфер +1.
    # 2. Проверяем, сколько раз смартфон успел "прочитать" буфер с момента прошлой задачи.
    # 3. Если успел прочитать - буфер обнуляется (или уменьшается).
    
    last_arrival = 0
    
    for arrival in arrival_times:
        # Сколько времени прошло с прошлой задачи
        time_diff = arrival - last_arrival
        
        # Увеличиваем буфер (пришла новая задача)
        current_buffer += 1
        
        # Смартфон читает каждые read_interval_ms
        # Вычисляем, наступило ли время чтения между предыдущим событием и текущим
        # Для упрощения: если интервал чтения прошел, буфер очищается
        
        # В методичке логика: "смартфон извлекает ВСЕ накопленные сообщения"
        # Проверим, было ли событие чтения в промежутке [last_arrival, arrival]
        
        # Кол-во чтений в этом промежутке (упрощенно)
        reads = int(arrival / read_interval_ms) - int(last_arrival / read_interval_ms)
        
        if reads > 0:
            current_buffer = 0 # Смартфон всё вычитал
            # Но текущая задача только пришла, она остается в буфере до след. чтения, 
            # либо если чтение произошло ровно сейчас.
            # Допустим, чтение происходит мгновенно ПЕРЕД записью новой, если совпало, 
            # но здесь мы считаем размер ПРИ поступлении.
            # Пусть будет так: если было чтение, старое ушло, новая задача легла в пустой буфер = 1.
            current_buffer = 1
            
        buffer_sizes.append(current_buffer)
        last_arrival = arrival

    # Построение графика
    plt.figure(figsize=(10, 5))
    plt.plot(range(1, n_tasks + 1), buffer_sizes, marker='s', linestyle='--', color='g')
    plt.title(f"{title} (Интервал чтения: {read_interval_ms} мс)")
    plt.xlabel("Номер задачи")
    plt.ylabel("Сообщений в буфере")
    plt.yticks(range(0, max(buffer_sizes)+2))
    plt.grid(True)
    plt.show()

# --- ЗАПУСК ЭКСПЕРИМЕНТОВ ---

print("=== ЭКСПЕРИМЕНТ 1: ОПТИМИЗАЦИЯ ЗАДЕРЖЕК ===")
# 1. Базовая модель (Fog 30-80)
avg_base = simulate_delay(fog_min=10, fog_max=40, title="Рис. 1 - Базовая сквозная задержка")
print(f"Базовая средняя задержка: {avg_base:.2f} мс")

# 2. Оптимизированная модель (Fog 10-40)
avg_opt = simulate_delay(fog_min=10, fog_max=40, title="Рис. 2 - Оптимизированная сквозная задержка")
print(f"Оптимизированная средняя задержка: {avg_opt:.2f} мс")

reduction = ((avg_base - avg_opt) / avg_base) * 100
print(f"Снижение задержки составило: {reduction:.2f}%")


print("\n=== ЭКСПЕРИМЕНТ 2: БУФЕР СМАРТФОНА ===")
# 3. Быстрое чтение (60 мс)
simulate_buffer(read_interval_ms=60, title="Рис. 3 - Быстрое чтение (буфер пуст)")

# 4. Медленное чтение (200 мс)

simulate_buffer(read_interval_ms=200, title="Рис. 4 - Медленное чтение (накопление)")
