import time
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from collections import deque


class RealtimePlot:
    def __init__(self, axes, color: str, max_entries=32):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axes = axes
        self.max_entries = max_entries
        self.lineplot, = axes.plot([], [], c=color) # 'ro-'
        self.axes.set_autoscaley_on(b=True)

    def add(self, x, y):
        self.axis_x.extend(x)
        self.axis_y.extend(y)
        self.lineplot.set_data(self.axis_x, self.axis_y)
        self.axes.set_ylim(0, 0.3)
        # self.axes.set_xlim(self.axis_x[0],
        # self.axis_x[-1] + 1e-15, auto=True)
        self.axes.set_xlim(0, self.axis_x[-1] + 5)
        self.axes.set_xticks(np.arange(start=round(self.axis_x[0]),
                                       stop=round(self.axis_x[-1] + 1),
                                       step=5))
        self.axes.relim()
        self.axes.autoscale_view()  # rescale the y-axis

    def animate(self, figure, callback, interval=50):
        def wrapper(frame_index):
            self.add(*callback(frame_index))
            self.axes.relim()
            self.axes.autoscale_view()
            return self.lineplot

        animation.FuncAnimation(figure, wrapper, interval=interval)


def main():
    start = time.time()
    fig, axes = plt.subplots()
    display = RealtimePlot(axes)
    display.animate(fig, lambda frame_index: (time.time() - start, np.random.random() * 100))
    plt.show()

    fig, axes = plt.subplots()
    display = RealtimePlot(axes)
    while True:
        display.add(time.time() - start, np.random.random() * 100)
        plt.pause(2)


if __name__ == "__main__":
    main()
