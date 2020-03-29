#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Solution:
    def romanToInt(self, s: str) -> int:
        roman_to_int_map = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        answer = 0
        for i in range(len(s)):
            # 如果当前字符代表的值不小于其右边，就加上该值；否则就减去该值
            if i < len(s) - 1 and roman_to_int_map[s[i]] < roman_to_int_map[s[i + 1]]:
                answer -= roman_to_int_map[s[i]]
            else:
                answer += roman_to_int_map[s[i]]
        return answer

    def longestCommonPrefix(self, strs: list) -> str:
        # 空直接返回空字符串
        if not strs:
            return ""

        common_prefix = ''
        for i in range(len(strs[0])):
            common_prefix += strs[0][i]
            for j in range(1, len(strs)):
                if i >= len(strs[j]):
                    return common_prefix[:-1]
                if strs[j][i] != common_prefix[i]:
                    return common_prefix[:-1]
        return common_prefix


if __name__ == '__main__':
    solution = Solution()
    # result = solution.romanToInt('IX')
    result = solution.longestCommonPrefix(["flower", "flow", "flight"])
    print(result)
    result = solution.longestCommonPrefix(["dog", "racecar", "car"])
    print(result)