import numpy as np
from typing import List
from queue import Queue

from numpy import ndarray


def fifo_averaging(avg_volt: ndarray, avg_volt_queue: Queue) -> ndarray:
    avg_volt_queue.put(avg_volt)
    volt_fifo = np.mean(avg_volt_queue.queue)
    # print(f"fifo = {np.mean(avg_volt_queue.queue):.3f}")
    if avg_volt_queue.full():
        avg_volt_queue.get()
    return volt_fifo


def get_averaging(data: List[float], step: int) -> List[ndarray]:
    """
    Функция усредняет массив чисел, разделяя data на подмассивы длинной step
    :param data: np.array, list - последовательность из чисел
    :param step: сколько чисел должно быть в подмассиве
    :return: усредненный список из len(data) / step элементов
    """
    start = 0
    finish = step
    average_list = []
    while start < len(data):
        slice_data = data[start:finish]
        mean_value = np.mean(slice_data)
        average_list.append(mean_value)
        start = finish
        finish = start + step
    return average_list


if __name__ == "__main__":
    data = np.random.randint(0, 100, 200)
    print(get_averaging(data, step=3))
