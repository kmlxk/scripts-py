#coding=utf-8  
import random  
import unittest  
  
class TestSequenceFunctions(unittest.TestCase):  
    def setUp(self):  
        self.seq = range(10)  
          
    def test_shuffle(self):  
        # make sure the shuffled sequence does not lose any elements  
        random.shuffle(self.seq)  
        self.seq.sort()  
        self.assertEqual(self.seq, range(10))  
          
        # should raise an exception for an immutable sequence  
        self.assertRaises(TypeError, random.shuffle, (1,2,3))  
  
    def test_choice(self):  
        element = random.choice(self.seq)  
        self.assertTrue(element in self.seq)  
   
    def test_sample(self):  
        with self.assertRaises(ValueError):  
            random.sample(self.seq, 20)  
        for element in random.sample(self.seq, 5):  
            self.assertTrue(element in self.seq)  
  
results_fields = [  
    ("username", unicode),  
    ("showid", unicode),  
    ("total_pv", int),  
    ("pubdate", unicode),  
    ("tags", list),  
    ("showname", unicode),  
    ("pg", int),  
    ("ext", str),  
]  
results_fields_map = dict(results_fields)  
class TestDictValueFormatFunctions(unittest.TestCase):  
    def setUp(self):  
        self.results = [{  
            "username": u"疯狂豆花",  
            "showid": u"130e28f0fe0811e0a046",  
            "total_pv": 14503214,  
            "pubdate": u"2012-07-07 01:22:47",  
            "tags": [  
                "轩辕剑",  
                "天之痕"  
                ],  
            "showname" : u"轩辕剑之天之痕",  
            "pg" : 1,  
            "ext" : "mp4"  
        }  
        ]  
    def test_format(self):  
        self.assertTrue(isinstance(self.results, list), "self.results's type must be dict but got {0}".format(type(self.results)))  
        for r in self.results:  
            for f in results_fields_map:  
                value = r.get(f, None)  
                self.assertTrue(isinstance(value, results_fields_map[f]), u"{0}'s type must be {1} but got {2}".format(value, results_fields_map[f], type(value)))  
                #self.assertTrue(isinstance(value, results_fields_map[f]))  
    def test_value(self):  
        for r in self.results:  
            self.assertEqual(r["pg"], 1)  
            self.assertEqual(r["ext"], u"mp4")  
  
if __name__ == '__main__':  
    # unittest.main() # 用这个是最简单的，下面的用法可以同时测试多个类  
    # unittest.TextTestRunner(verbosity=2).run(suite1) # 这个等价于上述但可设置verbosity=2，省去了运行时加-v  
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)  
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestDictValueFormatFunctions)  
    suite = unittest.TestSuite([suite1, suite2])  
    unittest.TextTestRunner(verbosity=2).run(suite)  