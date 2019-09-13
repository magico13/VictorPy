from bluepy import btle
import sys
import time

vector = None

readUUID = "30619f2d-0f54-41bd-a65a-7588d8c85b45"
writeUUID = "7d2a4bda-d29b-4152-b725-2491478c5cd7"
cccd = "00002902-0000-1000-8000-00805f9b34fb"

class BLEDelegate(btle.DefaultDelegate, object):
    def handleNotification(self, cHandle, data):
        print('handleNotification: cHandle: {0} data: {1}'.format(cHandle, data))
        super(BLEDelegate, self).handleNotification(cHandle, data)
    
    def handleDiscovery(self, scanEntry, isNewDev, isNewData):
        super(BLEDelegate, self).handleDiscovery(scanEntry, isNewDev, isNewData)
        name = scanEntry.getValueText(9)
        #if name:
            #print('handleDiscovery: name: {0} isNewDev: {1} isNewData: {2}'.format(name, isNewDev, isNewData))
        if name and isNewDev and "Vector" in name: #named vector
            factoryData = scanEntry.getValueText(255)
            pairable = (factoryData == u'f8057670')
            print('{0}({1}) pairable? {2}'.format(name, factoryData, pairable))
            if pairable or 'M2R6' in name: #todo: store last robot id
                global vector
                vector = scanEntry
      
def printBytes(bytes):
    print(','.join(str(b) for b in bytes))
        

scanner = btle.Scanner()
scanner.clear()
scanner.withDelegate(BLEDelegate())
scanner.start()
attempts = 0
print("Scanning...")
while (not vector and attempts < 10):
    scanner.process(1)
    attempts += 1
scanner.stop()
results = scanner.getDevices()

if not vector:
    print("No pairable robots found")
    sys.exit()
else: print('Connecting to {0}'.format(vector.getValueText(9)))
dev = btle.Peripheral(vector.addr, vector.addrType)



print("Services:")
for svc in dev.getServices():
    print('-'+str(svc))
    print("--Descriptors:")
    for desc in svc.getDescriptors():
        val = '<No Read Support>'
        try:
            val = desc.read()
        except: pass
        print('---{0}: {1}'.format(desc, val))
    print("--Characteristics: ")
    for char in svc.getCharacteristics():
        val = '<No Read Support>'
        if char.supportsRead(): val = str(char.read())
        print('---'+str(char)+': '+val)

comSvc = dev.getServiceByUUID('fee3')
readChar = comSvc.getCharacteristics(readUUID)[0]
writeChar = comSvc.getCharacteristics(writeUUID)[0]
cccdDesc = comSvc.getDescriptors(cccd)[0]

cccdDesc.write(bytes([1, 0]))

# read the current value
data = None
while True:
    data = readChar.read()
    printBytes(data)
    if len(data) > 0: break
    time.sleep(1)
    
# write the bytes '197,1,5,0,0,0'
b = bytes([197,1,5,0,0,0])
writeChar.write(b)

lastData = data
while True:
    data = readChar.read()
    if len(data) > 0 and data != lastData:
        lastData = data
        printBytes(data)
    time.sleep(0.1)
#print('Waiting 10s for notifications')
#attempts = 0
#while attempts < 10:
#    if dev.waitForNotifications(1): continue
#    attempts += 1

  