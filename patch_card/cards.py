
from virtualsmartcard.cards.Relay import RelayOS
from virtualsmartcard.CardGenerator import CardGenerator
from virtualsmartcard.VirtualSmartcard import Iso7816OS

class PatchCard(RelayOS):
    """
    We are using the RelayOS virtual smartcard and patch some pdus
    """
    def execute(self, msg):
        """Intercept message"""
        # Forward to card and return response
        reply = super().execute(msg)
        return reply


class SimulCard(Iso7816OS):
    def __init__(self, *args, **kwargs):
        gen = CardGenerator("iso7816")
        MF, SAM = gen.getCard()
        super().__init__(MF, SAM)

