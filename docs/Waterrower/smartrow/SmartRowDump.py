import itertools
import binascii

f = open("docs/Waterrower/Smartrowdump.txt", "r")



result = []
resultascii = []
resultasciispacearray = []

for line in itertools.islice(f, 1, None, 2):
    line = line.strip()
    line = line.split(' ')[-1]
    line = line.replace("-", " ")
    #print(line)
    #resultascii.append(binascii.unhexlify(line))
    result.append(line)
    line = line.replace(" ", "")
    resultascii.append(binascii.unhexlify(line))

    #resultasciispacearray.append = resultasciispace


#print(result)
#print(resultascii)
#print(resultascii[30])


# r = open("/home/ino/PycharmProjects/WaterrowerAntBle/docs/Waterrower/decode.txt","w")
# for i in result:
#     r.write(i)
#     r.write("\n")
#
# s = open("/home/ino/PycharmProjects/WaterrowerAntBle/docs/Waterrower/decode2.txt","w")
# for z in resultascii:
#     #print(z)
#     print(z.decode("utf-8"))
#     s.write(z.decode("utf-8"))
#     s.write(("\n"))
#
#
a = open("/docs/Waterrower/decodeA.txt", "w")
for x in resultascii:
    #print(z)
    test = x.decode("utf-8")
    firstchar = test.split(" ")[0]
    firstchar = firstchar[0]
    #print(firstchar)
    if firstchar == "a":
        #print(x.decode("utf-8"))
        a.write(x.decode("utf-8"))
        a.write(("\n"))

to = open("/docs/Waterrower/decode.txt", "w")

together = []
for l in range(len(resultascii)):

    together.append(result[l] +" "+ resultascii[l].decode("utf-8"))
    #print(together)

toA = open("/docs/Waterrower/decodeA.txt", "w")

for f in together:
    f = f[:51] + "| " + f[51:]
    # f = f[:52] + " " + f[52:]
    # f = f[:58] + " " + f[58:]
    f = f[:54] + " " + f[54:]
    f = f[:60] + " " + f[60:]
    to.write(f)
    to.write(("\n"))

    firstchar = f.split(" ")[0]

    if firstchar == "7A":
        print(f)
        toA.write(f)
        toA.write(("\n"))

