from concurrent.futures import ThreadPoolExecutor
import time

def pulus(x,y):
    z = 1
    def summm(x,y):
        return x+y+z

    sums = summm(x,y)
    print("begin"+str(x+y))
    time.sleep(x)
    print("end"+str(x+y))
    return sums

with ThreadPoolExecutor(max_workers=10) as executor:
    num = [10,2]
    num2 = [1]*2
    res = executor.map(pulus, num, num2)
    print("end")
print("oh")



print(list(res))
