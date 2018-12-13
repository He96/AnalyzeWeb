import re

name = re.search(r'《.*》', '《文化寻真：人类学学者访谈录:（2005～2015）（套装全2册）》 …', flags=0).group(0)
name = name[1:len(name)-1]
print(name)