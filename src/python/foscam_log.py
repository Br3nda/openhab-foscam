from urllib import unquote
import datetime
import socket
import struct


class FoscamLog(object):
    """Log records are returned as a list. Each log record is a list
        with the following values.

        * Log timestamp as a datetime
        * User ID
        * Host IP address
        * Record type
        * Raw log record
    """

    LOG_RECORD_TYPES = {
        '0': "SystemPowerOn",
        '1': "DetectMotionAlarm",
        '3': "UserLogin",
        '4': "UserLogout",
        '5': "UserOffline",
    }

    def __init__(self, camera):
        self._camera = camera

    @staticmethod
    def _decode_log_record(r):
        record = unquote(r).split('+')
        record.append(r)
        record[0] = datetime.datetime.utcfromtimestamp(int(record[0]))
        record[2] = socket.inet_ntoa(struct.pack("<I", int(record[2])))
        record[3] = FoscamLog.LOG_RECORD_TYPES.get(record[3], str(record[3]))
        return record

    @staticmethod
    def _decode_log_records(response):
        payload = response[1]
        return [FoscamLog._decode_log_record(payload[key])
                for key in sorted(payload) if key.startswith("log") and payload[key]]

    def get_log_records(self):
        offset = 0
        response = self._camera.get_log(offset)
        payload = response[1]
        total_count = int(payload["totalCnt"])
        while True:
            for key in sorted(payload):
                if key.startswith("log"):
                    record = payload[key]
                    if record is not None:
                        yield self._decode_log_record(record)
            offset += 10
            if offset >= total_count:
                break
            response = self._camera.get_log(offset)
            payload = response[1]

    def get_log_start_time(self):
        response = self._camera.get_log(0)
        total_count = int(response[1]["totalCnt"])
        if total_count > 10:
            response = self._camera.get_log(total_count-10)
        return self._decode_log_records(response)[-1][0]


