from numpy import arange
import matplotlib.pyplot as plt
from FunctionDesigner import Function2D

class Plotter:
    @staticmethod
    def plot_function(range_min=0.0, range_max=10.0, plot_function=plt.plot, ref_function=lambda x: x**2,
                      label="Plot", xlabel="x", ylabel="y"):
        x = arange(range_min, range_max, (range_max-range_min) / 100)
        y = [ref_function(i) for i in x]
        plot_function(x, y)
        if ref_function:
            plot_function(x, ref_function(x), linestyle='dashed')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(label)
        plt.grid(True, color='#e0e0e0', linestyle='dashed')
        plt.show()


    @staticmethod
    def plot_uniform(value):
        label = "Uniform {}".format(value)
        u = lambda x: value
        Plotter.plot_function(ref_function=u, label="Uniform")

    # @staticmethod
    # def plot_gauss(mu, sigma):
    #     assert(mu - 4*sigma > 0)
    #     label = "Gauss({:3.1f}, {:3.1f})".format(mu, sigma)
    #     g = Function2D.get_gauss(mu, sigma)
    #     gauss2D = Function2D(label, g, mu-4*sigma, mu+4*sigma)
    #     gauss2D.plot_function()
    #     Plotter.plot_function(ref_function=gauss2D, label="Gauss")

    @staticmethod
    def plot_diag_limit(overhead, angular_coeff, range_min=0.0, range_max=100000.0):
        """
        Don't use this method directly. Call plot_bandwidth_model instead
        :param overhead: time required for a size 0 transaction
        :param angular_coeff: determined by the bandwidth
        :param range_min: start of plotting. Generally 0
        :param range_max: end of plotting in MB. Generally the size of the packet sent
        :return: the function to use to evaluate your transaction
        """
        label = "DiagLimit ({}, {})" .format(overhead, angular_coeff)
        angular_coeff = 1000.0 / angular_coeff
        d = Function2D.get_diag_limit(overhead, angular_coeff)
        diag2D = lambda x: x * angular_coeff
        Plotter.plot_function(ref_function=diag2D, label="Diag Limit",
                              xlabel="File Size(MB)", ylabel="Time (us)")
        # diag2D.plot_function(plt.semilogy)

    @staticmethod
    def plot_bandwidth_model(latency_ms, bandwidth_kBps, packet_size_kB=100000.0):
        Plotter.plot_diag_limit(latency_ms * 1e3, 1e6/bandwidth_kBps, 0.0, packet_size_kB/1e3)