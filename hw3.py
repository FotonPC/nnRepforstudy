import os, sys, time, string, pickle

def sendObj(rAdress, wAdress, obj):
    data = pickle.dumps(obj)
    assert os.read(rAdress, 4) == b'read'
    os.write(wAdress, bytes(hex(len(data))[2:].zfill(8), encoding='utf8'))
    assert os.read(rAdress, 4) == b'entr'
    os.write(wAdress, data)
    assert os.read(rAdress, 4) == b'succ'
    return 1

def receiveObj(rAdress, wAdress):
    os.write(wAdress, b'read')
    data = os.read(rAdress, 8)
    lenght = int(data.decode(), 16)
    os.write(wAdress, b'entr')
    data = os.read(rAdress, lenght)
    os.write(wAdress, b'succ')
    obj = pickle.loads(data)
    return obj

def start_processing(r, w):
    self_data = dict()
    while True:
        data = os.read(r, 4)
        if data == b'ping':
            os.write(w, b'pong')
        elif data == b'kill':
            os.write(w, b'okay')
            return
        elif data == b'load':
            data = receiveObj(r, w)
            try:
                self_data[data] += 1
            except:
                self_data[data] = 1
            os.write(w, b'succ')
        elif data == b'chec':
            data = receiveObj(r, w)
            if data in self_data.keys():
                os.write(w, b'here')
            else:
                os.write(w, b'nope')
        elif data == b'getw':
            data = receiveObj(r, w)
            sendObj(r, w, '; '.join([f"<{k}, {self_data[k]}>" for k in self_data.keys()]))
            
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
                print("Error, it's not a word")
                continue
            ind = alpha.index(word[0])
            os.write(wList[2*ind], b'load')
            if sendObj(rList[2*ind+1], wList[2*ind], word):
                if os.read(rList[2*ind+1], 4) == b'succ':
                    print('Loading was succesfull')
        elif query[0] == 'check' and len(query) == 2:
            word = query[-1]
            if not word.isalpha():
                print('Error its not a word!')
                continue
            ind = alpha.index(word[0])
            os.write(wList[2*ind], b'chec')
            if sendObj(rList[2*ind+1], wList[2*ind], word):
                if os.read(rList[2*ind+1], 4) == b'here':
                    print('Word is in memory')
                else:
                    print("Word isn't in memory")
        elif query[0] == 'get' and len(query) == 2 and len(query[-1]) == 1:
            letter = query[-1]
            if not letter in alpha:
                print("It's not a letter!")
            ind = alpha.index(letter)
            os.write(wList[2*ind], b'getw')
            if sendObj(rList[2*ind+1], wList[2*ind], letter):
                print('Answer:', receiveObj(rList[2*ind+1], wList[2*ind]))


        elif len(query) > 0:
            print('Error, unknown command')
main()
