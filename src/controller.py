import nidaqmx
import time
import matplotlib.pyplot as plt
from matplotlib.artist import Artist
from numpy import ndarray
from nidaqmx.constants import TerminalConfiguration as TerminalConfig
from nidaqmx.constants import AcquisitionType
from nidaqmx.errors import DaqError
from queue import Queue

from smoothing import get_averaging, fifo_averaging
from realtimeplot import RealtimePlot


class PID_regulator:
    """
    Proportional Integral Derivative controller
    """
    def __init__(self, p: float, d: float,
                 i: float, delta_t: float) -> None:
        """
        Инициализация начальных параметров для PID регулятора
        :param p: пропорциональный коэффициент
        :param d: дифференциальный коэффициент
        :param i: интегральный коэффициент
        :param delta_t: время между двумя точками напряжения
        вычисляется как кол-во точек в буфере на частоту дискретизаци,
        к примеру, кол-во точек в буфере (samps_per_chan) = 100,
        а частота дискретизации (rate) = 1000, тогда delta_t = 0.1 секунда
        """
        self.p = p
        self.d = d
        self.i = i
        self.delta_t = delta_t
        self.integral = 0  # сумма всех volt
        self.volt_prev = 0  # предыдущее значение volt

    def start(self, volt: float, required_volt: float) -> float:
        """
        Запуск PID контроллера
        :param required_volt:
        :param volt: текущее напряжение, полученное с Analog Input
        :return: регуляризованное напряжение для Analog Output
        """
        volt, volt_previous = volt, self.volt_prev

        # print('***', required_volt, volt, '***')
        self.integral += required_volt - volt # сумма всех напряжений
        # print('integral', self.integral)
        self.volt_prev = volt  # запоминаем текущее напряжение, как предыдущее

        dif_func = (volt - volt_previous) / self.delta_t
        prop_func = required_volt - volt  # значение ошибки
        integral_func = self.i * self.integral * self.delta_t
        u_out = self.p*prop_func + self.d*dif_func + integral_func
        return u_out


class PCI:
    """
    Класс для настройки конфигураций аналоговых входа и выхода
    в устройстве NI PCI-6251
    """
    def __init__(self):
        self.system = nidaqmx.system.System.local()
        self.devices = [dev.name for dev in self.system.devices]
        self.AnIn_ch = [ch.name for dev in self.devices
                        for ch in self.system.devices[dev].ai_physical_chans]
        self.AnOut_ch = [ch.name for dev in self.devices
                         for ch in self.system.devices[dev].ao_physical_chans]
        self.DigOut_ch = [ch.name for dev in self.devices
                          for ch in self.system.devices[dev].do_lines]
        self.AnIn_task = None
        self.AnOut_task = None
        self.DigOut_task = None
        self.input_rate = None
        self.input_samples = None

    def config_AnalogIn(self, device: str,
                        channel: int,
                        rate: int,
                        samples: int) -> None:
        """
        Настройка аналогового входа
        :param device: название device, например, 'Dev1'.
        :param channel: номер канала, например, 7.
        :param rate: частота дискретизации сигнала.
        :param samples: кол-во выборок на канал (размер буфера)
        """
        self.input_rate = rate
        self.input_samples = samples

        self.AnIn_task = nidaqmx.Task()

        try:
            system = self.system.devices[device]
            AnIn_ch = [ch.name for ch in system.ai_physical_chans]
            channel = AnIn_ch[channel]
        except DaqError:
            print(f'{device} не используется в системе')
            exit()
        except IndexError:
            print(f'Канала {channel} не используется в системе')
            exit()

        config = TerminalConfig.RSE
        self.AnIn_task.ai_channels.add_ai_voltage_chan(
            physical_channel=channel,
            terminal_config=config
        )
        sample_mode = AcquisitionType.FINITE
        self.AnIn_task.timing.cfg_samp_clk_timing(rate=rate,
                                                  sample_mode=sample_mode,
                                                  samps_per_chan=samples)

    def config_AnalogOut(self, device: str,
                         channel: int) -> None:
        """
        Настройка аналогового выхода
        :param device: название device, например, 'Dev1'.
        :param channel: номер канала, например, 7.
        """
        self.AnOut_task = nidaqmx.Task()

        try:
            system = self.system.devices[device]
            AnOut_ch = [ch.name for ch in system.ao_physical_chans]
            channel = AnOut_ch[channel]
        except DaqError:
            print(f'{device} не используется в системе')
            exit()
        except IndexError:
            print(f'Канала {channel} не используется в системе')
            exit()

        self.AnOut_task.ao_channels.add_ao_voltage_chan(
            physical_channel=channel
        )

    def config_DigitalOut(self, device: str,
                          line: int) -> None:
        """
        Настройка аналогового выхода
        :param device: название device, например, 'Dev1'.
        :param line: номер линии, например, 20.
        """
        self.DigOut_task = nidaqmx.Task()

        try:
            system = self.system.devices[device]
            DigOut_ch = [ch.name for ch in system.do_lines]
            line = DigOut_ch[line]
        except DaqError:
            print(f'{device} не используется в системе')
            exit()
        except IndexError:
            print(f'Канала {line} не используется в системе')
            exit()

        self.DigOut_task.do_channels.add_do_chan(
            lines=line
        )

    def close_task(self):
        self.AnIn_task.close()
        self.AnOut_task.close()


