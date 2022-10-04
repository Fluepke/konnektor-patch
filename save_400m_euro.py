#!/bin/env python3

CMD_SELECT = 0xA4
CMD_READ_BINARY = 0xB0

DF_NK =   bytes([0xD2, 0x76, 0x00, 0x01, 0x44, 0x03])
EF_C_NK_VPN_R2048 = bytes([0xC5, 0x05])

CARD_FS = {
    DF_NK: {
        EF_C_NK_VPN_R2048: {
            'sfid': 0x05,
            'replacement': './C_NK_VPN_R2048.der'
        }
    }
}

#from virtualsmartcard.VirtualSmartcard import SmartcardOS
from smartcard.System import readers
from smartcard.Exceptions import NoCardException

class PatchCard():
    """
    gSMC-K wrapper, intercepts read commands for the following files:
      * MF /DF.NK/ EF.C.NK.VPN.R2048
      * MF /DF.AK/ EF.C.AK.AUT.R2048
      * MF / DF.SAK / EF.C.SAK.AUT.R2048
    """
    def __init__(self):
        self.current_df = b''
        self.current_ef = b''
        for reader in readers():
            try:
                print(reader)
                self.connection = reader.createConnection()
                connection.connect()
            except NoCardException:
                print(reader, 'no card inserted')
            except:
                print(reader, 'connection failed')

    def getATR(self):
        return self.connection.getATR()

    def execute(self, msg):
        if msg[1] == CMD_SELECT: # ref: ISO/IEC 7846-4:4:2020, table 62
            if msg[2] == 0x04: # Select by DF name
                self.current_df = bytes(msg[5:])
            elif msg[2] == 0x02: # Select EF unter the DF referenced by curDF
                self.current_ef = bytes(msg[5:])
            else:
                pass # TODO support all selection mode and keep track of currently selected df
        if msg[1] == CMD_READ_BINARY: # TODO support Short File Identifiers
            if self.current_df in CARD_FS and self.current_ef in CARD_FS[self.current_df]:
                ef = CARD_FS[self.current_df]
                # TODO implement read operations on the 'replacement' file
            
        if msg in commands_and_response:
            print("< " + msg.hex())
            resp_c = response_counter[msg]
            len_r = len(commands_and_response[msg])
            resp = commands_and_response[msg][resp_c % len_r]
            response_counter[msg] += 1
            print("> " + msg.hex())
            return resp
        print("Unknown APDU! " + msg.hex())
        return b'\x6d\x00'

if __name__ == "__main":
    c = PatchCard()