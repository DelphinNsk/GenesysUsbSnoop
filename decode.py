#!/usr/bin/env python

import libxml2
import subprocess
import xml.sax
import sys

import pdmlHandler
import USBBus
import GenesysChip
import Log

if __name__ == '__main__':
    filename = '../scans/scan50dpi2.pcapng'
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    log = Log.Log("{:s}.log".format(filename),["Genesys"])

    chip = GenesysChip.GenesysChip(filename,log)
    usb = USBBus.USBHandler( chip, log)
    handler = pdmlHandler.pdmlHandler( usb )

    pgmlStream = subprocess.Popen(['tshark','-r'+filename, '-Tpdml'], stdout=subprocess.PIPE);
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    parser.parse( pgmlStream.stdout )

