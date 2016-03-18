"""
This module deals with the communication with UI-enabled clients, using
websockets.

(mostly unpopulated, I expect Nic will work on this module elsewhere to begin
with)
"""

class UIServer:
    """Class acting as websocket server for the UI."""

    def Start(self):
        """
        Start up the server. This is a blocking method, not returning until
        the server is shut down.
        """
        # Temporary loop waiting for Ctrl+C
        try:
            while 1:
                pass
        except KeyboardInterrupt:
            return
