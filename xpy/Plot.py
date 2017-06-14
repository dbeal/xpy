#!/usr/bin/env python3

class Plot(object):
    @classmethod
    def function(self, fn, domain = (-10, 10), point_count = 1000):
        import matplotlib.pyplot as plt
        import numpy as np
        X = np.linspace(domain[0], domain[1], point_count)
        plt.plot(X, list(map(fn, X)))
        plt.show()

