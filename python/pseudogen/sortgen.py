import os


def read_numbers(filename='random_numbers.txt'):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Файл {filename} не найден")
    numbers = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                numbers.append(int(line))
    return numbers


def _bubble_sort_asc(numbers):
    arr = numbers[:]
    n = len(arr)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:           # уже отсортировано — выходим раньше
            break
    return arr

def sort_numbers(numbers, choice):
    if not isinstance(numbers, list):
        raise TypeError("numbers должен быть list")
    if not isinstance(choice, int):
        raise TypeError("choice должно быть int")

    if choice == 1:
        asc = _bubble_sort_asc(numbers)
        n = len(asc)
        desc = [0] * n
        for i in range(n):
            desc[i] = asc[n - 1 - i]
        return desc
    elif choice == 2:
        return _bubble_sort_asc(numbers)
    else:
        raise ValueError("choice должен быть 1 или 2")


def sort_from_file(choice=1, filename='random_numbers.txt'):
    numbers = read_numbers(filename)
    return sort_numbers(numbers, choice)


if __name__ == '__main__':
    try:
        choice = int(input("Введите 1 (по убыванию) или 2 (по возрастанию): "))
        result = sort_from_file(choice)
        print("Отсортированный список:")
        print(result)
    except (ValueError, TypeError, FileNotFoundError) as e:
        print(f"Ошибка: {e}")