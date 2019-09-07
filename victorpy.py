from bluepy import btle
import sys

print "Scanning... Wait 5 seconds."
scanner = btle.Scanner()
results = scanner.scan(5)

vector = None

for res in results:
  if "Vector" in res.getValueText(9): #named vector
    pairable = (res.getValueText(255) == u'f8057670')
    print(str(res.getValueText(9)) + ' pairable? '+str(pairable))
    if pairable: vector = res

if not vector:
  print("No pairable robots found")
  sys.exit()

dev = btle.Peripheral(vector.addr, vector.addrType)

print "Services..."
for svc in dev.services:
  print(str(svc))
  print("Characteristics: ")
  for char in svc.getCharacteristics():
    val = '<No Read Support>'
    if char.supportsRead(): val = str(char.read())
    print(str(char)+': '+val)
  