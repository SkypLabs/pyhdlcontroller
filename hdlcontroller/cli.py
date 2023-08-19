"""
CLI module.
"""

from argparse import ArgumentParser
from sys import exit as sys_exit
from sys import stderr, stdout
from time import sleep

import serial

from hdlcontroller.hdlcontroller import HDLController


def get_arg_parser():
    """
    Returns the argument parser.
    """

    arg_parser = ArgumentParser(
        description="HDLC controller example",
        epilog="""
        Example: hdlc-tester -d /dev/ttyUSB0 -b 115200 -m 'Hello world!'
        """,
    )

    arg_parser.add_argument(
        "-b",
        "--baudrate",
        type=int,
        default="9600",
        help="serial baudrate value in bauds per second (default: 9600)",
    )

    arg_parser.add_argument(
        "-d",
        "--device",
        default="/dev/ttyACM0",
        help="serial device to use (default: /dev/ttyACM0)",
    )

    arg_parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default="1.0",
        help="""
        sending interval between two data frames in seconds (default: 1.0)
        """,
    )

    arg_parser.add_argument(
        "-m",
        "--message",
        default="test",
        help="test message to send (default: test)",
    )

    arg_parser.add_argument(
        "-N",
        "--no-fcs-nack",
        action="store_true",
        help="""
        do not send back an NACK when a corrupted frame is received
        (default: false)
        """,
    )

    arg_parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="""
        do not send anything, just display what is received (default: false)
        """,
    )

    arg_parser.add_argument(
        "-Q",
        "--queue-size",
        type=int,
        default="0",
        help="queue size for data frames received (default: 0)",
    )

    arg_parser.add_argument(
        "-t",
        "--serial-timeout",
        type=int,
        default="0",
        help="serial read timeout value in seconds (default: 0)",
    )

    arg_parser.add_argument(
        "-T",
        "--sending-timeout",
        type=float,
        default="2.0",
        help="HDLC sending timeout value in seconds (default: 2.0)",
    )

    arg_parser.add_argument(
        "-w",
        "--window",
        type=int,
        default="3",
        help="sending window (default: 3)",
    )

    arg_parser.set_defaults(
        quiet=False,
        no_fcs_nack=False,
    )

    return arg_parser


def main():
    """
    Entry point of the command-line tool.
    """

    args = vars(get_arg_parser().parse_args())

    # Serial port configuration
    ser = serial.Serial()
    ser.port = args["device"]
    ser.baudrate = args["baudrate"]
    ser.timeout = args["serial_timeout"]

    stdout.write("[*] Connection...\n")

    try:
        ser.open()
    except serial.SerialException as err:
        stderr.write("[x] Serial connection problem: {0}\n".format(err))
        sys_exit(1)

    def read_uart():
        return ser.read(ser.in_waiting)

    def send_callback(data):
        print("> {0}".format(data))

    def receive_callback(data):
        print("< {0}".format(data))

    try:
        hdlc_c = HDLController(
            read_uart,
            ser.write,
            window=args["window"],
            sending_timeout=args["sending_timeout"],
            frames_queue_size=args["queue_size"],
            fcs_nack=not (args["no_fcs_nack"]),
        )
        hdlc_c.set_send_callback(send_callback)
        hdlc_c.set_receive_callback(receive_callback)
        hdlc_c.start()

        while True:
            if not args["quiet"]:
                hdlc_c.send(args["message"])

            sleep(args["interval"])
    except KeyboardInterrupt:
        stdout.write("[*] Bye!\n")
    finally:
        if "hdlc_c" in locals():
            hdlc_c.stop()  # type: ignore

        ser.close()
