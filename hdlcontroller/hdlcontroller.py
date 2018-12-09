#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from yahdlc import *
from threading import Thread, Event, Lock
from queue import Queue, Full
from time import sleep, time

class HDLController:
    """
    An HDLC controller based on python4yahdlc.
    """

    MAX_SEQ_NO = 8
    MIN_SENDING_TIMEOUT = 0.5

    def __init__(self, read_func, write_func, sending_timeout=2, window=3, frames_queue_size=0, fcs_nack=True):
        if not hasattr(read_func, '__call__'):
            raise TypeError('The read function parameter is not a callable object')
        if not hasattr(write_func, '__call__'):
            raise TypeError('The write function parameter is not a callable object')

        self.read = read_func
        self.write = write_func

        self.window = window
        self.fcs_nack = fcs_nack
        self.senders = dict()
        self.send_lock = Lock()
        self.new_seq_no = 0

        self.send_callback = None
        self.receive_callback = None

        self.set_sending_timeout(sending_timeout)

        self.receiver = None
        self.frames_received = Queue(maxsize=frames_queue_size)

    def start(self):
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

    def stop(self):
        """
        Stops HDLC controller's threads.
        """

        if self.receiver != None:
            self.receiver.join()

        for s in self.senders.values():
            s.join()

    def set_send_callback(self, callback):
        """
        Sets the send callback function.

        If the HDLC controller has already been started, the new
        callback function will be taken into account for the next
        data frames to be sent.
        """

        if not hasattr(callback, '__call__'):
            raise TypeError('The callback function parameter is not a callable object')

        self.send_callback = callback

    def set_receive_callback(self, callback):
        """
        Sets the receive callback function.

        This method has to be called before starting the
        HDLC controller.
        """

        if not hasattr(callback, '__call__'):
            raise TypeError('The callback function parameter is not a callable object')

        self.receive_callback = callback

    def set_sending_timeout(self, sending_timeout):
        """
        Sets the sending timeout.
        """

        if sending_timeout >= HDLController.MIN_SENDING_TIMEOUT:
            self.sending_timeout = sending_timeout

    def get_senders_number(self):
        """
        Returns the number of active senders.
        """

        return len(self.senders)

    def send(self, data):
        """
        Sends a new data frame.

        This method will block until a new room is available for
        a new sender. This limit is determined by the size of the window.
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
        self.new_seq_no = (self.new_seq_no + 1) % HDLController.MAX_SEQ_NO

    def get_data(self):
        """
        Gets the next frame received.

        This method will block until a new data frame is available.
        """

        return self.frames_received.get()

    class Sender(Thread):
        """
        Thread used to send HDLC frames.
        """

        def __init__(self, write_func, send_lock, data, seq_no, timeout=2, callback=None):
            super().__init__()
            self.write = write_func
            self.send_lock = send_lock
            self.data = data
            self.seq_no = seq_no
            self.timeout = timeout
            self.callback = callback

            self.stop_sender = Event()
            self.stop_timeout = Event()
            self.next_timeout = 0

        def run(self):
            while not self.stop_sender.isSet():
                self.stop_timeout.wait(max(0, self.next_timeout - time()))
                self.stop_timeout.clear()

                if not self.stop_sender.isSet():
                    self.next_timeout = time() + self.timeout

                    with self.send_lock:
                        self.__send_data()

        def join(self, timeout=None):
            """
            Stops the current thread.
            """

            self.stop_sender.set()
            self.stop_timeout.set()
            super().join(timeout)

        def ack_received(self):
            """
            Informs the sender that the related ACK frame has been received.
            As a consequence, the current thread is being stopped.
            """

            self.join()

        def nack_received(self):
            """
            Informs the sender that an NACK frame has been received.
            As a consequence, the data frame is being resent.
            """

            self.stop_timeout.set()

        def __send_data(self):
            """
            Sends a new data frame.
            """

            if self.callback != None:
                self.callback(self.data)

            self.write(frame_data(self.data, FRAME_DATA, self.seq_no))

    class Receiver(Thread):
        """
        Thread used to receive HDLC frames.
        """

        def __init__(self, read_func, write_func, send_lock, senders_list, frames_received, callback=None, fcs_nack=True):
            super().__init__()
            self.read = read_func
            self.write = write_func
            self.send_lock = send_lock
            self.senders = senders_list
            self.frames_received = frames_received
            self.callback = callback
            self.fcs_nack = fcs_nack

            self.stop_receiver = Event()

        def run(self):
            while not self.stop_receiver.isSet():
                try:
                    data, ftype, seq_no = get_data(self.read())

                    if ftype == FRAME_DATA:
                        with self.send_lock:
                            if self.callback != None:
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
                        raise TypeError('Bad frame type received')
                except MessageError:
                    # No HDLC frame detected.
                    pass
                except KeyError:
                    # Drops bad (N)ACKs.
                    pass
                except Full:
                    # Drops new data frames when the receive queue
                    # is full.
                    pass
                except FCSError as e:
                    # Sends back an NACK if a corrupted frame is received
                    # and if the FCS NACK option is enabled.
                    if self.fcs_nack:
                        with self.send_lock:
                            self.__send_nack(e.args[0])
                except TypeError:
                    # Generally, raised when an HDLC frame with a bad frame
                    # type is received.
                    pass
                finally:
                    # 200 µs.
                    sleep(200 / 1000000.0)

        def join(self, timeout=None):
            """
            Stops the current thread.
            """

            self.stop_receiver.set()
            super().join(timeout)

        def __send_ack(self, seq_no):
            """
            Sends a new ACK frame.
            """

            self.write(frame_data('', FRAME_ACK, seq_no))

        def __send_nack(self, seq_no):
            """
            Sends a new NACK frame.
            """

            self.write(frame_data('', FRAME_NACK, seq_no))
