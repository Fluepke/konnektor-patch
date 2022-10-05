
import logging

from virtualsmartcard.SWutils import SW
from virtualsmartcard.ConstantDefinitions import FDB
from virtualsmartcard.cards.Relay import RelayOS
from virtualsmartcard.CardGenerator import CardGenerator
from virtualsmartcard.utils import C_APDU, R_APDU, hexdump, inttostring
from virtualsmartcard.VirtualSmartcard import Iso7816OS
from virtualsmartcard.SmartcardFilesystem import MF, DF, TransparentStructureEF

CMD_SELECT_FILE = 0xA4

# Directory Files
DF_AK  = bytes([0xD2, 0x76, 0x00, 0x01, 0x44, 0x02])
DF_NK  = bytes([0xD2, 0x76, 0x00, 0x01, 0x44, 0x03])
DF_SAK = bytes([0xD2, 0x76, 0x00, 0x01, 0x44, 0x04])

# Elementary Files
EF_C_AK_AUT_R2048  = 0xC503 # bytes([0xC5, 0x03])
EF_C_NK_VPN_R2048  = 0xC505 # bytes([0xC5, 0x05])
EF_C_SAK_AUT_R2048 = 0xC506 # bytes([0xC5, 0x06])


def is_seekable(ins):
    return ins in [
        0xb0, 0xb1, 0xd0, 0xd1, 0xd6, 0xd7, 0xa0, 0xa1, 0xb2, 0xb3,
        0xdc, 0xdd,
    ]


def create_filesystem():
    """
    Create the card fileystem with the certificate files
    """
    mf = MF(filedescriptor=FDB["DF"])

    # AK_AUT
    df = DF(parent=mf, fid=0x01, dfname=DF_AK)
    ef = TransparentStructureEF(
            parent=df, fid=0xC503, shortfid=0x03, data=b"CERT DATA")
    df.append(ef)
    mf.append(df)

    # NK_VPN
    df = DF(parent=mf, fid=0xAA00, dfname=DF_NK)
    ef = TransparentStructureEF(
            parent=df, fid=0xC505, shortfid=0x05, data=b"CERT DATA")
    df.append(ef)
    mf.append(df)

    # DF_SAK 
    df = DF(parent=mf, fid=0x02, dfname=DF_SAK)
    ef = TransparentStructureEF(
            parent=df, fid=0xC505, shortfid=0x06, data=b"CERT DATA")
    df.append(ef)
    mf.append(df)

    return mf


class PatchCard(RelayOS):
    """
    We are using the RelayOS virtual smartcard and patch some pdus
    """
    def __init__(self, *args, **kwargs):
        """Initialize interceptor card"""
        self.intercept_file = False
        self.intercept_mf = create_filesystem()
        self.intercept_handlers = {
            0x0c: self.intercept_mf.eraseRecord,
            0x0e: self.intercept_mf.eraseBinaryPlain,
            0x0f: self.intercept_mf.eraseBinaryEncapsulated,
            0xa0: self.intercept_mf.searchBinaryPlain,
            0xa1: self.intercept_mf.searchBinaryEncapsulated,
            0xa4: self.intercept_mf.selectFile,
            0xb0: self.intercept_mf.readBinaryPlain,
            0xb1: self.intercept_mf.readBinaryEncapsulated,
            0xb2: self.intercept_mf.readRecordPlain,
            0xb3: self.intercept_mf.readRecordEncapsulated,
            0xca: self.intercept_mf.getDataPlain,
            0xcb: self.intercept_mf.getDataEncapsulated,
            0xd0: self.intercept_mf.writeBinaryPlain,
            0xd1: self.intercept_mf.writeBinaryEncapsulated,
            0xd2: self.intercept_mf.writeRecord,
            0xd6: self.intercept_mf.updateBinaryPlain,
            0xd7: self.intercept_mf.updateBinaryEncapsulated,
            0xda: self.intercept_mf.putDataPlain,
            0xdb: self.intercept_mf.putDataEncapsulated,
            0xdc: self.intercept_mf.updateRecordPlain,
            0xdd: self.intercept_mf.updateRecordEncapsulated,
            0xe0: self.intercept_mf.createFile,
            0xe2: self.intercept_mf.appendRecord,
            0xe4: self.intercept_mf.deleteFile,
        }

        super().__init__(*args, **kwargs)

    def execute(self, msg):
        """Intercept message"""
        # Parse PDU
        try:
            c = C_APDU(msg)
            logging.debug("%s", str(c))
        except ValueError as e:
            logging.warning(str(e))
            # Pass to card and return
            return super().execute(msg)

        # Run on SC
        reply = super().execute(msg)

        # Run on virtual FS
        handler = self.intercept_handlers.get(c.ins)
        if handler and c.ins == CMD_SELECT_FILE:
            try:
                # File not found will raise an error
                self.intercept_mf.selectFile(c.p1, c.p2, c.data)
                self.intercept_file = True
            except:
                self.intercept_file = False

        elif handler and self.intercept_file:
            v_reply = handler(c.p1, c.p2, c.data)
            return v_reply

        return reply



