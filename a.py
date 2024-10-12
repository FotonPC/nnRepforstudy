import os, sys, time

def start_processing(r, w):
    while True:
        data = os.read(r, 4)
        if data == b'ping':
            os.write(w, b'pong')
        elif data == b'kill':
            os.write(w, b'okay')
            return
def main():
    k = int(input())
    rList = []
    wList = []
    for i in range(2*k):
        r, w = os.pipe()
        rList.append(r)
        wList.append(w)
    for i in range(k):
        pid = os.fork()
        if pid == 0:
            start_processing(rList[2*i], wList[2*i+1])
            return
    while True:
        query = input(' ~ ')
        query = query.split()
        if query[0] == 'kill':
            for i in range(k):
                os.write(wList[2*i], b'kill')
                data = os.read(rList[2*i+1], 4) # okay
                print(f'\rProcess #{i} kill: {data}', end='')
                time.sleep(0.01)
            print('\n\-_-/ All processes killed')
            return
        if query[0] == 'ping':
            try:
                num = int(query[-1])
                if -1 < num < k:
                    os.write(wList[2*num], b'ping')
                    data = os.read(rList[2*num+1], 4)
                    print(f'Response from P#{num} : {data}')
                else:
                    print("Error: unknown process")
            except ValueError:
                print('Error, wrong type')
main()
