# -*- coding: utf-8 -*-
"""
Генерация заданий с гарантированно считающимися ответами.
Каждая функция возвращает (текст_задания, ответ).
Используется seed = вариант (1..20) для воспроизводимости.
"""

import random
import math
import fnmatch
from collections import defaultdict


def _seed(effective_variant: int, task: int):
    """Файл 2 (41-60) — отдельный диапазон seed, чтобы все задания отличались от двух других файлов."""
    if effective_variant >= 41:
        random.seed((effective_variant - 40 + 100) * 100 + task)  # 10100..12000
    else:
        random.seed(effective_variant * 100 + task)


def _scenario_index(effective_variant: int, num_choices: int, shift_per_file: int = 2) -> int:
    """Индекс сценария с учётом файла."""
    base = (effective_variant - 1) % num_choices
    file_offset = (effective_variant - 1) // 20
    return (base + file_offset * shift_per_file) % num_choices


def _is_file2(effective_variant: int) -> bool:
    """Задания для файла «Информатика 2» — другая формулировка."""
    return effective_variant >= 41


def gen_task1(effective_variant: int) -> tuple:
    """Неравенство в двоичной: границы и 4 варианта в тексте. Ответ 1–4."""
    _seed(effective_variant, 1)
    low_dec = random.randint(64, 200)
    high_dec = random.randint(low_dec + 4, 250)
    # Один правильный вариант строго между low и high
    correct = random.randint(low_dec + 1, high_dec - 1)
    wrongs = []
    while len(wrongs) < 3:
        x = random.randint(32, 254)
        if x != correct and (x <= low_dec or x >= high_dec) and x not in wrongs:
            wrongs.append(x)
    opts = [correct] + wrongs
    random.shuffle(opts)
    ans_idx = opts.index(correct) + 1
    low_bin = bin(low_dec)[2:].zfill(8)
    high_bin = bin(high_dec)[2:].zfill(8)
    if _is_file2(effective_variant):
        lines = [
            "Задание 1.",
            f"Дано: {low_bin} < C < {high_bin}. Укажите номер (1–4) числа C в двоичной системе, удовлетворяющего неравенству:",
            f"1) {bin(opts[0])[2:].zfill(8)}",
            f"2) {bin(opts[1])[2:].zfill(8)}",
            f"3) {bin(opts[2])[2:].zfill(8)}",
            f"4) {bin(opts[3])[2:].zfill(8)}.",
        ]
    else:
        lines = [
            "Задание 1.",
            f"Дано: {low_bin} < C < {high_bin}. Какое из чисел С, записанных в двоичной системе счисления, удовлетворяет неравенству?",
            f"1) {bin(opts[0])[2:].zfill(8)}",
            f"2) {bin(opts[1])[2:].zfill(8)}",
            f"3) {bin(opts[2])[2:].zfill(8)}",
            f"4) {bin(opts[3])[2:].zfill(8)}.",
        ]
    return "\n\n".join(lines), str(ans_idx)


def _task2_match(mask: str, name: str) -> bool:
    return fnmatch.fnmatch(name, mask)


def gen_task2(effective_variant: int) -> tuple:
    """Файлы и маски. Одна маска выбирает ровно указанную группу."""
    _seed(effective_variant, 2)
    scenarios = [
        (["comics.mp3", "demidov.mp4", "mig.mp3", "smi.mdb", "smi.mp3", "smi.mpeg"],
         ["comics.mp3", "demidov.mp4", "smi.mp3", "smi.mpeg"],
         ["?*mi*.m*", "*mi*.mp*", "*?mi?.mp*", "*?mi*.mp*"]),
        (["box.txt", "box.csv", "bot.txt", "bot.csv", "bolt.dat"],
         ["box.txt", "box.csv"],
         ["*.csv", "box.*", "b*.*", "bo?.*"]),
        (["rain.mp4", "train.mp4", "rain.mp3", "train.mp3", "gain.mp4"],
         ["rain.mp4", "rain.mp3"],
         ["r*.mp*", "rain.*", "*ain.mp4", "*rain*"]),
        (["a1.x", "a2.x", "b1.x", "b2.x", "a1.y", "b1.y"],
         ["a1.x", "a1.y"],
         ["a1.*", "a?.*", "*1.*", "a*.x"]),
        (["cat.doc", "car.doc", "cut.doc", "cat.pdf", "car.pdf"],
         ["cat.doc", "car.doc"],
         ["ca*.doc", "c*t.doc", "*.doc", "c?r.doc"]),
    ]
    idx = _scenario_index(effective_variant, len(scenarios))
    all_files, selected, masks = scenarios[idx]
    # Определяем номер правильной маски (1–4)
    for i, mask in enumerate(masks):
        chosen = [f for f in all_files if _task2_match(mask, f)]
        if set(chosen) == set(selected):
            answer = str(i + 1)
            break
    else:
        answer = "1"
    if _is_file2(effective_variant):
        lines = [
            "Задание 2.",
            "В каталоге находятся файлы со следующими именами:",
            "\n".join(all_files),
            "Определите, по какой из масок будет выбрана указанная группа файлов:",
            "\n".join(selected),
            "1) " + masks[0] + ";",
            "2) " + masks[1] + ";",
            "3) " + masks[2] + ";",
            "4) " + masks[3] + ".",
        ]
    else:
        lines = [
            "Задание 2.",
            "В каталоге находятся файлы со следующими именами:",
            "\n".join(all_files),
            "Определите, по какой из масок будет выбрана указанная группа файлов:",
            "\n".join(selected),
            "1) " + masks[0] + ";",
            "2) " + masks[1] + ";",
            "3) " + masks[2] + ";",
            "4) " + masks[3] + ".",
        ]
    return "\n\n".join(lines), answer


