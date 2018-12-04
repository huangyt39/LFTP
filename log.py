
import time
import datetime

class Logger:
    """
    output: {time} - {prefix} {info}
    """

    def __init__(self, prefix):
        self.prefix = prefix

    def log(self, info):
        print('{} - {} / {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.prefix, info))

    @staticmethod
    def err(e):
        print('{} - Error: {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), e))

SenderLogger = Logger('Sender')
ReceiverLogger = Logger('Receiver')
ClientLogger = Logger('Client')
ServerLogger = Logger('Server')
FileLogger = Logger('File')
RwndLogger = Logger('Rwnd')
CwndLogger = Logger('Cwnd')
ThreadLogger = Logger('Thread')
SendStateLogger = Logger('SendState')
CongestionSateLogger = Logger('CongestionSate')
SSThreshLogger = Logger('SSThresh')
WriteLogger = Logger('WriteData')
SendSeqLogger = Logger('SendSeq')
RecvSeqLogger = Logger('RecvSeq')