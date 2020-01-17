import time
def printer():
    i = 0
    while True:
        print(i)
        i+=1
        time.sleep(0.01)

if __name__ == "__main__":
    printer()

#printer()