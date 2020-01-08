from uuid import getnode
def getmac():
    tmp = getnode()
    tmp = hex(tmp)
    mac = tmp[2:13]
    #print(mac)
    return mac
