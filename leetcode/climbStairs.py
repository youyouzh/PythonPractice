class Solution(object):
    def climbStairs(self, n):
        """
        :type n: int
        :rtype: int
        """

        if n == 1:
            return 1
        elif n == 2:
            return 2
        a, b = 1, 2
        for i in range(2, n):
            a, b = b, a + b

        return b


    def titleToNumber(self, s):
        """
        :type s: str
        :rtype: int
        """

        sum = 0
        for letter in s:
            sum = sum * 26 + (ord(letter) - ord('A') + 1)
        return sum


    def isPalindrome(self, s):
        """
        :type s: str
        :rtype: bool
        """

# s = ''.join(filter(str.isalnum,s)).lower()
        clean_s = ''
        for letter in s:
            if letter.isalnum():
                clean_s += letter.lower()
        return clean_s == clean_s[::-1]


    def firstMissingPositive(self, nums: list) -> int:
        """
            :type nums: List[int]
           :rtype: int
        """

        length = len(nums)
        i = 0
        while i < length:
            # 将值移动到相应下标的位置
            if 0 < nums[i] <= length and nums[nums[i] - 1] != nums[i]:
                # 交换后还需重新检查
                nums[nums[i] - 1], nums[i] = nums[i], nums[nums[i] - 1]
            else:
                i += 1
        for i in range(length):
            # 查找下标不为值的位置
            if nums[i] != i + 1:
                return i + 1
        # 所有位置的值和索引相同，则为长度+1
        return length + 1

    def missingNumber(self, nums: list) -> int:
        length = len(nums)
        i = 0
        while i < length:
            # 将值移动到相应下标的位置
            if 0 <= nums[i] < length and nums[nums[i]] != nums[i]:
                # 交换后还需重新检查
                nums[nums[i]], nums[i] = nums[i], nums[nums[i]]
            else:
                i += 1
        for i in range(length):
            # 查找下标不为值的位置
            if nums[i] != i:
                return i
        # 所有位置的值和索引相同，则为长度+1
        return length

    def missingNumberV2(self, nums: list) -> int:
        sum = len(nums)
        # 值和下标组成一对数
        for i in range(len(nums)):
            sum ^= i
            sum ^= nums[i]
        return sum

    def majorityElement(self, nums: list) -> int:
        count = 1
        # 首先选取第一个作为基准
        base = nums[0]
        for i in range(1, len(nums)):
            # 遇到相同的数则计数加1
            if base == nums[i]:
                count += 1
            else:
                # 遇到不同的计数减1
                count -= 1
                # 如果计数为0，则取下一个为基准
                if count == 0:
                    base = nums[i + 1]
        # 最后一定基准的数的count大于0
        return base

if __name__ == '__main__':
    solution = Solution()
    # result = solution.titleToNumber('AZBBY')
    # result = solution.isPalindrome('acv.!!')
    result = solution.firstMissingPositive([-1, 4, 2, 1, 9, 10])
    print(result)