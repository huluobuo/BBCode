def quick_sort(arr):
    if len(arr) <= 1:
        return arr  # Base case: already sorted

    pivot = arr[0]  # 选择第一个元素作为基准
    left = [x for x in arr[1:] if x <= pivot]
    right = [x for x in arr[1:] if x > pivot]

    return quick_sort(left) + right  # 递归调用

# 示例用法
arr = [12, 8, 11, 7, 6, 5]
sorted_arr = quick_sort(arr)
print("排序后的数组:", sorted_arr)  # 输出: 排序后的数组: [12, 8, 11, 7, 6, 5]