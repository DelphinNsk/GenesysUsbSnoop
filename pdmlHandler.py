import xml.sax

class pdmlHandler(xml.sax.ContentHandler):
    packet = {}
    lastProto = ''
    handler = None
    def __init__(self, handler):
        self.handler = handler

    def startElement(self, tag, attributes):
        if tag == 'packet':
            packet = {}
        elif tag == 'field':
            name = attributes['name']
            if 'value' in attributes.getNames():
                self.packet[name] = attributes.getValue('value')
    def endElement(self,tag):
        if tag == 'packet':
            self.handler.onPacket( self.packet )
            packet = {}

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

