import binascii
import struct

import Log

class USBRequest:
    c = None # commit packet
    s = None # submit packet
    def __init__(self,s,c):
        self.s = s
        self.c = c

class UsbUrb:
    URB_CONTROL = 0x02
    URB_BULK = 0x03
    URB_INTERRUPT = 0x01
    DIR_OUT = 0
    TYPE_SUBMIT = 0x53
    TYPE_COMPLETE = 0x43
    URB_SETUP_VENDOR = 0x02
    def __init__(self, packet):
        self.id = packet['usb.urb_id']
        self.bTransferType =  int(packet['usb.transfer_type'],16)
        self.isSubmit = int(packet['usb.urb_type'],16) == self.TYPE_SUBMIT;
        self.IsOut = int(packet['usb.endpoint_number.direction'],16) == self.DIR_OUT
        self.parseSetup(packet)
        self.parseData(packet)
    def parseData(self,packet):
        if 'usb.capdata' in packet:
            self.data = packet['usb.capdata']
        elif '' in packet:
            self.data = packet['']
            # print 'control data: '+self.data;
        else:
            self.data = ''

    def parseSetup(self,packet):
        self.bRequestType =  int(packet['usb.bmRequestType.type'],16)
        self.bRequestDir =  int(packet['usb.bmRequestType.direction'],16)
        if self.bRequestType == self.URB_SETUP_VENDOR:
            self.bSetupRequest = int(packet['usb.setup.bRequest'],16)
            self.wSetupValue = int(packet['usb.setup.wValue'],16)
            self.wSetupIndex = int(packet['usb.setup.wIndex'],16)

class USBHandler:
    LOG_NAME = 'USB'
    def __init__(self, handler, logs):
        self.handler = handler
        self.logs = logs
        self.sended = {}
        self.recived = {}

    def onPacket(self, packet ):
        urb = UsbUrb(packet);

        if urb.bTransferType == UsbUrb.URB_INTERRUPT:
            if urb.isSubmit:
                if urb.id in self.recived:
                    s = self.recived[urb.id]
                    self.handler.onRecvCommand(s,urb)
                    self.recived.pop(urb.id)
                else:
                    self.log("interrupt submit without complete id=0x{:}".format(urb.id))
            else:
                self.recived[urb.id] = urb
        else:
            if urb.isSubmit:
                self.sended[urb.id] = urb
            else:
                if urb.id in self.sended:
                    s = self.sended[urb.id]
                    self.handler.onSendCommand(s,urb)
                    self.sended.pop(urb.id)
                else:
                    self.log("complete without submit id=0x{:}".format(urb.id))

    def log(self, message):
        self.logs.log(self.LOG_NAME, message)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

