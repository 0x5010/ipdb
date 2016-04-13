# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import time
from IpDB import IpDB


def test_search(cache=True):
    algorithm = "binary" if cache else "b-tree"

    print("initializing %s..." % algorithm)

    searcher = IpDB(cache)
    try:
        while True:
            line = raw_input("ipdbn>> ")
            line = line.strip()

            if line == "":
                print("[Error]: Invalid ip address.")
                continue

            if line == "quit":
                break

            if not searcher.is_ip(line):
                print("[Error]: Invalid ip address.")
                continue

            s_time = time.time() * 1000
            data = searcher.search(line)
            e_time = time.time() * 1000

            if isinstance(data, (tuple, list)):
                print("[Return]: %s in %f millseconds" % ("|".join(data), e_time - s_time))
            else:
                print("[Error]: ", data)
            if searcher.is_3g(line):
                print("[Return]: %s in %f millseconds" % ("is_3g", e_time - s_time))
            else:
                print("[Return]: %s in %f millseconds" % ("no_3g", e_time - s_time))

    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        print("[Info]: Thanks for your use, Bye.")
        searcher.close()

if __name__ == "__main__":
    test_search()
