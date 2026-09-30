
import matplotlib.pyplot as plt


def build_figure(numbers, chart_type='hist', figsize=(7, 4), dpi=100):
    if not numbers:
        raise ValueError("Список чисел пуст")

    fig = plt.Figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111)

    if chart_type == 'hist':
        lo, hi = min(numbers), max(numbers)
        if lo == hi:
            hi = lo + 1
        ax.hist(numbers, bins=range(lo, hi + 2), edgecolor='black', align='left')
        ax.set_title("Гистограмма")

    elif chart_type == 'line':
        ax.plot(numbers)
        ax.set_title("Линейный график")

    elif chart_type == 'bar':
        freq = {}
        for x in numbers:
            freq[x] = freq.get(x, 0) + 1
        keys = sorted(freq.keys())
        ax.bar(keys, [freq[k] for k in keys])
        ax.set_title("Столбчатая диаграмма")

    elif chart_type == 'pie':
        freq = {}
        for x in numbers:
            freq[x] = freq.get(x, 0) + 1
        items = sorted(freq.items(), key=lambda kv: -kv[1])[:15]
        labels = [str(k) for k, _ in items]
        sizes = [v for _, v in items]
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title("Круговая диаграмма (топ-15)")
        ax.axis('equal')

    else:
        raise ValueError(f"Неизвестный тип диаграммы: {chart_type}")

    if chart_type != 'pie':
        ax.set_xlabel("Значение")
        ax.set_ylabel("Частота")

    fig.tight_layout()
    return fig


def save_figure(fig, path='histogram.png'):
    fig.savefig(path)


if __name__ == '__main__':
    import os
    from pseudogen import random_gen
    from sortgen import read_numbers

    if os.path.exists('random_numbers.txt'):
        nums = read_numbers('random_numbers.txt')
    else:
        nums = [random_gen(1, 100) for _ in range(1000)]

    fig = build_figure(nums, 'hist')
    save_figure(fig, 'histogram.png')
    print("График сохранён в histogram.png")