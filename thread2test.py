import time
from queue import Queue


def Ble_reset_test(out_q):
    while True:
        time.sleep(5)
        print(out_q)
        print("going to reset")
        out_q.put("reset_ble")
        print("output filled with reset")
