import matplotlib.pyplot as plt
from numpy import arange
from numpy import exp

class Function2D:
    def __init__(self, label, function, range_min, range_max):
        assert(range_min < range_max)
        self.label = label
        self.function = function
        self.range_min = range_min
        self.range_max = range_max
        self.step = float(range_max - range_min) / 100.0

    def plot_function(self):
        x = arange(self.range_min, self.range_max, self.step)
        y = self.function(x)
        plt.plot(x, y)
        plt.show()

    def change_range(range_min, range_max):
        self.range_min = range_min
        self.range_max = range_max
        self.step = float(range_max - range_min) / 100.0

    def change_function(function):
        self.function = function

    def change_label(label):
        self.label = label

    def evaluate(self, x):
        return self.function(x)


if __name__ == "__main__":
    f = lambda x: 3 * exp(-(x-2)**2 / (2*(4**2)))
    f = Function2D("DiskAccessTime", f, -10, 14)
    # f.plot_function()
    for i in range(-10, 10):
        print "[%3d] %4.2f" %(i, f.evaluate(i))
