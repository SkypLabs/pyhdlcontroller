from yahdlc import *
from threading import Thread, Event, Lock
from time import sleep

class HDLController:
	"""
	An HDLC controller based on python4yahdlc.
	"""

	MAX_SEQ_NO = 8

	def __init__(self, read_func, write_func, window=3):
		if not hasattr(read_func, '__call__'):
			raise TypeError('The read function is not a callable object')
		if not hasattr(write_func, '__call__'):
			raise TypeError('The write function is not a callable object')

		self.read = read_func
		self.write = write_func

		self.window = window
		self.senders = list()
		self.send_lock = Lock()
		self.new_seq_no = 0

		self.receiver = self.Receiver(self.read, self.write, self.send_lock, self.senders)

	def start(self):
		"""
		Start HDLC controller's threads.
		"""

		self.receiver.start()

	def stop(self):
		"""
		Stop HDLC controller's threads.
		"""

		self.receiver.join()

		for s in self.senders:
			s.join()

	def send(self, data):
		"""
		Send a new data frame.

		This method will block until a new room is
		available for a new sender. This limit is
		determined by the size of the window.
		"""

		while len(self.senders) >= self.window:
			pass

		self.senders.insert(self.new_seq_no, self.Sender(self.write, self.send_lock, data, self.new_seq_no))
		self.senders[self.new_seq_no].start()
		self.new_seq_no = (self.new_seq_no + 1) % HDLController.MAX_SEQ_NO

	class Sender(Thread):
		"""
		Thread used to send HDLC frames.
		"""

		def __init__(self, write_func, send_lock, data, seq_no):
			super().__init__()
			self.write = write_func
			self.send_lock = send_lock
			self.data = data
			self.seq_no = seq_no
			self.ack = Event()

		def run(self):
			with self.send_lock:
				self.__send_data()

			while not self.ack.isSet():
				pass

		def join(self, timeout=None):
			"""
			Stop the current thread.
			"""

			self.ack.set()
			super().join(timeout)

		def ack_received(self):
			"""
			Inform the sender that the ack frame
			has been received which has the
			consequence of stopping the current
			thread.
			"""

			self.join()

		def nack_received(self):
			"""
			Inform the sender that a nack frame
			has been received which has the
			consequence of resending the data
			frame.
			"""

			with self.send_lock:
				self.__send_data()

		def __send_data(self):
			"""
			Send a new data frame.
			"""

			self.write(frame_data(self.data, FRAME_DATA, self.seq_no))

	class Receiver(Thread):
		"""
		Thread used to receive HDLC frames.
		"""

		def __init__(self, read_func, write_func, send_lock, senders_list):
			super().__init__()
			self.read = read_func
			self.write = write_func
			self.send_lock = send_lock
			self.senders = senders_list
			self.stop_receiver = Event()

		def run(self):
			while not self.stop_receiver.isSet():
				try:
					data, type, seq_no = get_data(self.read())

					if type == FRAME_DATA:
						with self.send_lock:
							self.__send_ack((seq_no + 1) % HDLController.MAX_SEQ_NO)
					elif type == FRAME_ACK:
						seq_no_sent = (seq_no - 1) % HDLController.MAX_SEQ_NO
						self.senders[seq_no_sent].ack_received()
						del self.senders[seq_no_sent]
					elif type == FRAME_NACK:
						self.senders[seq_no].nack_received()
					else:
						raise TypeError('Bad frame type received')
				except MessageError:
					# No HDLC frame detected
					pass
				except IndexError:
					# Drop bad (n)ack
					pass
				except FCSError:
					with self.send_lock:
						self.__send_nack(seq_no)
				finally:
					# 200 µs
					sleep(200 / 1000000.0)

		def join(self, timeout=None):
			"""
			Stop the current thread.
			"""

			self.stop_receiver.set()
			super().join(timeout)

		def __send_ack(self, seq_no):
			"""
			Send a new ack frame.
			"""

			self.write(frame_data('', FRAME_ACK, seq_no))

		def __send_nack(self, seq_no):
			"""
			Send a new nack frame.
			"""

			self.write(frame_data('', FRAME_NACK, seq_no))

if __name__ == '__main__':
	import serial
	from sys import stdout, stderr

	# Serial port configuration
	ser = serial.Serial()
	ser.port = '/dev/pts/6'
	ser.baudrate = 9600
	ser.timeout = 0

	stdout.write('[*] Connection ...\n')

	try:
		ser.open()
	except serial.serialutil.SerialException as e:
		stderr.write('[x] Serial connection problem : {0}\n'.format(e))
		exit(1)

	def read_uart():
		return ser.read(ser.inWaiting())

	try:
		hdlc_c = HDLController(read_uart, ser.write)
		hdlc_c.start()
		while True: pass
	except KeyboardInterrupt:
		stdout.write('[*] Bye !\n')
		hdlc_c.stop()
		ser.close()
