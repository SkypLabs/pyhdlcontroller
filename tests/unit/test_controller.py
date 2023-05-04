"""
Unit tests for the HDLC controller.
"""

import unittest
from time import sleep

from yahdlc import FRAME_ACK, FRAME_DATA, FRAME_NACK, frame_data

from hdlcontroller.hdlcontroller import HDLController, Timeout


class TestHDLCController(unittest.TestCase):
    """
    Tests the HDLC Controller.
    """

    def test_without_parameters(self):
        """
        Instantiates a new HDLC controller without parameters.
        """

        with self.assertRaises(TypeError):
            _ = HDLController()  # type: ignore

    def test_with_only_one_parameter(self):
        """
        Instantiates a new HDLC controller without write function.
        """

        def read_func() -> bytes:
            return b"test"

        with self.assertRaises(TypeError):
            _ = HDLController(read_func)  # type: ignore

    def test_bad_read_function(self):
        """
        Instantiates a new HDLC controller with an invalid read function.
        """

        read_func = "not a function"

        def write_func(_: bytes) -> None:
            pass

        with self.assertRaises(TypeError):
            _ = HDLController(read_func, write_func)  # type: ignore

    def test_bad_write_function(self):
        """
        Instantiates a new HDLC controller with an invalid write function.
        """

        write_func = "not a function"

        def read_func() -> bytes:
            return b"test"

        with self.assertRaises(TypeError):
            _ = HDLController(read_func, write_func)  # type: ignore

    def test_stop_before_start(self):
        """
        Stops the HDLC controller before it even started.
        """

        def read_func() -> bytes:
            return b"test"

        def write_func(_: bytes) -> None:
            pass

        hdlc_c = HDLController(read_func, write_func)
        hdlc_c.stop()

    def test_send_one_frame(self):
        """
        Tests the HDLC controller by sending one frame.
        """

        def read_func() -> bytes:
            return b"test"

        def write_func(data: bytes) -> None:
            write_func.data = data

        write_func.data = None

        hdlc_c = HDLController(read_func, write_func)

        hdlc_c.send(b"test")
        while write_func.data is None:
            pass
        self.assertEqual(write_func.data, frame_data("test", FRAME_DATA, 0))
        self.assertEqual(hdlc_c.get_senders_number(), 1)

        hdlc_c.stop()

    def test_send_three_frames(self):
        """
        Tests the HDLC controller by sending three frame.
        """

        def read_func() -> bytes:
            return b"test"

        def write_func(data: bytes) -> None:
            write_func.data = data

        hdlc_c = HDLController(read_func, write_func)

        write_func.data = None
        hdlc_c.send(b"test_1")
        while write_func.data is None:
            pass
        self.assertEqual(write_func.data, frame_data("test_1", FRAME_DATA, 0))
        self.assertEqual(hdlc_c.get_senders_number(), 1)

        write_func.data = None
        hdlc_c.send(b"test2")
        while write_func.data is None:
            pass
        self.assertEqual(write_func.data, frame_data("test2", FRAME_DATA, 1))
        self.assertEqual(hdlc_c.get_senders_number(), 2)

        write_func.data = None
        hdlc_c.send(b"test3")
        while write_func.data is None:
            pass
        self.assertEqual(write_func.data, frame_data("test3", FRAME_DATA, 2))
        self.assertEqual(hdlc_c.get_senders_number(), 3)

        hdlc_c.stop()

    def test_send_one_frame_and_wait_timeout(self):
        """
        Tests the timeout while sending one frame.
        """

        def read_func() -> bytes:
            return b"test"

        def write_func(data: bytes) -> None:
            write_func.data = data

        hdlc_c = HDLController(read_func, write_func)

        write_func.data = None
        hdlc_c.send(b"test")
        while write_func.data is None:
            pass
        self.assertEqual(write_func.data, frame_data("test", FRAME_DATA, 0))
        self.assertEqual(hdlc_c.get_senders_number(), 1)

        write_func.data = None
        while write_func.data is None:
            pass
        self.assertEqual(write_func.data, frame_data("test", FRAME_DATA, 0))
        self.assertEqual(hdlc_c.get_senders_number(), 1)

        hdlc_c.stop()

    def test_send_three_frames_and_wait_timeout(self):
        """
        Tests the timeout while sending three frames.
        """

        def read_func() -> bytes:
            return b"test"

        def write_func(data: bytes) -> None:
            write_func.data = data

        hdlc_c = HDLController(read_func, write_func, sending_timeout=Timeout(5.0))

        write_func.data = None
        hdlc_c.send(b"test_1")
        while write_func.data is None:
            pass
        self.assertEqual(write_func.data, frame_data("test_1", FRAME_DATA, 0))
        self.assertEqual(hdlc_c.get_senders_number(), 1)

        sleep(1)

        write_func.data = None
        hdlc_c.send(b"test_2")
        while write_func.data is None:
            pass
        self.assertEqual(write_func.data, frame_data("test_2", FRAME_DATA, 1))
        self.assertEqual(hdlc_c.get_senders_number(), 2)

        sleep(1)

        write_func.data = None
        hdlc_c.send(b"test_3")
        while write_func.data is None:
            pass
        self.assertEqual(write_func.data, frame_data("test_3", FRAME_DATA, 2))
        self.assertEqual(hdlc_c.get_senders_number(), 3)

        write_func.data = None
        while write_func.data is None:
            pass
        self.assertEqual(write_func.data, frame_data("test_1", FRAME_DATA, 0))
        self.assertEqual(hdlc_c.get_senders_number(), 3)

        write_func.data = None
        while write_func.data is None:
            pass
        self.assertEqual(write_func.data, frame_data("test_2", FRAME_DATA, 1))
        self.assertEqual(hdlc_c.get_senders_number(), 3)

        write_func.data = None
        while write_func.data is None:
            pass
        self.assertEqual(write_func.data, frame_data("test_3", FRAME_DATA, 2))
        self.assertEqual(hdlc_c.get_senders_number(), 3)

        hdlc_c.stop()

    def test_send_frame_and_receive_ack(self):
        """
        Tests the reception of an ACK frame after having sent a DATA one.
        """

        def read_func() -> bytes:
            return frame_data("", FRAME_ACK, 1)

        def write_func(data: bytes) -> None:
            write_func.data = data

        hdlc_c = HDLController(read_func, write_func)

        write_func.data = None
        hdlc_c.send(b"test")
        while write_func.data is None:
            pass
        self.assertEqual(write_func.data, frame_data("test", FRAME_DATA, 0))
        self.assertEqual(hdlc_c.get_senders_number(), 1)

        hdlc_c.start()
        sleep(1)
        self.assertEqual(hdlc_c.get_senders_number(), 0)

        hdlc_c.stop()

    def test_send_frame_and_receive_bad_ack(self):
        """
        Tests the reception of an invalid ACK frame after having sent a DATA
        one.
        """

        def read_func() -> bytes:
            return frame_data("", FRAME_ACK, 4)

        def write_func(data: bytes) -> None:
            write_func.data = data

        hdlc_c = HDLController(read_func, write_func)

        write_func.data = None
        hdlc_c.send(b"test")
        while write_func.data is None:
            pass
        self.assertEqual(write_func.data, frame_data("test", FRAME_DATA, 0))
        self.assertEqual(hdlc_c.get_senders_number(), 1)

        hdlc_c.start()
        sleep(1)
        self.assertEqual(hdlc_c.get_senders_number(), 1)

        hdlc_c.stop()

    def test_send_frame_and_receive_nack(self):
        """
        Tests the reception of an NACK frame after having sent a DATA one.
        """

        def read_func() -> bytes:
            return frame_data("", FRAME_NACK, 0)

        def write_func(data: bytes) -> None:
            write_func.data = data

        hdlc_c = HDLController(read_func, write_func)

        write_func.data = None
        hdlc_c.send(b"test")
        while write_func.data is None:
            pass
        self.assertEqual(write_func.data, frame_data("test", FRAME_DATA, 0))
        self.assertEqual(hdlc_c.get_senders_number(), 1)

        hdlc_c.start()
        sleep(1)
        self.assertEqual(hdlc_c.get_senders_number(), 1)

        hdlc_c.stop()

    def test_receive_one_frame(self):
        """
        Tests the reception of one DATA frame.
        """

        def read_func() -> bytes:
            return frame_data("test", FRAME_DATA, 0)

        def write_func(data: bytes) -> None:
            write_func.data = data

        hdlc_c = HDLController(read_func, write_func)

        write_func.data = None
        hdlc_c.start()
        self.assertEqual(hdlc_c.get_data(), b"test")
        self.assertEqual(write_func.data, frame_data("", FRAME_ACK, 1))

        hdlc_c.stop()

    def test_receive_three_frames(self):
        """
        Tests the reception of three DATA frames.
        """

        def read_func() -> bytes:
            data = frame_data("test_" + str(read_func.i), FRAME_DATA, read_func.i)
            read_func.i += 1
            return data

        def write_func(_: bytes) -> None:
            pass

        hdlc_c = HDLController(read_func, write_func)

        read_func.i = 1
        hdlc_c.start()
        self.assertEqual(hdlc_c.get_data(), b"test_1")
        self.assertEqual(hdlc_c.get_data(), b"test_2")
        self.assertEqual(hdlc_c.get_data(), b"test_3")

        hdlc_c.stop()

    def test_receive_one_corrupted_frame_and_send_back_nack(self):
        """
        Tests the reception of a corrupted DATA frame and the emission of an
        NACK as expected.
        """

        def read_func() -> bytes:
            data = bytearray(frame_data("test", FRAME_DATA, 0))
            data[7] ^= 0x01
            return bytes(data)

        def write_func(data: bytes) -> None:
            write_func.data = data

        hdlc_c = HDLController(read_func, write_func)

        write_func.data = None
        hdlc_c.start()
        while write_func.data is None:
            pass
        self.assertEqual(write_func.data, frame_data("", FRAME_NACK, 0))

        hdlc_c.stop()

    def test_receive_one_corrupted_frame_and_do_not_send_back_nack(self):
        """
        Tests the reception of a corrupted DATA frame and that the controller
        does not send back an NACK as the option has been turned off.
        """

        def read_func() -> bytes:
            data = bytearray(frame_data("test", FRAME_DATA, 0))
            data[7] ^= 0x01
            return bytes(data)

        def write_func(data: bytes) -> None:
            write_func.data = data

        hdlc_c = HDLController(read_func, write_func, fcs_nack=False)

        write_func.data = None
        hdlc_c.start()
        sleep(1)
        self.assertEqual(write_func.data, None)

        hdlc_c.stop()
