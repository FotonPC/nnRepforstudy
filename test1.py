import os, sys, time

def code():
    try:
        num = int(input())
        pid = os.fork()
        if pid == 0:
            code()
        else:
            os.waitpid(pid, 0)
            print(num)
    finally:
        return


code()