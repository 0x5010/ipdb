# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

import struct
import io
import socket
import sys


TXT = "ipdb.txt"
DB = "ip2region.db"
_3GTXT = "3gips.txt"


# search return (country, area, province, city, isp)
class IpDB(object):
    __headerSip = []
    __headerPtr = []
    __f = None
    __cache = {}
    __3gips = set()

    def __init__(self, cache=True):
        if cache:
            self.init_cache(TXT)
            self.init_g3ips(_3GTXT)
            self.search = self.binary_cache_search
            self.close = self.cache_close
        else:
            self.init_db(DB)
            self.init_g3ips(_3GTXT)
            self.search = self.btree_db_search
            self.close = self.db_close

    def init_db(self, db_file):
        try:
            self.__f = io.open(db_file, "rb")
            # pass the super block
            self.__f.seek(8)
            # read the header block
            b = self.__f.read(4086)
            # parse the header block
            # sip = None
            # ptr = None
            for i in range(0, len(b)-1, 8):
                sip = self.get_long(b, i)
                ptr = self.get_long(b, i+4)
                if ptr == 0:
                    break
                self.__headerSip.append(sip)
                self.__headerPtr.append(ptr)

        except IOError as e:
            print("[Error]: ", e)
            sys.exit()

    def init_cache(self, txt_file):
        try:
            with io.open(txt_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    sip, eip, country, area, province, city, isp = line.split("|")
                    network = self.ip2long(sip)
                    self.__cache[network] = (country, area, province, city, isp)
                    self.__headerSip.append(network)
        except IOError as e:
            print("[Error]: ", e)
            sys.exit()

    def init_g3ips(self, _3gips_file):
        with io.open(_3gips_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                self.__3gips.add(line)

    def btree_db_search(self, ip):
        if not ip.isdigit():
            ip = self.ip2long(ip)

        header_len = len(self.__headerSip) - 1
        l, h, s_ptr, e_ptr = 0, header_len, 0, 0
        while l <= h:
            m = (l + h) // 2

            if ip == self.__headerSip[m]:
                if m > 0:
                    s_ptr = self.__headerPtr[m - 1]
                    e_ptr = self.__headerPtr[m]
                    break
                else:
                    s_ptr = self.__headerPtr[m]
                    e_ptr = self.__headerPtr[m + 1]
                    break

            if ip > self.__headerSip[m]:
                if m == header_len:
                    s_ptr = self.__headerPtr[m - 1]
                    e_ptr = self.__headerPtr[m]
                    break
                elif ip < self.__headerSip[m + 1]:
                    s_ptr = self.__headerPtr[m]
                    e_ptr = self.__headerPtr[m + 1]
                    break
                l = m + 1
            else:
                if m == 0:
                    s_ptr = self.__headerPtr[m]
                    e_ptr = self.__headerPtr[m + 1]
                    break
                elif ip > self.__headerSip[m - 1]:
                    s_ptr = self.__headerPtr[m - 1]
                    e_ptr = self.__headerPtr[m]
                    break

                h = m - 1
        if s_ptr == 0:
            return "N1"

        index_len = e_ptr - s_ptr
        self.__f.seek(s_ptr)
        b = self.__f.read(index_len + 12)

        l, h, mix_ptr = 0, index_len // 12, 0
        while l <= h:
            m = (l + h) // 2
            offset = m * 12

            if ip >= self.get_long(b, offset):
                if ip > self.get_long(b, offset+4):
                    l = m + 1
                else:
                    mix_ptr = self.get_long(b, offset+8)
                    break
            else:
                h = m - 1

        if mix_ptr == 0:
            return "N2"

        data_ptr = mix_ptr & 0x00FFFFFFL
        data_len = (mix_ptr >> 24) & 0xFF

        self.__f.seek(data_ptr)
        data = self.__f.read(data_len)
        return data[4:].split("|")

    def binary_cache_search(self, ip):
        if not ip.isdigit():
            ip = self.ip2long(ip)

        l, h = 0, len(self.__headerSip) - 1
        while l < h:
            m = (l + h) // 2
            x = self.__headerSip[m]
            if ip == x:
                h = m
                break
            elif ip > x:
                l = m + 1
            else:
                h = m - 1
        return self.__cache[self.__headerSip[h]]

    def is_3g(self, ip):
        return ip in self.__3gips

    @staticmethod
    def is_ip(ip):
        p = ip.split(".")

        if len(p) != 4:
            return False
        for pp in p:
            if not pp.isdigit():
                return False
            if int(pp) > 255:
                return False
        return True

    @staticmethod
    def get_long(b, offset):
        if len(b[offset:offset + 4]) == 4:
            return struct.unpack('I', b[offset:offset+4])[0]
        return 0

    @staticmethod
    def ip2long(ip):
        _ip = socket.inet_aton(ip)
        return struct.unpack("!L", _ip)[0]

    def db_close(self):
        self.__headerSip = None
        self.__headerPtr = None
        self.__f.close()
        self.__f = None

    def cache_close(self):
        self.__cache = None
        self.__headerSip = None
