import time


l = list(range(0, 100))

def filter(i):
    print('hello')
    if i + int(i * 0.5) % 7 == 0:
        return i

s = time.time()
new_list = []
for f in l:
    r = filter(f)
    if r:
        new_list.append(r)
e = time.time()
print(len(new_list))
print('time for loop:', str(e-s))

s = time.time()
p = list(map(filter, l))
print(len(p))
e = time.time()

print('time for map:', str(e-s))