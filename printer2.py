import time
def printer():
    i = 0
    while i < 100:
        print(i**2)
        i+=1
        time.sleep(1)

printer()