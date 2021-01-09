nRF Connect, 2021-01-07
SmartRow ()
V    18:14:02.183    Connecting to
D    18:14:02.183    gatt = device.connectGatt(autoConnect = false, TRANSPORT_LE, preferred PHY = LE 1M)
D    18:14:02.562    [Callback] Connection state changed with status: 0 and new state: CONNECTED (2)
I    18:14:02.562    Connected to F9:FA:97:16:EF:F2
V    18:14:02.594    Discovering services...
D    18:14:02.594    gatt.discoverServices()
D    18:14:02.596    [Broadcast] Action received: android.bluetooth.device.action.ACL_CONNECTED
I    18:14:02.797    Connection parameters updated (interval: 7.5ms, latency: 0, timeout: 5000ms)
D    18:14:02.898    [Callback] Services discovered with status: 0
I    18:14:02.898    Services discovered
V    18:14:02.923    Generic Access (0x1800)
- Device Name [R W] (0x2A00)
- Appearance [R] (0x2A01)
- Peripheral Preferred Connection Parameters [R] (0x2A04)
Generic Attribute (0x1801)
Unknown Service (00001234-0000-1000-8000-00805f9b34fb)
- Unknown Characteristic [WNR] (00001235-0000-1000-8000-00805f9b34fb)
- Unknown Characteristic [N R] (00001236-0000-1000-8000-00805f9b34fb)
  Client Characteristic Configuration (0x2902)
D    18:14:02.924    gatt.setCharacteristicNotification(00001236-0000-1000-8000-00805f9b34fb, true)
I    18:14:02.959    Connection parameters updated (interval: 35.0ms, latency: 0, timeout: 5000ms)
I    18:14:07.692    Connection parameters updated (interval: 30.0ms, latency: 0, timeout: 4000ms)
D    18:16:05.655    [Callback] Connection state changed with status: 8 and new state: DISCONNECTED (0)
E    18:16:05.656    Error 8 (0x8): GATT CONN TIMEOUT
I    18:16:05.656    Disconnected
D    18:16:05.729    [Broadcast] Action received: android.bluetooth.device.action.ACL_DISCONNECTED
D    18:16:53.603    gatt.close()
D    18:16:53.606    wait(200)
V    18:16:53.809    Connecting to
D    18:16:53.810    gatt = device.connectGatt(autoConnect = false, TRANSPORT_LE, preferred PHY = LE 1M)
D    18:16:54.118    [Callback] Connection state changed with status: 0 and new state: CONNECTED (2)
I    18:16:54.118    Connected to
V    18:16:54.155    Discovering services...
D    18:16:54.155    gatt.discoverServices()
D    18:16:54.177    [Broadcast] Action received: android.bluetooth.device.action.ACL_CONNECTED
I    18:16:54.364    Connection parameters updated (interval: 7.5ms, latency: 0, timeout: 5000ms)
D    18:16:54.465    [Callback] Services discovered with status: 0
I    18:16:54.466    Services discovered
V    18:16:54.487    Generic Access (0x1800)
- Device Name [R W] (0x2A00)
- Appearance [R] (0x2A01)
- Peripheral Preferred Connection Parameters [R] (0x2A04)
Generic Attribute (0x1801)
Unknown Service (00001234-0000-1000-8000-00805f9b34fb)
- Unknown Characteristic [WNR] (00001235-0000-1000-8000-00805f9b34fb)
- Unknown Characteristic [N R] (00001236-0000-1000-8000-00805f9b34fb)
  Client Characteristic Configuration (0x2902)
D    18:16:54.488    gatt.setCharacteristicNotification(00001236-0000-1000-8000-00805f9b34fb, true)
I    18:16:54.532    Connection parameters updated (interval: 35.0ms, latency: 0, timeout: 5000ms)
I    18:16:59.232    Connection parameters updated (interval: 30.0ms, latency: 0, timeout: 4000ms)


