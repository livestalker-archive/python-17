import os
import unittest
import gzip
from struct import unpack

import pb
import deviceapps_pb2 as pypb2

MAGIC = 0xFFFFFFFF
DEVICE_APPS_TYPE = 1
TEST_FILE = "test.pb.gz"
HEADER_SIZE = 8


class TestPB(unittest.TestCase):
    deviceapps = [
        {"device": {"type": "idfa", "id": "e7e1a50c0ec2747ca56cd9e1558c0d7c"},
         "lat": 67.7835424444, "lon": -22.8044005471, "apps": [1, 2, 3, 4]},
        {"device": {"type": "gaid", "id": "e7e1a50c0ec2747ca56cd9e1558c0d7d"}, "lat": 42, "lon": -42, "apps": [1, 2]},
        {"device": {"type": "gaid", "id": "e7e1a50c0ec2747ca56cd9e1558c0d7d"}, "lat": 42, "lon": -42, "apps": []},
        {"device": {"type": "gaid", "id": "e7e1a50c0ec2747ca56cd9e1558c0d7d"}, "apps": [1]},
    ]

    def tearDown(self):
        os.remove(TEST_FILE)

    def test_write(self):
        bytes_written = pb.deviceapps_xwrite_pb(self.deviceapps, TEST_FILE)
        self.assertTrue(bytes_written > 0)
        un_size = self.get_uncompressed_size(TEST_FILE)
        self.assertEquals(bytes_written, un_size)

        with gzip.open(TEST_FILE, 'rb') as fd:
            for el in self.deviceapps:
                header = fd.read(HEADER_SIZE)
                magic, dev_apps_type, data_len = unpack('<IHH', header)
                self.assertEquals(magic, MAGIC)
                self.assertEquals(dev_apps_type, DEVICE_APPS_TYPE)

                data = fd.read(data_len)
                da = pypb2.DeviceApps()
                da.ParseFromString(data)
                if da.HasField('device'):
                    if da.device.HasField('type'):
                        self.assertEqual(da.device.type, el['device']['type'])
                    if da.device.HasField('id'):
                        self.assertEqual(da.device.id, el['device']['id'])
                self.assertEqual(da.apps, el['apps'])
                if da.HasField('lat'):
                    self.assertAlmostEqual(da.lat, el['lat'], places=5)
                if da.HasField('lon'):
                    self.assertAlmostEqual(da.lon, el['lon'], places=5)

    @unittest.skip("Optional problem")
    def test_read(self):
        pb.deviceapps_xwrite_pb(self.deviceapps, TEST_FILE)
        for i, d in enumerate(pb.deviceapps_xread_pb(TEST_FILE)):
            self.assertEqual(d, self.deviceapps[i])

    @staticmethod
    def get_uncompressed_size(file):
        fileobj = open(file, 'r')
        fileobj.seek(-8, 2)
        crc32 = gzip.read32(fileobj)
        isize = gzip.read32(fileobj)
        fileobj.close()
        return isize
