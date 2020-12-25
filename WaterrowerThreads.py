import WaterrowerBle
import WaterrowerInterface
import threading
from queue import Queue
from collections import deque


def main():
    def BleService(out_q, ble_in_q):
        print("THREAD - Start BLE Advertise and BLE GATT Server")
        bleService = WaterrowerBle.main(out_q, ble_in_q)
        bleService()

    def Waterrower(in_q, ble_out_q):
        print("THREAD - Start BLE GATT Server")
        Waterrowerserial = WaterrowerInterface.main(in_q, ble_out_q)
        Waterrowerserial()

    # def task3():
    #     print("THREAD - Start RS232 Interface")
    #     interface = rs232.main()
    #     interface()
    # TODO: Switch from queue to deque
    q = Queue()
    ble_q = deque(maxlen=1)
    t1 = threading.Thread(target=BleService, args=(q, ble_q))
    t2 = threading.Thread(target=Waterrower, args=(q, ble_q))
    t1.start()
    t2.start()


if __name__ == '__main__':
    main()
