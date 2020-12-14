
import WaterrowerBle
import WaterrowerInterface
import threading
from queue import Queue

def main():

    def BleService(out_q):
        print("THREAD - Start BLE Advertise and BLE GATT Server")
        bleService = WaterrowerBle.main()
        bleService()


    def Waterrower(in_q):
        print("THREAD - Start BLE GATT Server")
        Waterrowerserial = WaterrowerInterface.main(in_q)
        Waterrowerserial()

    # def task3():
    #     print("THREAD - Start RS232 Interface")
    #     interface = rs232.main()
    #     interface()

    q = Queue()
    t1 = threading.Thread(target=BleService,args =(q, ))
    t2 = threading.Thread(target=Waterrower,args =(q, ))
    # t3 = threading.Thread(target=task3) # will be for ant+
    # t4 = threading.Thread(target=task4)

    t1.start()
    t2.start()
    #t3.start() Would be for Ant+
    # t4.start()

    # t1.join()
    # t2.join()
    # t3.join()


if __name__ == '__main__':
    main()