def _fano_shortest(code_words: list) -> str:
    """Кратчайшее новое кодовое слово (Фано): не префикс и не имеет префикса из code_words."""
    used = set(code_words)
    for length in range(1, 10):
        for x in range(2 ** length):
            w = bin(x)[2:].zfill(length)
            if w in used:
                continue
            if any(p.startswith(w) for p in used if len(p) > len(w)):
                continue
            if any(w.startswith(p) for p in used):
                continue
            return w
    return ""


def gen_task3(effective_variant: int) -> tuple:
    """Фано: 4 кода для А,Б,В,Г; кратчайшее для Д."""
    _seed(effective_variant, 3)
    code_sets = [
        ["00", "01", "100", "101"],   # -> 11
        ["0", "100", "101", "110"],   # -> 111
        ["001", "010", "011", "1"],   # -> 000
        ["00", "10", "11", "010"],    # -> 011
        ["000", "001", "010", "011"], # -> 1 (все четыре начинаются с 0, пятое — "1")
    ]
    idx = _scenario_index(effective_variant, len(code_sets))
    valid = code_sets[idx]
    answer = _fano_shortest(valid)
    if _is_file2(effective_variant):
        lines = [
            "Задание 3.",
            "Для кодирования некоторой последовательности из букв А, Б, В, Г, Д, Е, Ж используют неравномерный двоичный код, удовлетворяющий условию Фано.",
            f"Для букв А, Б, В, Г использовали соответственно кодовые слова {', '.join(valid)}.",
            "Укажите кратчайшее возможное кодовое слово для буквы Д, при котором код допускает однозначное декодирование. Если таких кодов несколько, укажите код с наименьшим числовым значением.",
        ]
    else:
        lines = [
            "Задание 3.",
            "Для кодирования некоторой последовательности, состоящей из букв А, Б, В, Г, Д, Е, Ж решили использовать неравномерный двоичный код, удовлетворяющий условию Фано.",
            f"Для букв А, Б, В, Г использовали соответственно кодовые слова {', '.join(valid)}.",
            "Укажите кратчайшее возможное кодовое слово для буквы Д, при котором код будет допускать однозначное декодирование. Если таких кодов несколько, укажите код с наименьшим числовым значением.",
        ]
    return "\n\n".join(lines), answer


def gen_task4(effective_variant: int) -> tuple:
    """Реле: две скорости (бит/с), объём (Мбайт). Время в секундах."""
    _seed(effective_variant, 4)
    v1 = random.randint(200, 400)
    v2 = random.randint(200, 400)
    m = random.randint(4, 12)
    bits = m * 1024 * 1024 * 8
    if v1 >= v2:
        t = bits / v2
    else:
        t = bits / v1 + bits / v2
    answer = int(t) if abs(t - round(t)) < 1e-6 else int(t) + 1
    if _is_file2(effective_variant):
        lines = [
            "Задание 4.",
            f"У Кати есть доступ в Интернет по высокоскоростному радиоканалу ({v1} бит/с). У Пети — только приём от Кати по низкоскоростному каналу ({v2} бит/с). Катя скачивает для Пети данные объёмом {m} Мбайт и передаёт их ему.",
            "Каков минимально возможный промежуток времени (в секундах) с момента начала скачивания до полного получения данных Петей?",
        ]
    else:
        lines = [
            "Задание 4.",
            f"У Кати есть доступ к Интернет по высокоскоростному одностороннему радиоканалу, обеспечивающему скорость получения информации {v1} бит в секунду. У Пети нет скоростного доступа в Интернет, но есть возможность получать информацию от Кати по низкоскоростному телефонному каналу со средней скоростью {v2} бит в секунду. Петя договорился с Катей, что та будет скачивать для него данные объёмом {m} Мбайт по высокоскоростному каналу и ретранслировать их Пете по низкоскоростному каналу.",
            "Каков минимально возможный промежуток времени (в секундах), с момента начала скачивания Катей данных, до полного их получения Петей?",
        ]
    return "\n\n".join(lines), str(answer)


