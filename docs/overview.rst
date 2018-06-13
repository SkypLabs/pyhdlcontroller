========
Overview
========

The HDLC controller supports the following frames:

- DATA (I-frame_ with Poll bit)
- ACK (`S-frame Receive Ready`_ with Final bit)
- NACK (`S-frame Reject`_ with Final bit)

Each DATA frame must be positively or negatively acknowledged using respectively an ACK or NACK frame. The highest sequence number is 7. As a result, when sending a DATA frame, the expected acknowledgment sequence number is ``seq_no + 1 % MAX_SEQ_NO`` with ``MAX_SEQ_NO = 8``.

.. seqdiag::

    seqdiag {
      activation = None;
      default_note_color = lightblue;

      "A" ->> "B" [label = "DATA [Seq No = 1]", note = "The expected ACK frame's sequence number
      is 1 + 1 % MAX_SEQ_NO = 2"]
      "A" ->> "B" [label = "DATA [Seq No = 2]"]
      "A" <<- "B" [label = "ACK [Seq No = 2]", note = "ACK of the DATA frame's sequence number 1"]
      "A" <<- "B" [label = "ACK [Seq No = 3]", note = "ACK of the DATA frame's sequence number 2"]
    }

The number of DATA frames that can be sent before receiving the first acknowledgment is determined by the ``window`` parameter of :py:class:`HDLController <hdlcontroller.hdlcontroller.HDLController>`. Its default value is 3.

If the FCS_ field of a received frame is not valid, an NACK will be sent back with the same sequence number as the one of the corrupted frame to notify the sender about it:

.. seqdiag::

    seqdiag {
      activation = None;

      "A" ->> "B" [label = "DATA [Seq No = 1]"]
      "A" <<- "B" [label = "NACK [Seq No = 1]"]
      "A" ->> "B" [label = "DATA [Seq No = 1]"]
    }

For each DATA frame sent, a timer is started. If the timer ends before receiving any corresponding ACK and NACK frame, the DATA frame will be sent again:

.. seqdiag::

    seqdiag {
      activation = None;
      default_note_color = lightblue;

      "A" ->> "B" [label = "DATA [Seq No = 1]"]
      "A" <<- "B" [failed, note = "No ACK/NACK received before the end of
      the timer"]
      "A" ->> "B" [label = "DATA [Seq No = 1]"]
    }

The default timer value is 2 seconds and can be changed using the ``sending_timeout`` parameter of :py:class:`HDLController <hdlcontroller.hdlcontroller.HDLController>`.

.. _FCS: https://en.wikipedia.org/wiki/Frame_check_sequence
.. _I-frame: https://en.wikipedia.org/wiki/High-Level_Data_Link_Control#I-Frames_(user_data)
.. _S-frame Receive Ready: https://en.wikipedia.org/wiki/High-Level_Data_Link_Control#Receive_Ready_(RR)
.. _S-frame Reject: https://en.wikipedia.org/wiki/High-Level_Data_Link_Control#Reject_(REJ)
