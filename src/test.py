import time
from random import randint



s = time.time()
r = randint(0, 10^1000)
if r == 0:
    print('hello')
e = time.time()
print(e - s)