def gen_task5(effective_variant: int) -> tuple:
    """IP и адрес сети. Наименьший третий байт маски."""
    _seed(effective_variant, 5)
    b3 = random.randint(128, 240)
    mask3 = random.choice([b3, b3 & 0xFC, b3 & 0xF0, 192, 224, 240])
    net3 = b3 & mask3
    ip = f"10.{random.randint(1,200)}.{b3}.{random.randint(1,254)}"
    net = f"10.{ip.split('.')[1]}.{net3}.0"
    for m in range(256):
        if (b3 & m) == net3:
            answer = m
            break
    if _is_file2(effective_variant):
        lines = [
            "Задание 5.",
            f"Для узла с IP-адресом {ip} адрес сети равен {net}.",
            "Чему равно наименьшее возможное значение третьего слева байта маски? Ответ запишите в виде десятичного числа.",
        ]
    else:
        lines = [
            "Задание 5.",
            f"Для узла с IP-адресом {ip} адрес сети равен {net}.",
            "Чему равно наименьшее возможное значение третьего слева байта маски? Ответ запишите в виде десятичного числа.",
        ]
    return "\n\n".join(lines), str(answer)


def gen_task6(effective_variant: int) -> tuple:
    """Пароль: N символов, алфавит K, записать M паролей. Ответ — байты."""
    _seed(effective_variant, 6)
    length = random.choice([12, 15, 16, 20])
    charset = random.randint(8, 16)
    num_pass = random.choice([20, 25, 30, 50])
    bits = length * math.ceil(math.log2(charset))
    bytes_one = math.ceil(bits / 8)
    answer = bytes_one * num_pass
    letters = list("ИНФОРМАТИКАБВГДЕЖЗ")[:charset]
    if _is_file2(effective_variant):
        lines = [
            "Задание 6.",
            f"При регистрации в системе каждому пользователю выдаётся пароль из {length} символов из набора {', '.join(letters)}. Пароль записывается минимально возможным и одинаковым целым количеством байт (посимвольное кодирование, минимальное число бит на символ). Определите объём памяти в байтах для записи {num_pass} паролей.",
        ]
    else:
        lines = [
            "Задание 6.",
            f"При регистрации в компьютерной системе каждому пользователю выдаётся пароль, состоящий из {length} символов и содержащий только символы из набора {', '.join(letters)}. Каждый такой пароль записывается минимально возможным и одинаковым целым количеством байт (посимвольное кодирование, все символы кодируются одинаковым минимальным количеством бит). Определите объём памяти в байтах, отводимый программой для записи {num_pass} паролей.",
        ]
    return "\n\n".join(lines), str(answer)


def gen_task7(effective_variant: int) -> tuple:
    """Выражение a^b + c^d - e в троичной. Сколько цифр 2."""
    _seed(effective_variant, 7)
    a, b = random.choice([(9, 18), (9, 20), (8, 16)])
    c, d = random.choice([(3, 58), (3, 60), (3, 50)])
    e = random.randint(3, 15)
    n = a ** b + c ** d - e
    s = []
    while n:
        s.append(n % 3)
        n //= 3
    answer = (s or [0]).count(2)
    if _is_file2(effective_variant):
        lines = [
            "Задание 7.",
            f"Значение арифметического выражения: {a}^{b} + {c}^{d} – {e} записали в системе счисления с основанием 3. Сколько цифр «2» содержится в этой записи?",
        ]
    else:
        lines = [
            "Задание 7.",
            f"Значение арифметического выражения: {a}^{b} + {c}^{d} – {e} записали в системе счисления с основанием 3. Сколько цифр «2» содержится в этой записи?",
        ]
    return "\n\n".join(lines), str(answer)


