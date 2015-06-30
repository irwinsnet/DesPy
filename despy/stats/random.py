#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
Provides a random number seed function and statistical helper functions.

..  autosummary::

    seed
    get_poisson_pmf
    get_empirical_pmf
    
**Python Library Dependencies**
    * :mod:`random`
    
**External Library Dependencies**
    * :mod:`scipy.stats`
    * :mod:`numpy.random`
    
Designers should use the despy.stats.random.seed function when seeding
the random number generators. While despy will use the numpy random
number generator instead of the generator built into Python's random
module, we can't guarantee that Python random module functions won't
sneak into a custom subclass. The numpy and Python random number
generators use different random number sequences, so it's necessary to
seed both generators to ensure a consistent random number sequence
thoughout the simulation.

Using the other functions in this module is optional. Designers who are
familiar with the scipy.stats package are encouraged to use that package
directly -- it's more than sufficient. However, the documentation for
the scipy.stats package can be challenging for new users, so I've
included helper functions to steer new simulation designers in the
right direction.

The get_..._pmf and get_..._cdf functions return frozen scipy.stats
probability distributions. Each distribution can generate random
variables, calculate expected means, medians, and variances, and much
more. 
    
"""

import scipy.stats as stats
import numpy as np
import random

def seed(seed):
    """Seed random number generators in numpy and Python random module.
    """
    np.random.seed(seed)
    random.seed(seed)

def get_poisson_pmf(mu):
    """Return Scipy.stats Poisson PMF class with lambda = mu.
    """
    return stats.poisson(mu)

def get_empirical_pmf(values, probabilities, name="Empirical PMF"):
    """Return custom Scipy.stats discrete PMF.
    """
    return stats.rv_discrete(values=(values, probabilities), name=name)



            
        
    

            