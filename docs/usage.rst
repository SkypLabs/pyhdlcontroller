=====
Usage
=====

To create a new HDLC controller instance, you need to call the
``HDLController`` class with two parameters:

::

    hdlc_c = HDLController(read_func, write_func)

The first parameter is a function used to read from the serial bus while
the second parameter is a function used to write on it. For example, using
the ``pyserial`` module:

::

    ser = serial.Serial('/dev/ttyACM0')

    def read_serial():
        return ser.read(ser.in_waiting)

    hdlc_c = HDLController(read_serial, ser.write)

To start the reception thread:

::

    hdlc_c.start()

To send a new data frame:

::

    hdlc_c.send('Hello world!')

And to get the next received data frame available in the ``HDLController``
internal queue:

::

    data = hdlc_c.get_data()

The ``get_data()`` method will block until a new data frame is available.

Finally, to stop all the ``HDLController`` threads:

::

    hdlc_c.stop()
