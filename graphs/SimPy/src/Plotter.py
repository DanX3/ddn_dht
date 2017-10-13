from numpy import arange
import matplotlib.pyplot as plt
from FunctionDesigner import Function2D
import Parser

class Plotter:
    @staticmethod
    def plot_function(range_min=0.0, range_max=1.0, plot_function=plt.plot, ref_function=lambda x: x**2,
                      label="Plot", xlabel="x", ylabel="y", show=True):
        x = arange(range_min, range_max, (range_max-range_min) / 100).tolist()
        print(len(x))
        y = [ref_function(i) for i in x]
        # plot_function(x, y)
        if ref_function:
            plot_function(x, y, linestyle='dashed')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(label)
        plt.grid(True, color='#e0e0e0', linestyle='dashed')
        if show:
            plt.show()

    @staticmethod
    def plot_uniform(value):
        label = "Uniform {}".format(value)
        u = lambda x: value
        Plotter.plot_function(ref_function=u, label=label)

    @staticmethod
    def plot_gauss(mu=5, sigma=1):
        assert(mu - 4*sigma > 0)
        label = "Gauss({:3.1f}, {:3.1f})".format(mu, sigma)
        g = Function2D.get_gauss(mu, sigma)
        gauss2D = Function2D(label, g, mu-4*sigma, mu+4*sigma)
        Plotter.plot_function(ref_function=g, label="Gauss")

    @staticmethod
    def plot_diag_limit(overhead, angular_coeff, range_min=0.0, range_max=1e3):
        """
        Don't use this method directly. Call plot_bandwidth_model instead
        :param overhead: time required for a size 0 transaction
        :param angular_coeff: determined by the bandwidth
        :param range_min: start of plotting. Generally 0
        :param range_max: end of plotting in MB. Generally the size of the packet sent
        :return: the function to use to evaluate your transaction
        """
        label = "DiagLimit ({} ns latency, {} GBps)" .format(overhead, 1e3 / angular_coeff)
        d = Function2D.get_diag_limit(overhead, angular_coeff)
        diag2D = lambda x: x * angular_coeff
        Plotter.plot_function(ref_function=diag2D, range_min=range_min, range_max=range_max, show=False)
        Plotter.plot_function(ref_function=d, range_min=range_min, range_max=range_max, label=label, xlabel="File Size(KB)", ylabel="Time (us)")

    @staticmethod
    def plot_bandwidth_model(latency_ns, bandwidth_GBps):
        Plotter.plot_diag_limit(latency_ns, 1/bandwidth_GBps, range_max=1e6)


if __name__ == "__main__":
    parser = Parser.createparser()
    args = parser.parse_args()
    if args.function:
        if args.function == "gauss":
            Plotter.plot_gauss(args.mu, args.sigma)
        if args.function == "uniform":
            Plotter.plot_uniform(args.value)
        if args.function == "diag":
            Plotter.plot_bandwidth_model(args.overhead, args.angular_coeff)
    else:
        print("Required option <function>")