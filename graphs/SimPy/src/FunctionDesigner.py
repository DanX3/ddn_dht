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
    def get_bandwidth_model(latency_ns, bandwidth_GBps):
        if bandwidth_GBps == 0:
            raise ZeroDivisionError
        return Function2D.get_diag_limit(latency_ns, 1/bandwidth_GBps)

    @staticmethod
    def disk_interaction(filesize: int, bandwidth_KBps: int):
        return int(filesize * 1000000000 / bandwidth_KBps)  # 1e9, avoing int casting, to ns conversion

    @staticmethod
    def get_diag_limit(overhead, angular_coeff):
        #following the formula of hyperbola
        #   - it has diagonal limit for +infty
        #Y^2/a^2 - X^2/b^2 = 1
        #extracting y and selecting the positive part it becomes
        #y = sqrt(a^2 * (1 + x^2/b^2))
        a = overhead
        b = a / angular_coeff

        # This should be the canonical one, but the 1e0 makes it too far away from the limit
        # I want that the limit curve is as close as possible starting at 1024
        # packets sent bigger than 1024 has already peak efficiency
        # return lambda x: round(sqrt(a*a * (1e0 + (x*x)/(b*b))))
        return lambda x: round(sqrt(a*a * (1e-6 + (x*x)/(b*b))) * 1e3)


if __name__ == "__main__":
    f = Function2D.get_bandwidth_model(100000, 1)
    out = open('/tmp/data.txt', 'w')
    for i in range(0, 1500, 10):
        out.write("{} {}\n".format(i, f(i)))
    out.close()

