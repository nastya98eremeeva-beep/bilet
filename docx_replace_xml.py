# -*- coding: utf-8 -*-
"""
Замена текста в docx путём правки XML (без python-docx save).
Сохраняет всю структуру файла — подходит для документов со сложной вёрсткой (таблицы, и т.д.).
"""

import re
import zipfile
import tempfile
import shutil
from pathlib import Path

# Та же логика замен, что и в remake_tickets.py
DIGIT_MAP = str.maketrans('0123456789', '1234567890')

TASK_PLACEHOLDERS = [
    ('Задание 10', 'Задание_ДЕСЯТЬ_'),
    ('Задание 9', 'Задание_ДЕВЯТЬ_'),
    ('Задание 8', 'Задание_ВОСЕМЬ_'),
    ('Задание 7', 'Задание_СЕМЬ_'),
    ('Задание 6', 'Задание_ШЕСТЬ_'),
    ('Задание 5', 'Задание_ПЯТЬ_'),
    ('Задание 4', 'Задание_ЧЕТЫРЕ_'),
    ('Задание 3', 'Задание_ТРИ_'),
    ('Задание 2', 'Задание_ДВА_'),
    ('Задание 1', 'Задание_ОДИН_'),
]
_NAMES = ["ОДИН", "ДВА", "ТРИ", "ЧЕТЫРЕ", "ПЯТЬ", "ШЕСТЬ", "СЕМЬ", "ВОСЕМЬ", "ДЕВЯТЬ", "ДЕСЯТЬ"]
TASK_RESTORE = [(f'Задание_{_NAMES[n-1]}_', f'Задание {n}') for n in range(1, 11)]

INSTR_PLACEHOLDERS = [
    ('Для заданий 3-7, 9-10 ', 'Для заданий_ИНСТР_ТРИ_СЕМЬ_ДЕВЯТЬ_ДЕСЯТЬ_ '),
    ('Для заданий 3-7, 9-10\n', 'Для заданий_ИНСТР_ТРИ_СЕМЬ_ДЕВЯТЬ_ДЕСЯТЬ_\n'),
    ('Для заданий 3-7, 9-10', 'Для заданий_ИНСТР_ТРИ_СЕМЬ_ДЕВЯТЬ_ДЕСЯТЬ_'),
    ('Для заданий 1, 2, 8 ', 'Для заданий_ИНСТР_ОДИН_ДВА_ВОСЕМЬ_ '),
    ('Для заданий 1, 2, 8\n', 'Для заданий_ИНСТР_ОДИН_ДВА_ВОСЕМЬ_\n'),
    ('Для заданий 1, 2, 8', 'Для заданий_ИНСТР_ОДИН_ДВА_ВОСЕМЬ_'),
    ('Для заданий 2 - 21 ', 'Для заданий_ИНСТР_ДВА_ДВАДЦАТЬ_ОДИН_ '),
    ('Для заданий 2 - 21\n', 'Для заданий_ИНСТР_ДВА_ДВАДЦАТЬ_ОДИН_\n'),
    ('Для заданий 2 - 21', 'Для заданий_ИНСТР_ДВА_ДВАДЦАТЬ_ОДИН_'),
    ('Для заданий 1 - 10 ', 'Для заданий_ИНСТР_ОДИН_ДЕСЯТЬ_ '),
    ('Для заданий 1 - 10\n', 'Для заданий_ИНСТР_ОДИН_ДЕСЯТЬ_\n'),
    ('Для заданий 1 - 10', 'Для заданий_ИНСТР_ОДИН_ДЕСЯТЬ_'),
]
INSTR_RESTORE = [
    ('Для заданий_ИНСТР_ТРИ_СЕМЬ_ДЕВЯТЬ_ДЕСЯТЬ_', 'Для заданий 3-7, 9-10'),
    ('Для заданий_ИНСТР_ОДИН_ДВА_ВОСЕМЬ_', 'Для заданий 1, 2, 8'),
    ('Для заданий_ИНСТР_ДВА_ДВАДЦАТЬ_ОДИН_', 'Для заданий 2 - 21'),
    ('Для заданий_ИНСТР_ОДИН_ДЕСЯТЬ_', 'Для заданий 1 - 10'),
]