def gen_task8(effective_variant: int) -> tuple:
    """Отрезки P, Q, R и 4 варианта A. Формула тождественно ложна. Порядок вариантов ответа зависит от effective_variant."""
    def in_seg(x, s):
        return s[0] <= x <= s[1]
    p, q, r = (15, 30), (5, 10), (20, 25)
    options_base = [(0, 20), (0, 10), (10, 15), (25, 30)]  # правильный ответ — последний [25,30]
    _seed(effective_variant, 8)
    options = list(options_base)
    random.shuffle(options)
    correct_A = (25, 30)
    for ans_idx, A in enumerate(options):
        if A == correct_A:
            correct_pos = ans_idx + 1
            break
    else:
        correct_pos = 4
    opts_str = "; ".join(f"{i+1}) [{a}, {b}]" for i, (a, b) in enumerate(options))
    if _is_file2(effective_variant):
        lines = [
            "Задание 8.",
            f"На числовой прямой даны три отрезка: P = [{p[0]}, {p[1]}], Q = [{q[0]}, {q[1]}] и R = [{r[0]}, {r[1]}]. Выберите такой отрезок A, что формула",
            "((x ∈ P) → (x ∈ Q)) ∧ ((x ∉ A) → (x ∈ R))",
            f"тождественно ложна. Варианты: {opts_str}.",
        ]
    else:
        lines = [
            "Задание 8.",
            f"На числовой прямой даны три отрезка: P = [{p[0]}, {p[1]}], Q = [{q[0]}, {q[1]}] и R = [{r[0]}, {r[1]}]. Выберите такой отрезок A, что формула",
            "((x ∈ P) → (x ∈ Q)) ∧ ((x ∉ A) → (x ∈ R))",
            f"тождественно ложна. Варианты: {opts_str}.",
        ]
    return "\n\n".join(lines), str(correct_pos)


def gen_task9(effective_variant: int) -> tuple:
    """Калькулятор: команда 1 — прибавь 1; команда 2 — увеличь число десятков на 1. Число X в число Y."""
    _seed(effective_variant, 9)
    start = random.randint(5, 15)
    end = random.randint(start + 10, min(start + 50, 60))
    dp = defaultdict(int)
    dp[start] = 1
    for n in range(start, end + 1):
        if dp[n]:
            if n + 1 <= end:
                dp[n + 1] += dp[n]
            if n + 10 <= end and (n // 10) % 10 != 9:
                dp[n + 10] += dp[n]
    answer = dp[end]
    if _is_file2(effective_variant):
        lines = [
            "Задание 9.",
            "У исполнителя Калькулятор две команды, которым присвоены номера:",
            "1) прибавь 1;",
            "2) увеличь число десятков на 1 (например, 23 → 33).",
            "Программа — это последовательность команд. Сколько есть программ, которые число " + str(start) + " преобразуют в число " + str(end) + "?",
        ]
    else:
        lines = [
            "Задание 9.",
            "У исполнителя Калькулятор две команды, которым присвоены номера:",
            "1) прибавь 1;",
            "2) увеличь число десятков на 1 (например, 23 → 33).",
            "Программа — это последовательность команд. Сколько есть программ, которые число " + str(start) + " преобразуют в число " + str(end) + "?",
        ]
    return "\n\n".join(lines), str(answer)


def gen_task10(effective_variant: int) -> tuple:
    """Система логических уравнений: число переменных 6–14, ответ 2^(n/2)."""
    _seed(effective_variant, 10)
    n = 6 + _scenario_index(effective_variant, 5) * 2
    pairs = ["(x{} ≡ x{})".format(2 * k - 1, 2 * k) for k in range(1, n // 2 + 1)]
    eq = " ∧ ".join(pairs) + " = 1"
    answer = 2 ** (n // 2)
    if _is_file2(effective_variant):
        lines = [
            "Задание 10.",
            "Сколько различных решений имеет система уравнений:",
            eq + ",",
            "где x1, x2, …, x{} — логические переменные? В ответе укажите число решений.".format(n),
        ]
    else:
        lines = [
            "Задание 10.",
            "Сколько различных решений имеет система уравнений:",
            eq + ",",
            "где x1, x2, …, x{} — логические переменные? В ответе укажите число решений.".format(n),
        ]
    return "\n\n".join(lines), str(answer)


def generate_all_for_variant(effective_variant: int) -> tuple:
    """Возвращает (тексты заданий 1..10, ответы). effective_variant 1..40: вариант 1 в файле 0 → 1, в файле 1 → 2 и т.д."""
    gens = [gen_task1, gen_task2, gen_task3, gen_task4, gen_task5, gen_task6, gen_task7, gen_task8, gen_task9, gen_task10]
    texts = []
    answers = []
    for g in gens:
        t, a = g(effective_variant)
        texts.append(t)
        answers.append(a)
    return texts, answers
