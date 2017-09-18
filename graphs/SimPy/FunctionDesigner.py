import matplotlib.pyplot as plt
from numpy import arange, exp, linspace
import random
from os import getpid
from math import floor, sqrt, pi, log

class Function2D:
    def __init__(self, label, plotting_function, range_min=1.0, range_max=10.0,
                 function_reference=None):
        assert(range_min < range_max)
        self.label = label
        self.function = plotting_function
        self.range_min = range_min
        self.range_max = range_max
        self.step = float(range_max - range_min) / 100.0
        self.function_reference = function_reference

    def plot_function(self, plot_function=plt.plot, xlabel=None, ylabel=None):
        x = arange(self.range_min, self.range_max, self.step)
        y = [self.function(i) for i in x]
        plot_function(x, y)
        if self.function_reference:
            plot_function(x, self.function_reference(x), linestyle='dashed')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(self.label)
        plt.grid(True, color='#e0e0e0', linestyle='dashed')
        plt.show()

    @staticmethod
    def evaluate_function(f, range_min, range_max, eval_nodes=11):
        for i in linspace(range_min, range_max, eval_nodes):
            print("f({:.1f}) = {:.2f}".format(i, f(i)))

    @staticmethod
    def get_gauss(mu, sigma):
        return lambda x: 1.0/(sigma * sqrt(2.0 * pi)) \
                * exp(-(x - mu)**2 / (2*sigma*sigma))

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

    @staticmethod
    def gauss(mu, sigma):
        random.seed(getpid())
        return int(abs(random.gauss(mu, sigma)))

    @staticmethod
    def get_diag_limit(overhead, angular_coeff):
        #following the formula of hyperbola
        #   - it has diagonal limit for +infty
        #Y^2/a^2 - X^2/b^2 = 1
        #extracting y and selecting the positive part it becomes
        #y = sqrt(a^2 * (1 + x^2/b^2))
        #a = overhead
        #b = overhead / angular_coeff
        a = overhead
        b = a / angular_coeff
        return lambda x: round(sqrt(a*a * (1.0 + x**2/b**2)))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Plotter:
    @staticmethod
    def plot_uniform(value):
        label = "Uniform {}".format(value)
        u = lambda x: value
        uniform2D = Function2D(label, u, 1.0, 10.0)
        uniform2D.plot_function()

    @staticmethod
    def plot_gauss(mu, sigma):
        assert(mu - 4*sigma > 0)
        label = "Gauss({:3.1f}, {:3.1f})".format(mu, sigma)
        g = Function2D.get_gauss(mu, sigma)
        gauss2D = Function2D(label, g, mu-4*sigma, mu+4*sigma)
        gauss2D.plot_function()

    @staticmethod
    def plot_diag_limit(overhead, angular_coeff):
        label = "DiagLimit ({}, {})" .format(overhead, angular_coeff)
        angular_coeff = 1000.0 / angular_coeff
        d = Function2D.get_diag_limit(overhead, angular_coeff)
        diag2D = Function2D(label, d, 0.0, 500.0,
                function_reference=lambda x: x * angular_coeff)
        diag2D.plot_function(plt.plot, "File Size(MB)", "Time (s)")
        # diag2D.plot_function(plt.semilogy)



if __name__ == "__main__":
    f = lambda x: 3 * exp(-(x-2)**2 / (2*(4**2)))
    f = Function2D("DiskAccessTime", f, -10, 14)
    f.plot_function()
    for i in range(-10, 10):
        Print("[%3d] %4.2f" %(i, f.evaluate(i)))
