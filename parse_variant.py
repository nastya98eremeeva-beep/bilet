# -*- coding: utf-8 -*-
"""Извлечение данных по заданиям из текста варианта (оригинальный docx, до замены цифр)."""

import re


def get_variant_blocks(doc) -> list:
    """Возвращает список (start_para, end_para) для каждого варианта."""
    indices = []
    for i, p in enumerate(doc.paragraphs):
        if re.match(r'Вариант\s*(№\s*)?\d+', p.text.strip(), re.I):
            indices.append(i)
    blocks = []
    for k, start in enumerate(indices):
        end = indices[k + 1] if k + 1 < len(indices) else len(doc.paragraphs)
        blocks.append((start, end))
    return blocks


def block_text(doc, start: int, end: int) -> str:
    return '\n'.join(doc.paragraphs[i].text for i in range(start, min(end, len(doc.paragraphs))))


def parse_task1(text: str) -> tuple:
    """Возвращает (options_decimal, low, high). low/high могут быть None."""
    options = re.findall(r'[1-4]\)\s*(\d+)', text)
    bin_opts = []
    for o in options[:4]:
        o = o.rstrip('2')
        if len(o) == 8 and set(o) <= set('01'):
            bin_opts.append(int(o, 2))
        elif len(o) >= 7:
            try:
                bin_opts.append(int(o[:8], 2))
            except ValueError:
                pass
    # Границы неравенства в тексте часто отсутствуют (формула)
    low = high = None
    m = re.search(r'(\d{7,8})\s*[<]\s*[СC]\s*[<]\s*(\d{7,8})', text)
    if m:
        low, high = int(m.group(1), 2), int(m.group(2), 2)
    return (bin_opts, low, high)


def parse_task2(text: str) -> tuple:
    """Списки файлов и выбранных, маски."""
    lines = [s.strip() for s in text.split('\n') if s.strip()]
    all_files = []
    selected = []
    masks = []
    seen_define = False
    for i, line in enumerate(lines):
        if 'Определите' in line or 'масок' in line:
            seen_define = True
        if re.match(r'^[a-z0-9_]+\.(mp3|mp4|mdb|mpeg)$', line, re.I):
            if not seen_define:
                if line not in all_files:
                    all_files.append(line)
            else:
                selected.append(line)
        if re.match(r'^[1-4]\)\s+\S', line):
            mask = re.sub(r'^[1-4]\)\s*', '', line).rstrip('.;').strip()
            if '*' in mask or '?' in mask:
                masks.append(mask)
    selected = list(dict.fromkeys(selected))[:4]
    if len(all_files) < 6:
        all_files = ['comics.mp3', 'demidov.mp4', 'mig.mp3', 'smi.mdb', 'smi.mp3', 'smi.mpeg']
    if not selected:
        selected = ['comics.mp3', 'demidov.mp4', 'smi.mp3', 'smi.mpeg']
    return (all_files, selected, masks[:4])


def parse_task3(text: str) -> list:
    """Кодовые слова для букв А, Б, В, Г (запятые или 'и'): 00, 01, 100, 101."""
    # "использовали соответственно кодовые слова 00, 01, 100, 101" или "слова 00, 01, 100, 101"
    m = re.search(r'кодовые слова\s*([0-9,\s]+?)(?:\.|\.\s|Укажите|$)', text, re.I | re.DOTALL)
    if not m:
        m = re.search(r'слова\s+([0-9,\s]+?)(?:\.|\.\s|Укажите|$)', text, re.I | re.DOTALL)
    if m:
        raw = m.group(1)
        words = re.findall(r'[01]+', raw)
        if len(words) >= 4:
            return words[:4]
    return []


def parse_task4(text: str) -> tuple:
    """v_down, v_up (бит/с), m_mb (Мбайт). Задание про реле Кати/Пети."""
    bit_rates = re.findall(r'(\d+)\s*бит\s*(?:в\s*секунду|/с|/\s*с)?', text, re.I)
    if not bit_rates:
        bit_rates = re.findall(r'скорост[ьюи]\s*(\d+)\s*бит', text, re.I)
    mb = re.findall(r'(\d+)\s*Мбайт', text, re.I)
    if len(bit_rates) >= 2 and mb:
        return (int(bit_rates[0]), int(bit_rates[1]), int(mb[0]))
    return (None, None, None)


def parse_task5(text: str) -> tuple:
    """(ip_str, network_str)."""
    ips = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', text)
    if len(ips) >= 2:
        return (ips[0], ips[1])
    return (None, None)


