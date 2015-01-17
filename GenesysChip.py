from USBBus import UsbUrb
import struct
import binascii
import os
import shutil
import array

def dataToRegValue(data):
    return int( data[-2:],16)


class GenesysChip:
    LOG_NAME = 'Genesys'
    def __init__(self, filename, logs):
        self.logs = logs
        self.filename = filename
        self.file = None
        self.size = 0
        self.reg = {}
        self.folder= filename+"_dump"

        if os.path.exists(self.folder):
                shutil.rmtree(self.folder)

        os.mkdir(self.folder)

    def onRecvCommand(self,s,c):
            self.log("some recived usb command")

    def onSendCommand(self,s,c):
        if s.bTransferType == UsbUrb.URB_CONTROL:
            self.onControl(s,c)
        elif s.bTransferType == UsbUrb.URB_BULK:
            self.onBulk(s,c)

    def onBulkOut(self,data):
        words = array.array('H',data)
        for word in words:
                self.file.write("{:d} ".format(word));

    def onBulkIn(self,data):
        self.file.write(data)

    def onBulk(self,s,c):
        info = 'BULK'
        if s.IsOut:
            info = info + ' OUT'
            binData = binascii.unhexlify(s.data)
            self.onBulkOut(binData)
        else:
            info = info + ' IN'
            binData = binascii.unhexlify(c.data)
            self.onBulkIn(binData)

        self.size = self.size - len(binData)
        self.log(info)

        if (self.size <= 0 ):
                self.file.close()

    def onControl(self,s,c):
        if s.bRequestType == UsbUrb.URB_SETUP_VENDOR:  #vendor
            setupValueH = (s.wSetupValue >> 8) & 0xff
            setupValueL = s.wSetupValue & 0xff

            if s.bRequestDir == 1:  #in
                if s.bSetupRequest == 0x0c: #REQUEST_REGISTER
                    if setupValueH == 0x8e: #VALUE_GET_REGISTER
                        self.onInRegisterGet(s,c);
                        #sanei_usb_control_msg (REQUEST_TYPE_IN, REQUEST_REGISTER, VALUE_GET_REGISTER, 0x00, 1, &val);
                    elif setupValueH == 0x84: #VALUE_READ_REGISTER
                        self.onInRegisterRead(s,c);
                    else:
                        self.log("Unknown in register value 0x{:04x}".format(s.wSetupValue))
                elif s.bSetupRequest == 0x04: #REQUEST_BUFFER
                    if setupValueH == 0x8e: #VALUE_GET_REGISTER
                        if setupValueL == 0x00:
                            self.onInBufferGet(s,c)
                        else:
                            self.onInBufferGetH(s,c)
                    else:
                        self.log( "Unknown in buffer value 0x{:04x}".format(s.wSetupValue) )
            else: #out
                if s.bSetupRequest == 0x04: #register
                    if setupValueH == 0x82:
                        self.onBuffPreAccess(s,c)
                    elif setupValueH == 0x83:
                        if setupValueL == 0x01:
                            self.onWritehRegister(s,c)
                        else:
                            self.onWritehRegister(s,c)
                    else:
                        self.log("Unknown in buffer value 0x{:04x}".format(s.wSetupValue))

    def getFilename(self,addr,bulkDir):
        filenameBase = "{:s}_{:08x}.dump".format(bulkDir,addr)
        if bulkDir=='IN':
            if addr == 0x10000000:
                return ('image.data'.format(self.filename), "ab")

        if addr &  0x01000000 != 0: # gamma
            colorNum = (addr - 0x01000000 ) /0x200 # step is 0x200
            color = ["r","g","b"][colorNum]
            filenameBase = "gamma_{:s}.dump".format(color)

        if addr &  0x10000000 != 0: # slope or shading data
            if addr >= 0x10014000: #shading data
                colorNum = (addr - 0x10014000) / 0x2A000 # step is 0x2A000
                color = ["r","g","b"][colorNum]
                filenameBase = "shading_{:s}.dump".format(color)
            else:
                slopeNum = (addr - 0x10000000) / 0x4000 # step is 0x4000
                filenameBase = "slope_{:d}.dump".format(slopeNum)

        i = 0
        filename = "{:d}.{:s}".format(i,filenameBase)

        while os.path.exists(os.path.join(self.folder,filename)):
            i = i + 1
            filename = "{:d}.{:s}".format(i,filenameBase)

        return (filename,"a")

    def onBuffPreAccess(self,s,c):
        (addr,size) = struct.unpack('II', binascii.unhexlify(s.data) )

        isOut = s.wSetupIndex == 0x0100
        if isOut:
                bulkDir ='OUT'
        else:
                bulkDir = 'IN'

        (filename,mode) = self.getFilename(addr,bulkDir)

        info = 'sanei_genesys_write_ahb( ADDR=0x{:08x} size={:d} BULK_{:s} file={:s}'.format(addr,size,bulkDir,filename)
        self.log( info )

        filepath = os.path.join(self.folder, filename )

        self.file = open(filepath,mode);
        self.size = size;
        # self.handler.onReadBuffPreAccess(addr,size,isOut)

    def onWriteRegister(self,s,c):
        data = s.data
        (reg,val) = struct.unpack('BB', binascii.unhexlify(data) )
        info = 'sanei_genesys_write_register(0x{:02x},0x{:02x})'.format(reg,val)
        self.reg[reg]=val;
        self.log( info )

    def onWritehRegister(self,s,c):
        data = s.data
        (reg,val) = struct.unpack('BB', binascii.unhexlify(data) )
        info = 'sanei_genesys_write_hregister(0x{:02x},0x{:02x})'.format(reg,val)
        self.reg[reg]=val;
        self.log( info )

    def onInRegisterRead(self,s,c):
        self.log("sanei_usb_control_msg(dev->dn, REQUEST_TYPE_IN, REQUEST_REGISTER,VALUE_READ_REGISTER, INDEX, 1, val);")

    def onInRegisterGet(self,s,c):
        bReg = s.wSetupIndex & 0xff
        bResult = dataToRegValue(c.data)
        self.log("InRegisterGet(0x{:02x})=0x{:02x}".format(bReg,bResult))
        return
    def onInBufferGet(self,s,c):
        bReg = s.wSetupIndex & 0xff
        bResult = dataToRegValue(c.data)
        self.log( "sanei_genesys_read_register(0x{:02x})=0x{:02x}".format(bReg, bResult))
        return

    def onInBufferGetH(self,s,c):
        bReg = s.wSetupIndex & 0xff
        bResult = dataToRegValue(c.data)
        self.log( "sanei_genesys_read_register(0x1{:02x})=0x{:02x}".format(bReg, bResult))

    def log( self, message ):
        self.logs.log(self.LOG_NAME,message);

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
