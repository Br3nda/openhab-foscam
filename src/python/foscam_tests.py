import os
import unittest
import json
import ConfigParser
from pprint import pprint

# foscam-python-library must be in sys.path
import foscam
import foscam_log

# see camtest.cfg.template for an example test configuration file
config = ConfigParser.SafeConfigParser()
config_filepath = os.path.join(os.path.dirname(__file__), 'camtest.cfg')

if os.path.exists(config_filepath):
    config.read([config_filepath])

config_defaults = config.defaults()

CAM_HOST = config_defaults.get('host')
CAM_PORT = config_defaults.get('port') or 88
CAM_USER = config_defaults.get('user')
CAM_PASS = config_defaults.get('pass')


class FoscamLogTestDevice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not CAM_HOST:
            raise Exception("Must configure hostname in camtest.cfg")
        cls.camera = foscam.FoscamCamera(CAM_HOST, CAM_PORT, CAM_USER, CAM_PASS)

    def setUp(self):
        self.log = foscam_log.FoscamLog(self.camera)

    def test_get_log_start_time(self):
        print self.log.get_log_start_time()

    def test_log_record_stream(self):
        for i, record in enumerate(self.log.get_log_records()):
            print i, record

    def test_log_record_stream_filter(self):
        print filter(lambda r: r[3] == 'UserLogin', self.log.get_log_records())[0]


class FoscamLogTest(unittest.TestCase):
    def setUp(self):
        # No camera is required for these tests
        self.log = foscam_log.FoscamLog(None)

    def test_log_parsing(self):
        response = """
        [
            0,
            {
                "curCnt": "10",
                "log0": "1434737211%2Broot%2B16777343%2B1",
                "log1": "1434736643%2Broot%2B16777343%2B1",
                "log2": "1434732193%2Broot%2B16777343%2B1",
                "log3": "1434731832%2Broot%2B16777343%2B1",
                "log4": "1434731813%2Broot%2B16777343%2B1",
                "log5": "1434731464%2Broot%2B16777343%2B1",
                "log6": "1434731408%2Broot%2B16777343%2B1",
                "log7": "1434731384%2Broot%2B16777343%2B1",
                "log8": "1434730572%2Broot%2B16777343%2B1",
                "log9": "1434727949%2Broot%2B16777343%2B1",
                "totalCnt": "618"
            }
        ]"""
        json_response = json.loads(response)
        pprint(self.log._decode_log_records(json_response))


if __name__ == '__main__':
    unittest.main()