class PowerControlling(PCI):
    """
    Реализация контроля мощности лазера
    """
    def get_voltage(self, samples: int) -> list:
        """
        Функция выдает значения напряжения из буфера
        :param samples: кол-во значений из буфера
        :return: список из samples значений
        """
        volt = self.AnIn_task.read(number_of_samples_per_channel=samples)
        return volt

    def get_average_volt(self, samples: int,
                         avg_volt_queue: Queue) -> ndarray:
        """
        Функция получает значения напряжения из буфера,
        передает их в функцию для усреднения и на выходе
        возвращает среднее значение напряжения.
        :param samples: кол-во значений из буфера
        :param avg_volt_queue: очередь, в которой хранятся усредненные
        значения напряжения (нужна для реализации fifo усреднения)
        :return: среднее значение напряжения
        """
        volt = self.AnIn_task.read(number_of_samples_per_channel=samples)
        avg_volt = get_averaging(volt, step=samples)[0]
        volt_fifo = fifo_averaging(avg_volt, avg_volt_queue)
        return volt_fifo

    def send_analog_value(self, voltage_out) -> None:
        """
        Функция для отправки аналогового значения на выходной канал
        :param voltage_out: значение напряжения для отправки
        """
        self.AnOut_task.write(voltage_out)

    def start(self, volt_current, volt_required, pid,
              displays, start, drawing=False) -> None:
        """
        Функция для запуска контроллера мощности
        """

        voltage_out = pid.start(volt_current, volt_required)
        # print(f"ЦАП = {voltage_out}")
        # print(f'Current = {volt_current}')
        self.send_analog_value(voltage_out)

        if drawing:
            timer = time.time() - start
            displays[0].add([timer], [volt_current])
            displays[1].add([timer], [voltage_out])
            frame1 = plt.text(timer-3, volt_current+0.02,
                              f"volt_in = {round(volt_current, 3)}",
                              bbox=dict(facecolor='none', edgecolor='black',
                                        boxstyle='square,pad=1'))
            frame2 = plt.text(timer-3, voltage_out-0.02,
                              f"volt_out = {round(voltage_out, 3)}",
                              bbox=dict(facecolor='none', edgecolor='red',
                                        boxstyle='square,pad=1'))
            Artist.set_visible(frame1, True)
            Artist.set_visible(frame2, True)
            # To remove the artist
            plt.pause(0.5)
            Artist.remove(frame1), Artist.remove(frame2)


class TemperatureControlling(PCI):
    """
    Реализация контроля температуры
    """
    def get_temp(self, samples: int) -> list:
        """
        Функция выдает значения напряжения(температуры) из буфера
        :param samples: кол-во значений из буфера
        :return: список из samples значений
        """
        temp = self.AnIn_task.read(number_of_samples_per_channel=samples)
        return temp

    def get_average_temp(self, samples: int) -> ndarray:
        """
        Функция получает значения напряжения(температуры) из буфера,
        передает их в функцию для усреднения и на выходе
        возвращает среднее значение напряжения.
        :param samples: кол-во значений из буфера
        """
        temp = self.AnIn_task.read(number_of_samples_per_channel=samples)
        avg_temp = get_averaging(temp, step=samples)[0]
        return avg_temp

    def send_digital_value(self, temp_out):
        temp_out = -temp_out
        if temp_out < 0:
            temp_out = 0

        if temp_out > 0.5:
            temp_out = 0.5

        print('temp out=', temp_out)
        self.DigOut_task.write(True)
        time.sleep(temp_out)
        self.DigOut_task.write(False)

    def start(self, temp_current, temp_required, pid,
              displays, start, drawing=False) -> None:
        """
        Функция для запуска контроллера температуры
        """
        temp_out = pid.start(temp_current, temp_required)
        self.send_digital_value(temp_out)

        if drawing:
            timer = time.time() - start
            displays[0].add([timer], [temp_current])
            displays[1].add([timer], [temp_out])
            frame1 = plt.text(timer-3, temp_current+0.02,
                              f"volt_in = {round(temp_current, 3)}",
                              bbox=dict(facecolor='none', edgecolor='black',
                                        boxstyle='square,pad=1'))
            frame2 = plt.text(timer-3, temp_out-0.02,
                              f"volt_out = {round(temp_out, 3)}",
                              bbox=dict(facecolor='none', edgecolor='red',
                                        boxstyle='square,pad=1'))
            Artist.set_visible(frame1, True)
            Artist.set_visible(frame2, True)
            # To remove the artist
            plt.pause(0.5)
            Artist.remove(frame1), Artist.remove(frame2)


if __name__ == '__main__':
    controller1 = PowerControlling()
    controller1.config_AnalogIn(device='Dev1', channel=7,
                                rate=1000, samples=100)
    controller1.config_AnalogOut(device='Dev1', channel=0)
    controller1.get_voltage(samples=100)
    controller1.close_task()
