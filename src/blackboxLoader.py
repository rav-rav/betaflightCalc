'''
Created on 18.08.2016

@author: rav
'''

import csv
import numpy as np
import os
import cPickle

DECODE_EXE = r"blackbox_decode.exe"
DECODED_LOGS_PATH = r"e:\!_Temp_!\SP3\blackbox tools"

class BlackboxLoader:
    data = None
    
    def picStore(self, data, filename):
        with open(filename, "wb") as out:
            cPickle.dump(data, out, -1)
            
    
    def picLoad(self, filename):
        with open(filename, "rb") as inp:
            return cPickle.load(inp)
    
    
    def readFile(self, filename, idx):
        csvName = "%s.%02i.csv" % (filename[:-4], idx)
        picName = csvName + ".pic"
        if not os.path.isfile(csvName):
            self.decodeFile(filename) 

        try:
            data = self.picLoad(picName)
        except:
            print "loading csv"
            with open(csvName, 'rb') as csvfile:
                dialect = csv.Sniffer().sniff(csvfile.read(4096))
                csvfile.seek(0)
                reader = csv.reader(csvfile, dialect)
            
                data = None
                headerStrings = []
                
                for row in reader:
                    if data is None:
                        headerStrings = row
                        data = {}
                        for entry in row:
                            data[entry] = []
                        continue
                    
                    for i, entry in enumerate(row):
                        headerString = headerStrings[i]
                        try:
                            entry = float(entry)
                        except:
                            pass
                        data[headerString].append(entry)
            self.picStore(data, picName)
        self.data = data
        return data
    
    
    def decodeFile(self, filename):
        print "decoding..."
        os.chdir(DECODED_LOGS_PATH)
        cmd = "%s \"%s\"" % (DECODE_EXE, filename)
        os.system(cmd)


    def getBBData(self, name):
        if self.data is None:
            return
        return np.array(self.data[name])
      

    def printStats(self):
        if self.data is None:
            return
        print "Headers:"
        for k, v in sorted(self.data.iteritems()):
            print k

        times = np.diff(self.data["time (us)"])
        print "\nsampling rate", 1.0 / (np.median(times) * 0.000001), "hz"
  
    
if __name__ == '__main__':
    bbLoader = BlackboxLoader()
    #bbLoader.readFile(r"c:\Workspace\LiClipse Workspace\Sandbox\src\bt\blackbox_log_2016-07-03_194817.TXT", 1)
    bbLoader.readFile(r"e:\!_Temp_!\SP3\blackbox tools\blackbox_log_2016-08-28_191425.TXT", 3)

    print bbLoader.getBBData("debug[0]").shape
    bbLoader.printStats()