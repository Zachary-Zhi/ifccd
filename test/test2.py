from pathlib import Path
import os
# str1 = "\\\\192.168.8.250\\share1\\fusion\\a.tif"
str2 = "//192.168.8.249/share/ifccd/photo/IR_VIS1_1.tif"
# p = Path(str1)
# lparts1 = list(p.parts)
# print(lparts1)
# p = Path(str2)
# lparts2 = list(p.parts)
# print(lparts2)
# linux_path = '/'.join(str1.split('\\'))
# print(linux_path)
# p = Path(linux_path)
# lparts3 = list(p.parts)
# print(lparts3)


p = Path(str2)
print(p)
lparts = list(p.parts)
print(lparts)
filename = lparts[-1]
del lparts[-1]
del lparts[-1]
del lparts[0]
str111 = "/".join(lparts)
print(str111)
print(filename)
print("//" + str111 + "/" + filename)