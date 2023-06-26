import time
import matplotlib.pyplot as plt
from threading import Thread
from queue import Queue
from numpy import ndarray

from controller import PowerControlling, PID_regulator, TemperatureControlling
from realtimeplot import RealtimePlot


global temp_required


def controlling(controller: TemperatureControlling,
                pid,
                temp_current: ndarray,
                temp_required: float, displays, start) -> None:
    """
    Функция для управления процесса контроля
    :param controller: объект контроллера
    :param volt_current: текущее значение напряжения
    :param volt_required: необходимое значение напряжения
    """
    controller.start(temp_current, temp_required, pid,
                     displays, start, drawing=True)


def change_temp_required() -> None:
    """ Фукнция для изменения требуемого значения температуры"""
    global temp_required

    while True:
        temp_required = float(input("Enter required temp: "))


def main():
    global temp_required

    tempController1 = TemperatureControlling()
    tempController1.config_DigitalOut(device='Dev1', line=23)
    tempController1.config_AnalogIn(device='Dev1', channel=1,
                                    rate=1000, samples=20)

    start = time.time()
    fig, axes = plt.subplots(figsize=(12, 12))
    plt.title('Изменение температуры')
    plt.xlabel('Время, c')
    plt.ylabel('Температура, градусы цельсия')
    plt.grid()
    display = RealtimePlot(axes, max_entries=100, color='black')
    display2 = RealtimePlot(axes, max_entries=100, color='red')

    pid = PID_regulator(p=0.1, d=0, i=0.005, delta_t=0.2)

    t1 = Thread(target=change_temp_required)
    t1.start()

    temp_required = 20
    while True:
        temp = tempController1.get_average_temp(samples=20) * 100
        print(temp)
        controlling(tempController1, pid,
                    temp_current=temp, temp_required=temp_required,
                    displays=(display, display2), start=start)

    tempController1.AnIn_task.close()
    tempController1.DigOut_task.close()


if __name__ == '__main__':
    main()
