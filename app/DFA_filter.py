import jieba

from app.models import SensitiveWords


# DFA算法
class DFAFilter(object):
    def __init__(self):
        self.keyword_chains = {}  # 关键词链表
        self.delimit = '\x00'  # 限定

    def add(self, keyword):
        keyword = keyword.lower()  # 将关键词中的英文变为小写
        chars = keyword.strip()  # 将关键字去除首尾空格和换行符
        if not chars:  # 如果关键词为空直接返回
            return
        level = self.keyword_chains
        # 遍历关键字的每个字
        for i in range(len(chars)):
            # 如果这个字已经存在字符链的key中就进入其子字典
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self):
        words = SensitiveWords.query.all()
        print(words)
        for word in words:
            keyword = str(word).strip("'")
            self.add(str(keyword).strip())
        print(self.keyword_chains)

    def filter(self, message, repl="*"):
        message = message.lower()
        jieba.initialize()
        separate_words = jieba.lcut(message)
        rets = []
        count = 0
        for separate in separate_words:
            print(separate)
            print(count)
            words = separate_words[count]
            count += 1

            ret = []
            start = 0
            while start < len(words):
                level = self.keyword_chains
                step_ins = 0
                for char in words[start:]:
                    if char in level:
                        step_ins += 1
                        if self.delimit not in level[char]:
                            level = level[char]
                        else:
                            ret.append(repl * step_ins)
                            start += step_ins - 1
                            break
                    else:
                        ret.append(words[start])
                        print('A、' + words[start])
                        break
                else:
                    ret.append(words[start])
                    print('B、' + words[start])
                start += 1

            r = ''.join(ret)
            print(r)
            rets.append(r)

        return ''.join(rets)
