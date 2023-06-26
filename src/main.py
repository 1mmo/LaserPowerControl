import time
import matplotlib.pyplot as plt
from threading import Thread
from queue import Queue
from numpy import ndarray

from controller import PowerControlling, PID_regulator
from realtimeplot import RealtimePlot


global volt_required


def controlling(controller: PowerControlling,
                pid,
                volt_current: ndarray,
                volt_required: float, displays, start) -> None:
    """
    Функция для управления процесса контроля
    :param controller: объект контроллера
    :param volt_current: текущее значение напряжения
    :param volt_required: необходимое значение напряжения
    """
    controller.start(volt_current, volt_required, pid,
                     displays, start, drawing=True)


def change_volt_required() -> None:
    global volt_required
    """ Фукнция для изменения требуемого значения мощность """
    while True:
        volt_required = float(input("Enter required voltage: "))


def main():
    global volt_required

    controller1 = PowerControlling()
    controller1.config_AnalogIn(device='Dev1', channel=3,
                                rate=1000, samples=20)
    controller1.config_AnalogOut(device='Dev1', channel=1)

    start = time.time()
    fig, axes = plt.subplots(figsize=(12, 12))
    plt.title('Изменение напряжения')
    plt.xlabel('Время, c')
    plt.ylabel('Напряжение, В')
    plt.grid()
    display = RealtimePlot(axes, max_entries=100, color='black')
    display2 = RealtimePlot(axes, max_entries=100, color='red')

    avg_volt_queue = Queue(maxsize=2)
    pid = PID_regulator(p=0, d=0, i=10, delta_t=0.02)

    t1 = Thread(target=change_volt_required)
    t1.start()

    volt_required = 0
    while True:
        volt = controller1.get_average_volt(samples=20,
                                            avg_volt_queue=avg_volt_queue)
        controlling(controller1, pid,
                    volt_current=volt, volt_required=volt_required,
                    displays=(display, display2), start=start)

    controller1.close_task()


if __name__ == '__main__':
    main()
