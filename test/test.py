import unittest
from yahdlc import *
from hdlcontroller import HDLController
from time import sleep

class TestYahdlc(unittest.TestCase):
	def test_without_parameters(self):
		with self.assertRaises(TypeError):
			hdlc_c = HDLController()

	def test_with_only_one_parameter(self):
		def read_func():
			pass

		with self.assertRaises(TypeError):
			hdlc_c = HDLController(read_func)

	def test_bad_read_function(self):
		read_func = 'not a function'

		def write_func():
			pass

		with self.assertRaises(TypeError):
			hdlc_c = HDLController(read_func, write_func)

	def test_bad_write_function(self):
		write_func = 'not a function'

		def read_func():
			pass

		with self.assertRaises(TypeError):
			hdlc_c = HDLController(read_func, write_func)

	def test_stop_before_start(self):
		def read_func():
			pass

		def write_func():
			pass

		hdlc_c = HDLController(read_func, write_func)
		hdlc_c.stop()

	def test_send_one_frame(self):
		def read_func():
			pass

		def write_func(data):
			write_func.data = data

		write_func.data = None

		hdlc_c = HDLController(read_func, write_func)
		hdlc_c.send('test')
		while write_func.data == None: pass
		self.assertEqual(write_func.data, frame_data('test', FRAME_DATA, 0))
		self.assertEqual(hdlc_c.get_senders_number(), 1)
		hdlc_c.stop()

	def test_send_three_frames(self):
		def read_func():
			pass

		def write_func(data):
			write_func.data = data

		write_func.data = None

		hdlc_c = HDLController(read_func, write_func)
		hdlc_c.send('test1')
		while write_func.data == None: pass
		self.assertEqual(write_func.data, frame_data('test1', FRAME_DATA, 0))
		self.assertEqual(hdlc_c.get_senders_number(), 1)
		write_func.data = None
		hdlc_c.send('test2')
		while write_func.data == None: pass
		self.assertEqual(write_func.data, frame_data('test2', FRAME_DATA, 1))
		self.assertEqual(hdlc_c.get_senders_number(), 2)
		write_func.data = None
		hdlc_c.send('test3')
		while write_func.data == None: pass
		self.assertEqual(write_func.data, frame_data('test3', FRAME_DATA, 2))
		self.assertEqual(hdlc_c.get_senders_number(), 3)
		hdlc_c.stop()

	def test_send_one_frame_and_wait_timeout(self):
		def read_func():
			pass

		def write_func(data):
			write_func.data = data

		write_func.data = None

		hdlc_c = HDLController(read_func, write_func)
		hdlc_c.send('test')
		while write_func.data == None: pass
		self.assertEqual(write_func.data, frame_data('test', FRAME_DATA, 0))
		self.assertEqual(hdlc_c.get_senders_number(), 1)
		write_func.data = None
		while write_func.data == None: pass
		self.assertEqual(write_func.data, frame_data('test', FRAME_DATA, 0))
		self.assertEqual(hdlc_c.get_senders_number(), 1)
		hdlc_c.stop()

	def test_send_three_frames_and_wait_timeout(self):
		def read_func():
			pass

		def write_func(data):
			write_func.data = data

		write_func.data = None

		hdlc_c = HDLController(read_func, write_func, sending_timeout=5)
		hdlc_c.send('test1')
		while write_func.data == None: pass
		self.assertEqual(write_func.data, frame_data('test1', FRAME_DATA, 0))
		self.assertEqual(hdlc_c.get_senders_number(), 1)
		write_func.data = None
		sleep(1)
		hdlc_c.send('test2')
		while write_func.data == None: pass
		self.assertEqual(write_func.data, frame_data('test2', FRAME_DATA, 1))
		self.assertEqual(hdlc_c.get_senders_number(), 2)
		write_func.data = None
		sleep(1)
		hdlc_c.send('test3')
		while write_func.data == None: pass
		self.assertEqual(write_func.data, frame_data('test3', FRAME_DATA, 2))
		self.assertEqual(hdlc_c.get_senders_number(), 3)
		write_func.data = None
		while write_func.data == None: pass
		self.assertEqual(write_func.data, frame_data('test1', FRAME_DATA, 0))
		self.assertEqual(hdlc_c.get_senders_number(), 3)
		write_func.data = None
		while write_func.data == None: pass
		self.assertEqual(write_func.data, frame_data('test2', FRAME_DATA, 1))
		self.assertEqual(hdlc_c.get_senders_number(), 3)
		write_func.data = None
		while write_func.data == None: pass
		self.assertEqual(write_func.data, frame_data('test3', FRAME_DATA, 2))
		self.assertEqual(hdlc_c.get_senders_number(), 3)
		hdlc_c.stop()

	def test_send_frame_and_receive_ack(self):
		def read_func():
			return frame_data('', FRAME_ACK, 1)

		def write_func(data):
			write_func.data = data

		write_func.data = None

		hdlc_c = HDLController(read_func, write_func)
		hdlc_c.send('test')
		while write_func.data == None: pass
		self.assertEqual(write_func.data, frame_data('test', FRAME_DATA, 0))
		self.assertEqual(hdlc_c.get_senders_number(), 1)
		hdlc_c.start()
		sleep(1)
		self.assertEqual(hdlc_c.get_senders_number(), 0)
		hdlc_c.stop()

	def test_send_frame_and_receive_bad_ack(self):
		def read_func():
			return frame_data('', FRAME_ACK, 4)

		def write_func(data):
			write_func.data = data

		write_func.data = None

		hdlc_c = HDLController(read_func, write_func)
		hdlc_c.send('test')
		while write_func.data == None: pass
		self.assertEqual(write_func.data, frame_data('test', FRAME_DATA, 0))
		self.assertEqual(hdlc_c.get_senders_number(), 1)
		hdlc_c.start()
		sleep(1)
		self.assertEqual(hdlc_c.get_senders_number(), 1)
		hdlc_c.stop()

	def test_send_frame_and_receive_nack(self):
		def read_func():
			return frame_data('', FRAME_NACK, 0)

		def write_func(data):
			write_func.data = data

		write_func.data = None

		hdlc_c = HDLController(read_func, write_func)
		hdlc_c.send('test')
		while write_func.data == None: pass
		self.assertEqual(write_func.data, frame_data('test', FRAME_DATA, 0))
		self.assertEqual(hdlc_c.get_senders_number(), 1)
		hdlc_c.start()
		sleep(1)
		self.assertEqual(hdlc_c.get_senders_number(), 1)
		hdlc_c.stop()

	def test_receive_one_frame(self):
		def read_func():
			return frame_data('test', FRAME_DATA, 0)

		def write_func(data):
			write_func.data = data

		write_func.data = None

		hdlc_c = HDLController(read_func, write_func)
		hdlc_c.start()
		self.assertEqual(hdlc_c.get_data(), b'test')
		self.assertEqual(write_func.data, frame_data('', FRAME_ACK, 1))
		hdlc_c.stop()

	def test_receive_three_frames(self):
		def read_func():
			data = frame_data('test' + str(read_func.i), FRAME_DATA, read_func.i)
			read_func.i += 1
			return data

		def write_func(data):
			pass

		read_func.i = 1

		hdlc_c = HDLController(read_func, write_func)
		hdlc_c.start()
		self.assertEqual(hdlc_c.get_data(), b'test1')
		self.assertEqual(hdlc_c.get_data(), b'test2')
		self.assertEqual(hdlc_c.get_data(), b'test3')
		hdlc_c.stop()

if __name__ == '__main__':
	unittest.main()
