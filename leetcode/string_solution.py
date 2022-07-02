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

    def lengthOfLongestSubstring(self, s: str) -> int:
        """
        https://leetcode.cn/problems/longest-substring-without-repeating-characters/
        给定一个字符串 s ，请你找出其中不含有重复字符的 最长子串 的长度
        solution: 滑动窗口，左右指针
        """
        index_right = -1   # 右指针，初始值为 -1，相当于字符串左边界左侧，还没有开始移动

        window_chars = set()
        max_length = 0     # 保存最大子串长度
        for index_left in range(len(s)):
            if index_left > 0:
                # 滑动窗口左指针移动，并移除上一个字符
                window_chars.remove(s[index_left - 1])

            # 下一个字符不重复，则移动滑动窗口右指针
            while index_right + 1 < len(s) and s[index_right + 1] not in window_chars:
                window_chars.add(s[index_right + 1])
                index_right += 1

            max_length = max(max_length, index_right - index_left + 1)

        return max_length

    def expandAroundCenter(self, s, left, right):
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return left + 1, right - 1

    def longestPalindrome(self, s: str) -> str:
        """
        https://leetcode.cn/problems/longest-palindromic-substring/
        给你一个字符串 s，找到 s 中最长的回文子串。
        中心扩散算法
        """
        start, end = 0, 0
        for i in range(len(s)):
            left1, right1 = self.expandAroundCenter(s, i, i)
            left2, right2 = self.expandAroundCenter(s, i, i + 1)
            if right1 - left1 > end - start:
                start, end = left1, right1
            if right2 - left2 > end - start:
                start, end = left2, right2
        return s[start: end + 1]


class SolutionTest:
    def __init__(self):
        self.solution = Solution()

    def longestCommonPrefix(self):
        result = self.solution.longestCommonPrefix(["flower", "flow", "flight"])
        print(result)
        result = self.solution.longestCommonPrefix(["dog", "racecar", "car"])
        print(result)

    def lengthOfLongestSubstring(self):
        """
        abcabcbb -> abc -> 3
        """
        result = self.solution.lengthOfLongestSubstring('abcabcbb')
        assert result == 3

    def longestPalindrome(self):
        """
        输入：s = "babad"  输出："bab"   "aba" 同样是符合题意的答案。
        输入：s = "cbbd"   输出："bb"
        """


if __name__ == '__main__':
    solution_test = SolutionTest()
    solution_test.lengthOfLongestSubstring()
