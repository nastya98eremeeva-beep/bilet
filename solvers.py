# -*- coding: utf-8 -*-
"""
Решатели заданий по информатике (оригинальные числа в тексте).
Ответы для матрицы: для числовых ответов применяется digit_map к строке ответа.
"""

import re
from collections import defaultdict


def apply_digit_map(s: str, digit_map: dict) -> str:
    """Применяет перестановку цифр к строке (для записи ответа в матрицу переделанных билетов)."""
    if not s or not digit_map:
        return s
    return ''.join(digit_map.get(c, c) for c in s)


def solve_task1_binary_inequality(options_bin: list, low_dec: int = None, high_dec: int = None) -> str:
    """
    Задание 1: какое из чисел (в двоичной) удовлетворяет неравенству low < C < high.
    options_bin: список из 4 чисел в десятичном (уже переведённые из двоичного).
    Возвращает номер варианта 1-4 или '' если границы не заданы.
    """
    if low_dec is None or high_dec is None:
        return ''
    for i, val in enumerate(options_bin):
        if low_dec < val < high_dec:
            return str(i + 1)
    return ''


def solve_task2_mask(file_list: list, selected: list, masks: list) -> str:
    """
    Задание 2: какая маска выбирает ровно указанную группу файлов.
    file_list — все файлы, selected — выбранная группа, masks — список масок (строк).
    Возвращает номер маски 1-4 или ''.
    """
    def match_mask(mask: str, filename: str) -> bool:
        # Упрощённо: * — любое, ? — один символ
        import fnmatch
        return fnmatch.fnmatch(filename, mask.replace('*', '*').replace('?', '?'))

    for idx, mask in enumerate(masks):
        if idx >= 4:
            break
        chosen = [f for f in file_list if match_mask(mask, f)]
        if set(chosen) == set(selected):
            return str(idx + 1)
    return ''


def solve_task3_fano(code_words: list) -> str:
    """
    Задание 3: для букв А,Б,В,Г даны кодовые слова. Найти кратчайшее кодовое слово для Д (Фано).
    Ни одно кодовое слово не должно быть префиксом другого.
    """
    if len(code_words) < 4:
        return ''
    used = set(code_words)
    # Запрещено: w такое, что (1) w уже есть, (2) w — префикс какого-то кода, (3) какой-то код — префикс w
    for length in range(1, 10):
        for x in range(2 ** length):
            w = bin(x)[2:].zfill(length)
            if w in used:
                continue
            if any(p.startswith(w) for p in used if len(p) > len(w)):  # w — префикс кода
                continue
            if any(w.startswith(p) for p in used):  # код — префикс w
                continue
            return w
    return ''


def solve_task6_password(length: int, charset_size: int, num_passwords: int) -> int:
    """
    Задание 6: пароль из length символов, алфавит размера charset_size, записать num_passwords паролей.
    Минимальное целое число байт на пароль, затем * num_passwords.
    """
    if not all((length, charset_size, num_passwords)):
        return 0
    import math
    bits_per_char = math.ceil(math.log2(charset_size))
    bits_total = length * bits_per_char
    bytes_per_password = math.ceil(bits_total / 8)
    return bytes_per_password * num_passwords


def solve_task4_relay(v_down: int, v_up: int, m_mb: int) -> int:
    """
    Задание 4: скорость приёма v_down бит/с, передачи v_up бит/с, объём M Мбайт.
    Минимальное время (сек) до полного получения данных.
    """
    bits = m_mb * 1024 * 1024 * 8
    if v_down >= v_up:
        t = bits / v_up
    else:
        t = bits / v_down + bits / v_up
    return int(t) if abs(t - round(t)) < 1e-6 else int(t) + 1


def solve_task5_mask_byte(ip_str: str, net_str: str) -> int:
    """
    Задание 5: IP и адрес сети. Наименьшее возможное значение третьего слева байта маски.
    """
    ip = [int(x) for x in ip_str.split('.')]
    net = [int(x) for x in net_str.split('.')]
    # Третий байт (индекс 2): ip[2] & mask[2] = net[2]
    a, b = ip[2], net[2]
    # Минимальный байт маски: 255 даёт a, нужно b. a & m = b => m должен быть >= b и (a & m)=b.
    # Наименьшее m: m = b подходит (a & b = b только если b имеет 1 только там, где a имеет 1).
    # Иначе перебираем. b = 192, a = 208. 208 & 192 = 192. Так что 192 подходит.
    for m in range(256):
        if (a & m) == b:
            return m
    return 0


def solve_task7_base3_count2(expr: str) -> int:
    """
    Задание 7: значение выражения (a^b + c^d - e) записали в системе с основанием 3. Сколько цифр «2»?
    expr: "9^20 + 3^60 - 5" или "98 + 324 - 18" (98 = 9^8, 324 = 3^24).
    """
    parts = re.findall(r'(\d+)\s*[\^]\s*(\d+)\s*\+\s*(\d+)\s*[\^]\s*(\d+)\s*[–\-]\s*(\d+)', expr)
    if parts:
        a, b, c, d, e = int(parts[0][0]), int(parts[0][1]), int(parts[0][2]), int(parts[0][3]), int(parts[0][4])
    else:
        nums = re.findall(r'\d+', expr)
        if len(nums) >= 5:
            a, b, c, d, e = int(nums[0]), int(nums[1]), int(nums[2]), int(nums[3]), int(nums[4])
        elif len(nums) == 3:
            # Формат "98 + 324 - 18": 98 = 9^8, 324 = 3^24
            x, y, e = int(nums[0]), int(nums[1]), int(nums[2])
            if 10 <= x <= 99 and 100 <= y <= 999:
                a, b = x // 10, x % 10
                c, d = y // 100, y % 100
            else:
                return 0
        else:
            return 0
    n = a ** b + c ** d - e
    if n <= 0:
        return 0
    s = []
    while n:
        s.append(n % 3)
        n //= 3
    return (s or [0]).count(2)


