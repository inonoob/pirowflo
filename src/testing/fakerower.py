import itertools
import time
import binascii

result = []

def FakeSmartRowerData(f,deque_input):
    #print("in the function")
    for index, line in enumerate(itertools.islice(f, 1, None, 2)):
        #print(line)
        line = line.strip()
        #print(line)
        line = line.split(' ')[-1]
        #print(line)
        test = line.split("-")
        #print(test)
        test1 = []
        for bt in test:
            #convertdata = bt.encode("utf-8")
            hex_int = int(bt, 16)
            test1.append(hex_int)

        #print(test1)
        deque_input.append(test1)
        time.sleep(0.1)


def main(in_q, ble_out_q):
    f = open("/home/pi/fakesmartrow/testing/Log_2021-01-08_21_16_57.txt", "r")
    while True:
        FakeRowData = FakeSmartRowerData(f,ble_out_q)



if __name__ == '__main__':
    f = open("Log_2021-01-08_21_16_57.txt", "r")
    test = []
    FakeSmartRowerData(f,test)
