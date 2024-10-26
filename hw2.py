import os, sys, time, string

def start_processing(r, w):
    self_data = []
    while True:
        data = os.read(r, 4)
        if data == b'ping':
            os.write(w, b'pong')
        elif data == b'kill':
            os.write(w, b'okay')
            return
        elif data == b'load':
            os.write(w, b'read')
            data = os.read(r, 8)
            num = int(data.decode(), 16)
            os.write(w, b'entr')
            data = os.read(r, num)
            self_data.append(data)
            os.write(w, b'succ')
        elif data == b'chec':
            os.write(w, b'read')
            data = os.read(r, 8)
            num = int(data.decode(), 16)
            os.write(w, b'entr')
            data = os.read(r, num)
            if data in self_data:
                os.write(w, b'here')
            else:
                os.write(w, b'nope')
def main():
    alpha = string.ascii_letters
    k = len(alpha)
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
        if len(query) == 0:
            continue
        elif query[0] == 'kill' and query[-1] == 'all':
            for i in range(k):
                os.write(wList[2*i], b'kill')
                data = os.read(rList[2*i+1], 4) # okay
                print(f'\rProcess #{i} kill: {data}', end='')
                time.sleep(0.01)
            print('\n\-_-/ All processes killed')
            return
        elif query[0] == 'ping':
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
        elif query[0] == 'load' and len(query) == 2:
            word = query[-1]
            if not word.isalpha():
                print("Error, its not a word")
                continue
            ind = alpha.index(word[0])
            os.write(wList[2*ind], b'load')
            assert os.read(rList[2*ind+1], 4) == b'read'
            os.write(wList[2*ind], bytes(hex(len(word))[2:].zfill(8), encoding='utf8'))
            assert os.read(rList[2*ind+1], 4) == b'entr'
            os.write(wList[2*ind], bytes(word, encoding='utf8'))
            if os.read(rList[2*ind+1], 4) == b'succ':
                print('Loading was succesfull')
        elif query[0] == 'check' and len(query) == 2:
            word = query[-1]
            if not word.isalpha():
                print('Error its not a word!')
                continue
            ind = alpha.index(word[0])
            os.write(wList[2*ind], b'chec')
            assert os.read(rList[2*ind+1], 4) == b'read'
            os.write(wList[2*ind], bytes(hex(len(word))[2:].zfill(8), encoding='utf8'))
            assert os.read(rList[2*ind+1], 4) == b'entr'
            os.write(wList[2*ind], bytes(word, encoding='utf8'))
            if os.read(rList[2*ind+1], 4) == b'here':
                print('Word is in memory')
            else:
                print('Word isnt in memory')



        elif len(query) > 0:
            print('Error, unknown command')
main()
