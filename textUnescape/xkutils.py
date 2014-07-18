#coding:utf-8
#!/usr/bin/python
#indent=4
import json
import unittest
import codecs
import re
import chardet

class StringHelper:

    @staticmethod
    def unescape(encoded, match = r'\\u(.{4})'):
        return re.sub(match, lambda x: unichr(int(x.group(1), 16)), encoded)

    @staticmethod
    def unescape2(encoded, sep = r'\u'):
        return "".join([(len(i)>=4 and unichr(int(i[0:4],16)) + i[4:] or "") for i in encoded.split(sep)]);

    @staticmethod
    def unescape3(encoded, sep = r'\u'):
        return json.loads('"'+encoded+'"');
 

class TextFileHelper:
    
    @staticmethod
    def smartUnicode(data):
        test = chardet.detect(data);
        if test['confidence'] > 0.5:          
            return data.decode(test['encoding']);
        return data.decode('GB2312'); #在CN中文大多数采用GB2312编码
    
    @staticmethod
    def getEncoding(data):
        if len(data) > 3:
            if data[:3] == codecs.BOM_UTF8:
                return 'utf-8';
            else:
                test = chardet.detect(data);
                return test['encoding'];
        else:
            test = chardet.detect(data);
            return test['encoding'];
    
    @staticmethod
    def getUnicode(data):
        if len(data) > 3:
            if data[:3] == codecs.BOM_UTF8:
                data = data[3:].decode('utf-8');
            else:
                data = TextFileHelper.smartUnicode(data)
        else:
            data = TextFileHelper.smartUnicode(data)
        return data

    @staticmethod
    def read(filename):
        fp = open(filename, 'r');
        data = fp.read();
        fp.close();
        return data;
    
    @staticmethod
    def write(filename, content):
        out = file(filename,"w");
        out.write(content);
        out.close();

class StringHelperTest(unittest.TestCase):
    def testConvert(self):
        src = '\u003CModule\u003E\u007B641531D6\u002DB0C0\u002D451A\u002D91B9\u002D11F620653914\u007D';
        dest = u'<Module>{641531D6-B0C0-451A-91B9-11F620653914}';
        dest1 = StringHelper.unescape(src);
        dest2 = json.loads('"'+src+'"');
        self.assertEqual(dest, dest1);
        self.assertEqual(dest, dest2);
        
if __name__ == '__main__':
    unittest.main()
