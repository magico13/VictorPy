from bluepy import btle
import sys
import time

vector = None

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

print("Services...")
for svc in dev.getServices():
    print(str(svc))
    print("Characteristics: ")
    for char in svc.getCharacteristics():
        val = '<No Read Support>'
        if char.supportsRead(): val = str(char.read())
        print(str(char)+': '+val)
comSvc = dev.getServiceByUUID('fee3')
while True:
    for char in comSvc.getCharacteristics():
        val = '<No Read Support>'
        if char.supportsRead(): val = str(char.read())
        print(str(char)+': '+val)
    time.sleep(1)
  