_VAR_DECADE = ["НУЛЬ", "ОДИН", "ДВА", "ТРИ", "ЧЕТЫРЕ", "ПЯТЬ", "ШЕСТЬ", "СЕМЬ", "ВОСЕМЬ", "ДЕВЯТЬ"]
def _var_ph_2(i):
    return f'Вариант_НОМЕР_{_VAR_DECADE[i // 10]}_{_VAR_DECADE[i % 10]}_'
_VAR_NAMES_1_20 = ["ОДИН", "ДВА", "ТРИ", "ЧЕТЫРЕ", "ПЯТЬ", "ШЕСТЬ", "СЕМЬ", "ВОСЕМЬ", "ДЕВЯТЬ", "ДЕСЯТЬ",
                   "ОДИННАДЦАТЬ", "ДВЕНАДЦАТЬ", "ТРИНАДЦАТЬ", "ЧЕТЫРНАДЦАТЬ", "ПЯТНАДЦАТЬ", "ШЕСТНАДЦАТЬ", "СЕМНАДЦАТЬ", "ВОСЕМНАДЦАТЬ", "ДЕВЯТНАДЦАТЬ", "ДВАДЦАТЬ"]
VARIANT_PLACEHOLDERS = [(f'Вариант № {i:02d}', _var_ph_2(i)) for i in range(20, 0, -1)]
for i in range(20, 0, -1):
    VARIANT_PLACEHOLDERS.append((f'Вариант {i}', f'Вариант_НОМ_{_VAR_NAMES_1_20[i-1]}_'))
# Всегда восстанавливаем в формате «Вариант № 01» … «Вариант № 20»
VARIANT_RESTORE = [(_var_ph_2(i), f'Вариант № {i:02d}') for i in range(1, 21)]
VARIANT_RESTORE += [(f'Вариант_НОМ_{_VAR_NAMES_1_20[i-1]}_', f'Вариант № {i:02d}') for i in range(1, 21)]


def replace_text(s: str) -> str:
    if not s:
        return s
    for orig, ph in INSTR_PLACEHOLDERS:
        s = s.replace(orig, ph)
    for orig, ph in VARIANT_PLACEHOLDERS:
        s = s.replace(orig, ph)
    for orig, ph in TASK_PLACEHOLDERS:
        s = s.replace(orig, ph)
    s = s.replace('2026', 'ГОД_ДВА_НУЛЬ_ДВА_ШЕСТЬ_')
    s = s.replace('2025', 'ГОД_ДВА_НУЛЬ_ДВА_ШЕСТЬ_')
    s = s.replace('2024', 'ГОД_ДВА_НУЛЬ_ДВА_ШЕСТЬ_')
    s = s.replace('У Васи ', 'У Кати ')
    s = s.replace('У Васи\n', 'У Кати\n')
    s = s.replace('У Васи.', 'У Кати.')
    s = s.replace('от Васи ', 'от Кати ')
    s = s.replace('от Васи.', 'от Кати.')
    s = s.replace('от Васи по', 'от Кати по')
    s = s.replace('от Васи', 'от Кати')
    s = s.replace('Компьютер Васи ', 'Компьютер Кати ')
    s = s.replace('Васи может', 'Кати может')
    s = s.replace('с Васей ', 'с Катей ')
    s = s.replace('с Васей,', 'с Катей,')
    s = s.replace('Васей ', 'Катей ')
    s = s.replace('Васей\n', 'Катей\n')
    s = s.replace('Васей.', 'Катей.')
    s = s.replace('Вася ', 'Катя ')
    s = s.replace('Вася\n', 'Катя\n')
    s = s.replace('Вася.', 'Катя.')
    s = s.replace('Васи', 'Кати')
    s = s.replace('Вася', 'Катя')
    s = s.replace('мальчик ', 'девочка ')
    s = s.replace('мальчик.', 'девочка.')
    s = s.replace('мальчик\n', 'девочка\n')
    s = s.replace('Мальчик ', 'Девочка ')
    s = s.replace('Мальчик.', 'Девочка.')
    s = s.replace('мальчик', 'девочка')
    s = s.replace('Мальчик', 'Девочка')
    s = s.translate(DIGIT_MAP)
    for ph, orig in INSTR_RESTORE:
        s = s.replace(ph, orig)
    for ph, orig in VARIANT_RESTORE:
        s = s.replace(ph, orig)
    for ph, orig in TASK_RESTORE:
        s = s.replace(ph, orig)
    s = s.replace('ГОД_ДВА_НУЛЬ_ДВА_ШЕСТЬ_', '2026')
    s = s.replace('3136 г.', '2026 г.').replace('3137 г.', '2026 г.')
    s = re.sub(r'\b3136\s*г\.', '2026 г.', s)
    s = re.sub(r'\b3137\s*г\.', '2026 г.', s)
    s = s.replace('3137', '2026').replace('3136', '2026')
    s = s.replace('5358 г.', '2026 г.').replace('5358', '2026')
    return s


