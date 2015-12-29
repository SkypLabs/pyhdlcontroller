from yahdlc import *
from threading import Thread
from queue import Queue, Empty
from time import sleep

class HDLController:
	max_seq_no = 8

	def __init__(self, read_func, write_func, window=3):
		self.window = window
		self.data_to_send = list()
		self.ack_to_send = Queue(self.window)
		self.send_seq_no = 0
		self.last_data_sent = 0

		if not hasattr(read_func, '__call__'):
			raise TypeError('The read function is not a callable object')
		if not hasattr(write_func, '__call__'):
			raise TypeError('The write function is not a callable object')

		self.read = read_func
		self.write = write_func

		t_sender = Thread(target=self.__sender)
		t_receiver = Thread(target=self.__receiver)

		t_sender.start()
		t_receiver.start()

	def send_data(self, data):
		# Block until a new room is available
		while self.data_to_send.count() >= self.window:
			pass

		self.data_to_send.insert(self.send_seq_no, (data, FRAME_DATA, self.send_seq_no))
		self.send_seq_no = (self.send_seq_no + 1) % HDLController.max_seq_no

	def __send_ack(self, seq_no):
		self.write(frame_data('', FRAME_ACK, seq_no))

	def __send_ack(self, type, seq_no):
		self.write(frame_data('', type, seq_no))

	def __send_nack(self, seq_no):
		self.write(frame_data('', FRAME_NACK, seq_no))

	def __sender(self):
		while True:
			# Ack to send ?
			try:
				for i in range(self.window):
					type, seq_no = self.ack_to_send.get_nowait()
					self.__send_ack(type, seq_no)
			except Empty:
				pass

			# Data to send ?
			try:
				data, type, seq_no = self.data_to_send[self.last_data_sent]
				self.write(frame_data(data, type, seq_no))
				self.last_data_sent = (self.last_sent + 1) % HDLController.max_seq_no
			except IndexError:
				pass

	def __receiver(self):
		while True:
			try:
				data, type, seq_no = get_data(self.read())

				if type == FRAME_DATA:
					# Send ACK
					self.ack_to_send.put((FRAME_ACK, (seq_no + 1) % HDLController.max_seq_no))
				elif type == FRAME_ACK:
					del self.data_to_send[seq_no]
				elif type == FRAME_NACK:
					pass
				else:
					raise TypeError('Bad frame type received')
			except MessageError:
				pass
			except IndexError:
				pass
			except FCSError:
				# Send NACK
				self.ack_to_send.put((FRAME_NACK, seq_no))
			finally:
				# 200 µs
				sleep(200 / 1000000.0)

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

	hdlc_c = HDLController(read_uart, ser.write)
