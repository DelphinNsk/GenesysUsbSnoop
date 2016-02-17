## Genesys Wireshark USB Dump Decoder ##

### Description ###
This util analysing usb dump of genesys chip based scanner

#### Usage ###

before use you need install tshark that was used as main decode engine

then run:

./decode.py \<filename\>

it will create folder in the folder where \<filename\> with name \<filename\>_dump where will be stored decoded data

### Result data description ###

Captured data have different types:

1. Image binary data (image.data)
2. Gamma data ([num].gamma_*.dump)
3. Slope (([num].slope_*.dump)
4. Shading ([num].shading_*.dump)

where [num] is sequence number of write