# Обратное отображение номера варианта после замены цифр (12->01, 13->02, ...)
def _variant_mapped(i):
    return f'{i:02d}'.translate(DIGIT_MAP)
_VARIANT_REVERSE = {_variant_mapped(i): f'{i:02d}' for i in range(1, 21)}


def process_xml_content(xml_bytes: bytes) -> bytes:
    """Заменяет текст во всех элементах <w:t>...</w:t>. Сохраняет атрибуты и структуру."""
    try:
        text = xml_bytes.decode('utf-8')
    except Exception:
        return xml_bytes

    def repl(m):
        prefix, content, suffix = m.group(1), m.group(2), m.group(3)
        return prefix + replace_text(content) + suffix

    pattern = re.compile(
        r'(<w:t(?:\s[^>]*)?>)([^<]*)(</w:t>)',
        re.DOTALL
    )
    text = pattern.sub(repl, text)
    # Нумерация вариантов: «Вариант № 12» → «Вариант № 01» (и т.д.), в т.ч. когда номер в отдельном run
    for mapped, correct in _VARIANT_REVERSE.items():
        text = text.replace('Вариант № ' + mapped, 'Вариант № ' + correct)
        # Номер в следующем run: Вариант № </w:t><w:t ...>12</w:t>
        text = re.sub(
            r'(Вариант № </w:t><w:t[^>]*>)\s*' + re.escape(mapped) + r'(\s*</w:t>)',
            r'\g<1>' + correct + r'\g<2>',
            text
        )
    # Год 2026: после замены цифр получается 3137; восстанавливаем даже если разбито по run (31 + 37)
    text = text.replace('3137', '2026').replace('3136', '2026')
    text = re.sub(r'\b3137\s*г\.', '2026 г.', text)
    text = re.sub(r'\b3136\s*г\.', '2026 г.', text)
    text = text.replace('5358 г.', '2026 г.').replace('5358', '2026')
    return text.encode('utf-8')


def process_docx_via_xml(src_path: Path, dst_path: Path) -> None:
    """
    Читает docx как zip, заменяет текст во всех word/*.xml, записывает новый docx.
    Копирует остальные файлы без изменений.
    """
    xml_files = [
        'word/document.xml',
        'word/footnotes.xml',
        'word/endnotes.xml',
    ]
    # Добавляем header/footer если есть
    with zipfile.ZipFile(src_path, 'r') as zf:
        for name in zf.namelist():
            if name.startswith('word/header') and name.endswith('.xml'):
                xml_files.append(name)
            if name.startswith('word/footer') and name.endswith('.xml'):
                xml_files.append(name)
    xml_files = list(dict.fromkeys(xml_files))

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        with zipfile.ZipFile(src_path, 'r') as zf_in:
            zf_in.extractall(tmpdir)
        for xml_name in xml_files:
            f = tmpdir / xml_name
            if f.exists():
                data = f.read_bytes()
                f.write_bytes(process_xml_content(data))
        with zipfile.ZipFile(dst_path, 'w', zipfile.ZIP_DEFLATED) as zf_out:
            for item in sorted(tmpdir.rglob('*')):
                if item.is_file():
                    arcname = item.relative_to(tmpdir)
                    zf_out.write(item, arcname)


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: docx_replace_xml.py input.docx output.docx")
        sys.exit(1)
    process_docx_via_xml(Path(sys.argv[1]), Path(sys.argv[2]))
