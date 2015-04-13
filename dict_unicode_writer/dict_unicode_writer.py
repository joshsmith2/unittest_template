# coding: utf-8
# Written by Mark Tolonen, and edited by Josh Smith.
# Retreived 13 April 2015 from
# http://stackoverflow.com/questions/5838605/
# python-dictwriter-writing-utf-8-encoded-csv-files

import csv
import cStringIO
import codecs

class DictUnicodeWriter(object):

    def __init__(self, f, fieldnames, dialect=csv.excel,
                 encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.DictWriter(self.queue, fieldnames,
                                     dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def decode(self, value):
        """
        If value is a unicode string, return a decoded version. If not, don't.
        :param value: Value to decode (or not)
        """
        if str(value.__class__) == "<type 'unicode'>":
            return_val = value.encode("utf-8")
        else:
            return_val = value
        return return_val

    def writerow(self, D):

        self.writer.writerow({k:self.decode(v) for k,v in D.items()})
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for D in rows:
            self.writerow(D)

    def writeheader(self):
        self.writer.writeheader()
