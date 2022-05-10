import unittest
import tkinter
from clock import Clock
from datetime import datetime, timedelta


def rightHour(test_hour):
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute
    utc_minute = (test_hour - int(test_hour) + current_minute) // 60
    utc_hour = current_hour + 3 + int(test_hour) + utc_minute
    
    if utc_hour < 0:
        utc_hour += 24
    
    return utc_hour % 24


def testTime(test_hour):
    h = datetime.timetuple(datetime.utcnow()+ timedelta(hours = test_hour))[3]
    return h % 24

    
    
class clockTest(unittest.TestCase):
    
    def testDelta(self):
        root = tkinter.Tk()
        self.obj = Clock(root)
        for c, off_set in self.obj.c_cities:
            self.obj.delta = testTime(off_set)
            self.assertEqual(self.obj.delta, rightHour(off_set))

        

if __name__ == '__main__':
    unittest.main()
        
   