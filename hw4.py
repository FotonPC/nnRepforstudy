import os, sys, time, string, pickle, threading


class ListenerPassive:
    def __init__(self, rAdr):
        self.queue = list()
        self.rAdr = rAdr
        self.listening = [True]
        self.thread = threading.Thread(target=self.listen)
        self.thread.start()
    def listen(self):
        while self.listening[0]:
            self.queue.append(receiveObjPassive(self.rAdr))
            time.sleep(0.075)
    def close(self):
        self.listening[0] = False



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

def receiveObjPassive(rAdress):
    data = os.read(rAdress, 8)
    length = int(data.decode(), 16)
    data = os.read(rAdress, length)
    obj = pickle.loads(data)
    return obj

def sendObjPassive(wAdress, obj):
    data = pickle.dumps(obj)
    os.write(wAdress, bytes(hex(len(data))[2:].zfill(8), encoding='utf8'))
    os.write(wAdress, data)

def process_child(w, rm, r):
    self_data2 = dict()
    listener = ListenerPassive(rm)
    while True:
         data = os.read(r, 4)
         if data == b'getw':
            if len(listener.queue) > 0:
                self_data2 = listener.queue[-1]
            sendObjPassive(w, '; '.join([f"<{k}, {self_data2[k]}>" for k in self_data2.keys()]))
         elif data == b'kill':
             return
    

def start_processing(r, w, getw, n_children=3):
    self_data = dict()
    self_rlist = list()
    self_wlist = list()
    for i in range(n_children):
        r2, w2 = os.pipe()
        self_rlist.append(r2)
        self_wlist.append(w2)
    for i in range(n_children):
        pid = os.fork()
        if pid == 0:
            process_child(w, self_rlist[i], getw)
            return
    
    while True:
            
        data = os.read(r, 4)

        if data == b'ping':
            os.write(w, b'pong')
        elif data == b'kill':

            return
        elif data == b'load':
            data = receiveObjPassive(r)
            
            try:
                self_data[data] += 1
            except:
                self_data[data] = 1
            sendObjPassive(w, b'succ')
            for i in range(n_children):
                sendObjPassive(self_wlist[i], self_data)
        elif data == b'chec':
            data = receiveObj(r, w)
            if data in self_data.keys():
                os.write(w, b'here')
            else:
                os.write(w, b'nope')
        elif data == b'getw':
            sendObjPassive(w, '; '.join([f"<{k}, {self_data[k]}>" for k in self_data.keys()]))

def main():
    begin = time.perf_counter()
    alpha = string.ascii_letters
    k = len(alpha)
    rList = []
    wList = []
    rListGETw = []
    wListGETw = []
    for i in range(2*k):
        r, w = os.pipe()
        rList.append(r)
        wList.append(w)
    for i in range(k):
        r, w = os.pipe()
        rListGETw.append(r)
        wListGETw.append(w)
        pid = os.fork()
        if pid == 0:
            start_processing(rList[2*i], wList[2*i+1], rListGETw[-1])
            return
    while True:
        query = input(f'[{round(time.perf_counter()-begin, 3)}s] ~ ')
        query = query.split()
        if len(query) == 0:
            continue
        elif query[0] == 'kill' and len(query) == 2 and len(query[-1]) == 1:
            letter = query[-1]
            ind = alpha.index(query[-1])
            os.write(wList[2*ind], b'kill') 
        elif query[0] == 'kill' and query[-1] == 'all':
            for i in range(k):
                os.write(wList[2*i], b'kill')
                for j in range(3):
                    os.write(wListGETw[i], b'kill')
            print('All processes killed\n')
            exit(1)
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
            sendObjPassive(wList[2*ind], word)
            listener = ListenerPassive(rList[2*ind+1])
            beg = time.perf_counter()
            while len(listener.queue) == 0 and time.perf_counter()-beg < 0.05:
                pass
            listener.close()
            del listener.thread
            if len(listener.queue) > 0 and listener.queue[-1] == b'succ':
                print('Loading was succesfull')
            else:
                print('Unexpected problems! Upss')
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
            os.write(wListGETw[ind], b'getw')

            print('Answer:', receiveObjPassive(rList[2*ind+1]))


        elif len(query) > 0:
            print('Error, unknown command')
main()
