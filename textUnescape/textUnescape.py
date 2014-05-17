#coding:utf-8
#!/usr/bin/python
#indent=4


from xkutils import * 

#dest1 = StringHelper.unescape(src);

raw = TextFileHelper.read('innerclass1.cs');

encoding = TextFileHelper.getEncoding(raw)
unicodeStr = TextFileHelper.getUnicode(raw);
content = StringHelper.unescape(unicodeStr)

TextFileHelper.write('innerclass2.cs', content.encode(encoding) );