def parse_task7(text: str) -> str:
    """Строка выражения вида 9^20 + 3^60 - 5 или 98 + 324 - 18 (без ^ = 9^8 + 3^24 - 18)."""
    m = re.search(r'(\d+)\s*[\^]\s*(\d+)\s*\+\s*(\d+)\s*[\^]\s*(\d+)\s*[–\-]\s*(\d+)', text)
    if m:
        return m.group(0)
    m = re.search(r'(\d+)\s*\+\s*(\d+)\s*[–\-]\s*(\d+)', text)
    if m:
        return m.group(0)
    return ''


def parse_task8(text: str) -> tuple:
    """P, Q, R и варианты A. Сегменты [a,b]."""
    segs = re.findall(r'\[(\d+)\s*,\s*(\d+)\]', text)
    if len(segs) >= 7:
        p, q, r = (int(segs[0][0]), int(segs[0][1])), (int(segs[1][0]), int(segs[1][1])), (int(segs[2][0]), int(segs[2][1]))
        options = [(int(segs[i][0]), int(segs[i][1])) for i in range(3, 7)]
        return (p, q, r, options)
    return (None, None, None, [])


def parse_task9(text: str) -> tuple:
    """(start, end, add_step, tens_step). add_step/tens_step по умолчанию 1 и 10."""
    m = re.search(r'число\s+(\d+)\s+преобразуют\s+в\s+число\s+(\d+)', text, re.I)
    if not m:
        return (None, None, 1, 10)
    start, end = int(m.group(1)), int(m.group(2))
    add_step = 1
    tens_step = 10
    m_add = re.search(r'прибавь\s*(\d+)', text, re.I)
    if m_add:
        add_step = int(m_add.group(1))
    m_tens = re.search(r'(?:десятков|десятки)\s+на\s*(\d+)', text, re.I)
    if m_tens:
        tens_step = int(m_tens.group(1))  # число десятков на 2 → шаг +20
    return (start, end, add_step, tens_step)


def parse_task6(text: str) -> tuple:
    """(длина_пароля, размер_алфавита, кол-во_паролей). Пароль из N символов, набор из K символов, записать M паролей."""
    m = re.search(r'(\d+)\s*символ', text, re.I)
    length = int(m.group(1)) if m else None
    # "из набора X, Y, Z" или "символы из набора И,Н,Ф,О,Р,М,А,Т,К" — считаем уникальные буквы
    m = re.search(r'набор[а]?\s*([А-Яа-яA-Za-z,\s]+?)(?:\.|Каждый|Определите|$)', text, re.I | re.DOTALL)
    if not m:
        m = re.search(r'символы\s+из\s+набора\s+([А-Яа-яA-Za-z,\s]+?)(?:\.|Каждый|$)', text, re.I | re.DOTALL)
    charset_size = None
    if m:
        letters = re.findall(r'[А-Яа-яA-Za-z]', m.group(1))
        if letters:
            charset_size = len(set(letters))
    # "для записи 25 паролей" или "записать 25 паролей"
    m = re.search(r'(?:для записи|записать|записывается)\s*(\d+)\s*парол', text, re.I)
    if not m:
        m = re.search(r'(\d+)\s*парол', text, re.I)
    num_passwords = int(m.group(1)) if m else None
    return (length, charset_size, num_passwords)


def parse_task10(text: str) -> int:
    """Число переменных в задании 10. «Переменных 21» → 21."""
    m = re.search(r'[Пп]еременных?\s*(\d+)', text, re.I)
    if m:
        return int(m.group(1))
    return 10


def extract_all_tasks_from_text(text: str) -> dict:
    """Извлекает данные по заданиям из готового текста варианта (например, после замены цифр)."""
    data = {}
    data[1] = parse_task1(text)
    data[2] = parse_task2(text)
    data[3] = parse_task3(text)
    data[4] = parse_task4(text)
    data[5] = parse_task5(text)
    data[7] = parse_task7(text)
    data[6] = parse_task6(text)
    data[8] = parse_task8(text)
    data[9] = parse_task9(text)
    data[10] = parse_task10(text)
    return data


def extract_all_tasks(doc, start: int, end: int) -> dict:
    """Из блока варианта извлекает данные для всех заданий. Ключи 1..10."""
    text = block_text(doc, start, end)
    return extract_all_tasks_from_text(text)