def solve_task8_segments(p: tuple, q: tuple, r: tuple, options: list) -> str:
    """
    Задание 8: P, Q, R — отрезки [a,b]. Формула ((x∈P)→(x∈Q)) ∧ ((x∉A)→(x∈R)) тождественно ложна.
    options: список из 4 отрезков [a,b]. Вернуть номер 1-4.
    """
    def in_seg(x, seg):
        return seg[0] <= x <= seg[1]

    for ans_idx, A in enumerate(options):
        ok = True
        for x in range(-5, 260):  # проверка по целым
            in_p, in_q, in_r = in_seg(x, p), in_seg(x, q), in_seg(x, r)
            in_a = in_seg(x, A)
            imp_pq = (not in_p) or in_q
            imp_ar = (in_a) or in_r
            if imp_pq and imp_ar:
                ok = False
                break
        if ok:
            return str(ans_idx + 1)
    return ''


def solve_task9_calculator(start: int, end: int, add_step: int = 1, tens_step: int = 1) -> int:
    """
    Задание 9: Калькулятор. Команда 1: прибавь add_step; команда 2: увеличь число десятков на tens_step (шаг +10*tens_step).
    Сколько программ переводят start в end?
    tens_step=1 → +10 (десятков на 1), tens_step=2 → +20 (десятков на 2).
    """
    step_add = add_step
    step_tens = 10 * tens_step
    dp = defaultdict(int)
    dp[start] = 1
    for n in range(start, end + 1):
        if dp[n] == 0:
            continue
        if n + step_add <= end:
            dp[n + step_add] += dp[n]
        # Не переполняем разряд десятков: (n//10)%10 + tens_step <= 9
        if step_tens and n + step_tens <= end and (n // 10) % 10 + tens_step <= 9:
            dp[n + step_tens] += dp[n]
    return dp[end]


def solve_task10_logic_system(num_vars: int = 10) -> int:
    """
    Задание 10: цепочка эквивалентностей по парам переменных.
    Чётное n: пары (x1≡x2), (x3≡x4), ... — решений 2^(n/2).
    Нечётное n (например 21): 10 пар + одна свободная переменная — решений 2^10 * 2 = 2^11.
    """
    if num_vars <= 0:
        return 0
    if num_vars % 2 == 0:
        return 2 ** (num_vars // 2)
    # Нечётное: (n-1)/2 пар и одна свободная
    return 2 ** ((num_vars - 1) // 2 + 1)


def solve_all(extracted: dict, digit_map_trans: str = None) -> list:
    """
    По данным extract_all_tasks возвращает список ответов [задание1, задание2, ...].
    digit_map_trans: строка для str.maketrans('0123456789', '1234567890') — перестановка цифр для ответа.
    """
    digit_map = dict(zip('0123456789', digit_map_trans or '1234567890')) if digit_map_trans else None

    def apply_map(s):
        if s is None or s == '':
            return s
        return apply_digit_map(str(s), digit_map) if digit_map else str(s)

    answers = [''] * 10
    # 1
    t1 = extracted.get(1)
    if t1 and len(t1) >= 3:
        opts, low, high = t1[0], t1[1], t1[2]
        if opts:
            answers[0] = solve_task1_binary_inequality(opts, low, high)
    # 2
    t2 = extracted.get(2)
    if t2 and len(t2) >= 3:
        fl, sel, masks = t2[0], t2[1], t2[2]
        if fl and masks:
            answers[1] = solve_task2_mask(fl, sel, masks)
    # 3
    t3 = extracted.get(3)
    if t3 and len(t3) >= 4:
        answers[2] = solve_task3_fano(t3)
        if answers[2] and digit_map:
            answers[2] = apply_map(answers[2])
    # 4
    t4 = extracted.get(4)
    if t4 and all(t4):
        v1, v2, m = t4[0], t4[1], t4[2]
        answers[3] = apply_map(solve_task4_relay(v1, v2, m))
    # 5
    t5 = extracted.get(5)
    if t5 and all(t5):
        answers[4] = apply_map(solve_task5_mask_byte(t5[0], t5[1]))
    # 6
    t6 = extracted.get(6)
    if t6 and all(t6):
        answers[5] = apply_map(solve_task6_password(t6[0], t6[1], t6[2]))
    # 7
    t7 = extracted.get(7)
    if t7:
        cnt = solve_task7_base3_count2(t7)
        answers[6] = apply_map(cnt) if cnt is not None else ''
    # 8
    t8 = extracted.get(8)
    if t8 and len(t8) == 4 and all(t8[3]):
        p, q, r, opts = t8[0], t8[1], t8[2], t8[3]
        answers[7] = solve_task8_segments(p, q, r, opts)
    # 9
    t9 = extracted.get(9)
    if t9 and len(t9) >= 2 and t9[0] is not None and t9[1] is not None:
        add_step = t9[2] if len(t9) > 2 else 1
        tens_step = t9[3] if len(t9) > 3 else 1
        answers[8] = apply_map(solve_task9_calculator(t9[0], t9[1], add_step, tens_step))
    # 10
    t10 = extracted.get(10)
    num_vars = t10 if isinstance(t10, int) and t10 > 0 else 10
    answers[9] = apply_map(solve_task10_logic_system(num_vars))
    return answers
