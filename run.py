import time
from network_generator_prestige import *
import pyximport; pyximport.install()
from network_generator_cython import *

start = time.time()
human_social_network_prestige((40, 40), 3.4)
print(time.time() - start)

start = time.time()
human_social_network_prestige_cython((40, 40), 3.4)
print(time.time() - start)