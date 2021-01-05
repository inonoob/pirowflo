"""Waterrower Ant and BLE Raspberry Pi Module
                                                             +-+
                                           XX+-----------------+
              +-------+                 XXXX    |----|       | |
               +-----+                XXX +----------------+ | |
               |     |             XXX    |XXXXXXXXXXXXXXXX| | |
+--------------X-----X----------+XXX+------------------------+-+
|                                                              |
+--------------------------------------------------------------+

Python script to broadcast waterrower data over BLE and ANT

"""

import argparse



parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawTextHelpFormatter,)
#We must specify both shorthand ( -n) and longhand versions ( --name)
parser.add_argument("-b", "--blue" , choices=[True, False], type=bool, default=True, help="Broadcast Waterrower data over bluetooth low energy" )
parser.add_argument("-a", "--antfe", choices=[True, False], type=bool, default=False, help="Broadcast Waterrower data over Ant+")
#ap.add_argument("-ahr", "--anfhr", help="Get heart rate from ant heart rate monitor")
#ap.add_argument("-s", "--smro", help="use smartrow as input value"



def main(args):
    print("test")
    print(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter, )
    # We must specify both shorthand ( -n) and longhand versions ( --name)
    parser.add_argument("-b", "--blue",  action='store_true', default=False, help="Broadcast Waterrower data over bluetooth low energy")
    parser.add_argument("-a", "--antfe", action='store_true', default=False, help="Broadcast Waterrower data over Ant+")
    args = parser.parse_args()
    print(args)
    main(args)