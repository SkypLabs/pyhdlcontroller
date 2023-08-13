from queue import Full, Queue
from threading import Event, Lock, Thread
from time import sleep, time
from typing import Callable, Dict, NewType, Union

from yahdlc import (
    FRAME_ACK,
    FRAME_DATA,
    FRAME_NACK,
    FCSError,
    MessageError,
    frame_data,
    get_data,
)

SequenceNumber = NewType("SequenceNumber", int)
Timeout = NewType("Timeout", float)

ReadFunction = Callable[[], bytes]
WriteFunction = Callable[[bytes], Union[int, None]]

Callback = Callable[[bytes], None]


class HDLController:
    """
    An HDLC controller based on python4yahdlc.
    """

    MAX_SEQ_NO = 8
    MIN_SENDING_TIMEOUT = 0.5

    def __init__(
        self,
        read_func: ReadFunction,
        write_func: WriteFunction,
        sending_timeout: Timeout = Timeout(2.0),
        window: int = 3,
        frames_queue_size: int = 0,
        fcs_nack: bool = True,
    ):
        if not callable(read_func):
            raise TypeError("'read_func' is not callable")

        if not callable(write_func):
            raise TypeError("'write_func' is not callable")

        self.read: ReadFunction = read_func
        self.write: WriteFunction = write_func

        self.window: int = window
        self.fcs_nack: bool = fcs_nack
        self.senders: Dict[SequenceNumber, HDLController.Sender] = {}
        self.send_lock: Lock = Lock()
        self.new_seq_no: SequenceNumber = SequenceNumber(0)

        self.send_callback: Union[Callback, None] = None
        self.receive_callback: Union[Callback, None] = None

        self.set_sending_timeout(sending_timeout)

        self.receiver: Union[HDLController.Receiver, None] = None
        self.frames_received: Queue = Queue(maxsize=frames_queue_size)

    def start(self) -> None:
        """
        Starts HDLC controller's threads.
        """

        self.receiver = self.Receiver(
            self.read,
            self.write,
            self.send_lock,
            self.senders,
            self.frames_received,
            callback=self.receive_callback,
            fcs_nack=self.fcs_nack,
        )

        self.receiver.start()

    def stop(self) -> None:
        """
        Stops HDLC controller's threads.
        """

        if self.receiver is not None:
            self.receiver.join()

        for sender in self.senders.values():
            sender.join()

    def set_send_callback(self, callback: Callback) -> None:
        """
        Sets the send callback function.

        If the HDLC controller has already been started, the new callback
        function will be taken into account for the next data frames to be
        sent.
        """

        if not callable(callback):
            raise TypeError("'callback' is not callable")

        self.send_callback = callback

    def set_receive_callback(self, callback: Callback) -> None:
        """
        Sets the receive callback function.

        This method has to be called before starting the HDLC controller.
        """

        if not callable(callback):
            raise TypeError("'callback' is not callable")

        self.receive_callback = callback

    def set_sending_timeout(self, sending_timeout: Timeout) -> None:
        """
        Sets the sending timeout.
        """

        if sending_timeout >= HDLController.MIN_SENDING_TIMEOUT:
            self.sending_timeout = sending_timeout

    def get_senders_number(self) -> int:
        """
        Returns the number of active senders.
        """

        return len(self.senders)

    def send(self, data: bytes) -> None:
        """
        Sends a new data frame.

        This method will block until a new room is available for a new sender.
        This limit is determined by the size of the window.
        """

        while len(self.senders) >= self.window:
            pass

        self.senders[self.new_seq_no] = self.Sender(
            self.write,
            self.send_lock,
            data,
            self.new_seq_no,
            timeout=self.sending_timeout,
            callback=self.send_callback,
        )

        self.senders[self.new_seq_no].start()
        self.new_seq_no = SequenceNumber(
            (self.new_seq_no + 1) % HDLController.MAX_SEQ_NO
        )

    def get_data(self) -> bytes:
        """
        Gets the next frame received.

        This method will block until a new data frame is available.
        """

        return self.frames_received.get()

    class Sender(Thread):
        """
        Thread used to send HDLC frames.
        """

        def __init__(
            self,
            write_func: WriteFunction,
            send_lock: Lock,
            data: bytes,
            seq_no: SequenceNumber,
            timeout: Timeout = Timeout(2.0),
            callback: Union[Callback, None] = None,
        ):
            super().__init__()
            self.write: WriteFunction = write_func
            self.send_lock: Lock = send_lock
            self.data: bytes = data
            self.seq_no: SequenceNumber = seq_no
            self.timeout: Timeout = timeout
            self.callback: Union[Callback, None] = callback

            self.stop_sender: Event = Event()
            self.stop_timeout: Event = Event()
            self.next_timeout: Timeout = Timeout(0.0)

        def run(self) -> None:
            while not self.stop_sender.is_set():
                self.stop_timeout.wait(max(0, self.next_timeout - time()))
                self.stop_timeout.clear()

                if not self.stop_sender.is_set():
                    self.next_timeout = Timeout(time() + self.timeout)

                    with self.send_lock:
                        self.__send_data()

        def join(self, timeout: Union[Timeout, None] = None) -> None:
            """
            Stops the current thread.
            """

            self.stop_sender.set()
            self.stop_timeout.set()
            super().join(timeout)

        def ack_received(self) -> None:
            """
            Informs the sender that the related ACK frame has been received.
            As a consequence, the current thread is being stopped.
            """

            self.join()

        def nack_received(self) -> None:
            """
            Informs the sender that an NACK frame has been received. As a
            consequence, the data frame is being resent.
            """

            self.stop_timeout.set()

        def __send_data(self) -> None:
            """
            Sends a new data frame.
            """

            if self.callback is not None:
                self.callback(self.data)

            self.write(frame_data(self.data, FRAME_DATA, self.seq_no))

    class Receiver(Thread):
        """
        Thread used to receive HDLC frames.
        """

        def __init__(
            self,
            read_func: ReadFunction,
            write_func: WriteFunction,
            send_lock: Lock,
            senders_list: Dict[SequenceNumber, "HDLController.Sender"],
            frames_received: Queue,
            callback: Union[Callback, None] = None,
            fcs_nack: bool = True,
        ):
            super().__init__()
            self.read: ReadFunction = read_func
            self.write: WriteFunction = write_func
            self.send_lock: Lock = send_lock
            self.senders: Dict[SequenceNumber, "HDLController.Sender"] = senders_list
            self.frames_received: Queue = frames_received
            self.callback: Union[Callback, None] = callback
            self.fcs_nack: bool = fcs_nack

            self.stop_receiver: Event = Event()

        def run(self):
            while not self.stop_receiver.is_set():
                try:
                    data, ftype, seq_no = get_data(self.read())

                    if ftype == FRAME_DATA:
                        with self.send_lock:
                            if self.callback is not None:
                                self.callback(data)

                            self.frames_received.put_nowait(data)
                            self.__send_ack((seq_no + 1) % HDLController.MAX_SEQ_NO)
                    elif ftype == FRAME_ACK:
                        seq_no_sent = (seq_no - 1) % HDLController.MAX_SEQ_NO
                        self.senders[seq_no_sent].ack_received()
                        del self.senders[seq_no_sent]
                    elif ftype == FRAME_NACK:
                        self.senders[seq_no].nack_received()
                    else:
                        raise TypeError("Bad frame type received")
                except MessageError:
                    # No HDLC frame detected.
                    pass
                except KeyError:
                    # Drops bad (N)ACKs.
                    pass
                except Full:
                    # Drops new data frames when the receive queue is full.
                    pass
                except FCSError as err:
                    # Sends back an NACK if a corrupted frame is received and
                    # if the FCS NACK option is enabled.
                    if self.fcs_nack:
                        with self.send_lock:
                            self.__send_nack(err.args[0])
                except TypeError:
                    # Generally, raised when an HDLC frame with a bad frame
                    # type is received.
                    pass
                finally:
                    # 200 µs.
                    sleep(200 / 1000000.0)

        def join(self, timeout: Union[Timeout, None] = None):
            """
            Stops the current thread.
            """

            self.stop_receiver.set()
            super().join(timeout)

        def __send_ack(self, seq_no: SequenceNumber):
            """
            Sends a new ACK frame.
            """

            self.write(frame_data("", FRAME_ACK, seq_no))

        def __send_nack(self, seq_no: SequenceNumber):
            """
            Sends a new NACK frame.
            """

            self.write(frame_data("", FRAME_NACK, seq_no))
