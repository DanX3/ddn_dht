from numpy import exp, linspace, exp
import random
from os import getpid
from math import sqrt, pi


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

    @staticmethod
    def evaluate_function(f, range_min, range_max, eval_nodes=11):
        for i in linspace(range_min, range_max, eval_nodes):
            print("f({:.1f}) = {:.2f}".format(i, f(i)))

    @staticmethod
    def get_gauss(mu, sigma):
        return lambda x: 1.0/(sigma * sqrt(2.0 * pi)) \
                * exp(-(x - mu)**2 / (2*sigma*sigma))

    def change_range(self, range_min, range_max):
        self.range_min = range_min
        self.range_max = range_max
        self.step = float(range_max - range_min) / 100.0

    def change_function(self, function):
        self.function = function

    def change_label(self, label):
        self.label = label

    def evaluate(self, x):
        return self.function(x)

    @staticmethod
    def gauss(mu, sigma):
        random.seed(getpid())
        return int(abs(random.gauss(mu, sigma)))

    @staticmethod
    def get_bandwidth_model(latency_us, bandwidth_kBps):
        if bandwidth_kBps == 0:
            raise ZeroDivisionError
        return Function2D.get_diag_limit(latency_us, 1e6/bandwidth_kBps)

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
        return lambda x: round(sqrt(a*a * (1.0 + (x*x)/(b*b))))


# if __name__ == "__main__":
#     f = lambda x: 3 * exp(-(x-2)**2 / (2*(4**2)))
#     f = Function2D("DiskAccessTime", f, -10, 14)
#     f.plot_function()
#     for i in range(-10, 10):
#         print("[%3d] %4.2f" % (i, f.evaluate(i)))