class SimulCard(Iso7816OS):
    def __init__(self, *args, **kwargs):
        gen = CardGenerator("iso7816")
        mf, sam = gen.getCard()

        self.intercept_file = False
        self.intercept_mf = create_filesystem()
        self.intercept_handlers = {
            0x0c: self.intercept_mf.eraseRecord,
            0x0e: self.intercept_mf.eraseBinaryPlain,
            0x0f: self.intercept_mf.eraseBinaryEncapsulated,
            0xa0: self.intercept_mf.searchBinaryPlain,
            0xa1: self.intercept_mf.searchBinaryEncapsulated,
            0xa4: self.intercept_mf.selectFile,
            0xb0: self.intercept_mf.readBinaryPlain,
            0xb1: self.intercept_mf.readBinaryEncapsulated,
            0xb2: self.intercept_mf.readRecordPlain,
            0xb3: self.intercept_mf.readRecordEncapsulated,
            0xca: self.intercept_mf.getDataPlain,
            0xcb: self.intercept_mf.getDataEncapsulated,
            0xd0: self.intercept_mf.writeBinaryPlain,
            0xd1: self.intercept_mf.writeBinaryEncapsulated,
            0xd2: self.intercept_mf.writeRecord,
            0xd6: self.intercept_mf.updateBinaryPlain,
            0xd7: self.intercept_mf.updateBinaryEncapsulated,
            0xda: self.intercept_mf.putDataPlain,
            0xdb: self.intercept_mf.putDataEncapsulated,
            0xdc: self.intercept_mf.updateRecordPlain,
            0xdd: self.intercept_mf.updateRecordEncapsulated,
            0xe0: self.intercept_mf.createFile,
            0xe2: self.intercept_mf.appendRecord,
            0xe4: self.intercept_mf.deleteFile,
        }

        self.last_command_offcut = b""
        self.last_command_sw = SW["normal"]

        super().__init__(mf, sam)


    def format_result(self, seekable, le, data, sw):
        """See Iso7816O implementation"""
        if not seekable:
            self.last_command_offcut = data[le:]
            l = len(self.last_command_offcut)
            if l == 0:
                self.last_command_sw = SW["NORMAL"]
            else:
                self.last_command_sw = sw
                sw = SW["NORMAL_REST"] + min(0xff, l)
        else:
            if le > len(data):
                sw = SW["WARN_EOFBEFORENEREAD"]

        if le is not None:
            result = data[:le]
        else:
            result = data[:0]

        return R_APDU(result, inttostring(sw)).render()


    def execute(self, msg):
        """Intercept message"""
        # Parse PDU
        try:
            c = C_APDU(msg)
            logging.debug("%s", str(c))
        except ValueError as e:
            logging.warning(str(e))
            # Pass to card and return
            return super().execute(msg)


        # Run on SC
        reply = super().execute(msg)

        # Run on virtual FS
        handler = self.intercept_handlers.get(c.ins)
        if handler and c.ins == CMD_SELECT_FILE:
            try:
                # File not found will raise an error
                self.intercept_mf.selectFile(c.p1, c.p2, c.data)
                self.intercept_file = True
            except:
                self.intercept_file = False

        elif handler and self.intercept_file:
            sw, result = handler(c.p1, c.p2, c.data)
            return self.format_result(
                is_seekable(c.ins),
                c.effective_Le,
                result,
                sw)

        return reply
