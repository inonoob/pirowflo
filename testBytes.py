import struct


WaterrowerValuesRaw = {
    'stroke_rate': 24,
    'total_strokes': 954,
    'total_distance_m': 11250,
    'instantaneous pace': 450.32,
    'watts': 0,
    'total_kcal': 0,
    'total_kcal_hour': 0,
    'total_kcal_min': 0,
    'heart_rate': 0,
    'elapsedtime': 0.0,
}

WRBytearray = []
for keys in WaterrowerValuesRaw:
    WaterrowerValuesRaw[keys] = int(WaterrowerValuesRaw[keys])
    print(WaterrowerValuesRaw[keys])
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['stroke_rate'] & 0xff)))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_strokes'] & 0xff)))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_strokes'] & 0xff00) >> 8))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_distance_m'] & 0xff)))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_distance_m'] & 0xff00) >> 8))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_distance_m'] & 0xff0000) >> 16))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['instantaneous pace'] & 0xff)))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['instantaneous pace'] & 0xff00) >> 8))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['watts'] & 0xff)))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['watts'] & 0xff00) >> 8))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_kcal'] & 0xff)))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_kcal'] & 0xff00) >> 8))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_kcal_hour'] & 0xff)))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_kcal_hour'] & 0xff00) >> 8))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['total_kcal_min'] & 0xff)))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['heart_rate'] & 0xff)))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['elapsedtime'] & 0xff)))
WRBytearray.append(struct.pack("B", (WaterrowerValuesRaw['elapsedtime'] & 0xff00) >> 8))
print(WRBytearray)