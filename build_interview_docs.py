#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Один файл с заданиями для устного собеседования (без шапок):
- Информатика 2: 20 вариантов, в каждом 5 вопросов с развёрнутым ответом + 5 заданий (разные числа).
- Файл ответов: эталоны на вопросы + ответы на задания.
"""

from pathlib import Path
from docx import Document

from interview_questions import THEORY_QUESTIONS, THEORY_ANSWERS
from task_generators import gen_task1, gen_task2, gen_task3, gen_task4, gen_task5

# Перестановка цифр 0→1..9→0 (как в основных билетах)
DIGIT_MAP = str.maketrans('0123456789', '1234567890')

# Плейсхолдеры для нумерации заданий и вопросов (чтобы не портить заменой цифр)
_TASK_PH = [(f'Задание {n}.', f'Задание_НОМ_{n}_') for n in range(5, 0, -1)]  # 5,4,3,2,1 — длинные первыми
_TASK_RESTORE = [(f'Задание_НОМ_{n}_', f'Задание {n}.') for n in range(1, 6)]

# Защита нумерации вариантов ответа 1)…4) в начале блоков (после \n\n)
_OPT_PROTECT = [
    ('\n\n1) ', '\n\n__ОПЦ_ОДИН_ '),
    ('\n\n2) ', '\n\n__ОПЦ_ДВА_ '),
    ('\n\n3) ', '\n\n__ОПЦ_ТРИ_ '),
    ('\n\n4) ', '\n\n__ОПЦ_ЧЕТЫРЕ_ '),
]
_OPT_RESTORE = [(ph, orig) for orig, ph in _OPT_PROTECT]


def replace_digits_and_names(s: str) -> str:
    """Замена цифр и имён. Нумерацию «Задание 1.» … «Задание 5.» и варианты 1)…4) сохраняем."""
    if not s:
        return s
    for orig, ph in _TASK_PH:
        s = s.replace(orig, ph)
    # Защита нумерации вариантов ответа
    for orig, ph in _OPT_PROTECT:
        s = s.replace(orig, ph)
    s = s.replace('Вася', 'Катя').replace('Васи', 'Кати').replace('Васей', 'Катей')
    s = s.replace('мальчик', 'девочка').replace('Мальчик', 'Девочка')
    s = s.translate(DIGIT_MAP)
    for ph, orig in _TASK_RESTORE:
        s = s.replace(ph, orig)
    # Восстановление нумерации вариантов ответа
    for ph, orig in _OPT_RESTORE:
        s = s.replace(ph, orig)
    return s


# Один файл для собеседования (file_id=2 → другие числа, чем в стандартных Информатика / Информационные технологии)
DISCIPLINES = [
    ('Информатика 2', 2),
]

TASK_GENS = [gen_task1, gen_task2, gen_task3, gen_task4, gen_task5]
NUM_VARIANTS = 20
NUM_QUESTIONS = 5
NUM_TASKS = 5


def build_one_docx(discipline_name: str, file_id: int, base: Path) -> list:
    """
    Создаёт один docx: только варианты, без шапок.
    Возвращает список ответов по вариантам: [ [задание1, ..., задание5], ... ]
    """
    doc = Document()
    # Не добавляем заголовок документа — сразу варианты
    all_answers = []

    for variant_num in range(1, NUM_VARIANTS + 1):
        effective_variant = variant_num + file_id * 20

        # Заголовок варианта
        p = doc.add_paragraph()
        p.add_run(f"Вариант №{variant_num}").bold = True

        # №1–№5: вопросы (без слова «Вопрос»)
        for i in range(NUM_QUESTIONS):
            doc.add_paragraph(f"№{i + 1}", style='Normal')
            doc.add_paragraph(THEORY_QUESTIONS[i])

        # №6–№10: задания (без слова «Задание», только номер и текст)
        task_answers = []
        for i, gen in enumerate(TASK_GENS):
            text, ans = gen(effective_variant)
            text_replaced = replace_digits_and_names(text)
            blocks = [b.strip() for b in text_replaced.split("\n\n") if b.strip()]
            doc.add_paragraph(f"№{NUM_QUESTIONS + i + 1}")  # №6, №7, … №10
            # Первый блок — «Задание N.»; остальное — условие и варианты
            for block in blocks[1:]:
                doc.add_paragraph(block)
            # Задания с выбором варианта (1, 2) — ответ 1–4, сдвиг цифр не применяем
            _MC = {0, 1}
            if i in _MC:
                task_answers.append(str(ans))
            else:
                task_answers.append(str(ans).translate(DIGIT_MAP))
        all_answers.append(task_answers)

    out_name = f"{discipline_name}_собеседование.docx"
    out_path = base / out_name
    doc.save(out_path)
    return all_answers


def write_answer_file(base: Path, discipline_answers: dict):
    """Пишет файл с ответами: по каждому файлу — варианты, по каждому варианту — эталоны на вопросы и ответы на задания."""
    lines = []
    lines.append("ОТВЕТЫ ДЛЯ УСТНОГО СОБЕСЕДОВАНИЯ")
    lines.append("Структура: 5 вопросов с развёрнутым ответом + 5 заданий. Ниже — эталоны ответов на вопросы и ответы на задания.")
    lines.append("")

    for discipline_name, file_id in DISCIPLINES:
        key = (discipline_name, file_id)
        if key not in discipline_answers:
            continue
        task_answers_per_variant = discipline_answers[key]
        lines.append("=" * 70)
        lines.append(f"Дисциплина: {discipline_name}")
        lines.append(f"Файл билетов: {discipline_name}_собеседование.docx")
        lines.append("=" * 70)

        for v in range(NUM_VARIANTS):
            lines.append("")
            lines.append(f"--- Вариант {v + 1} ---")
            lines.append("Вопросы (эталон ответа для проверяющего):")
            for i in range(NUM_QUESTIONS):
                lines.append(f"  Вопрос {i + 1}. {THEORY_ANSWERS[i]}")
            lines.append("Задания (краткий ответ):")
            task_ans = task_answers_per_variant[v]
            for i in range(NUM_TASKS):
                lines.append(f"  Задание {i + 1}. {task_ans[i]}")
        lines.append("")

    txt_path = base / "Ответы_собеседование.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # Docx с таблицей ответов на задания (для быстрой проверки)
    doc = Document()
    doc.add_paragraph("Ответы для устного собеседования", style="Title")
    doc.add_paragraph("Эталоны на вопросы — в файле Ответы_собеседование.txt. В таблице ниже — только ответы на задания (1–5).")
    doc.add_paragraph("")
    for discipline_name, file_id in DISCIPLINES:
        key = (discipline_name, file_id)
        if key not in discipline_answers:
            continue
        task_answers_per_variant = discipline_answers[key]
        doc.add_paragraph(f"{discipline_name}_собеседование.docx", style="Heading 2")
        table = doc.add_table(rows=1 + NUM_VARIANTS, cols=1 + NUM_TASKS)
        table.style = "Table Grid"
        h = table.rows[0].cells
        h[0].text = "Вариант"
        for i in range(NUM_TASKS):
            h[i + 1].text = f"Зад.{i + 1}"
        for v in range(NUM_VARIANTS):
            row = table.rows[v + 1].cells
            row[0].text = str(v + 1)
            for i in range(NUM_TASKS):
                row[i + 1].text = task_answers_per_variant[v][i]
        doc.add_paragraph("")
    docx_path = base / "Ответы_собеседование.docx"
    doc.save(docx_path)

    return txt_path, docx_path


def main():
    base = Path(__file__).resolve().parent
    discipline_answers = {}

    for discipline_name, file_id in DISCIPLINES:
        print(f"Формирование: {discipline_name}_собеседование.docx")
        answers = build_one_docx(discipline_name, file_id, base)
        discipline_answers[(discipline_name, file_id)] = answers
        print(f"  Вариантов: {NUM_VARIANTS}, вопросов: {NUM_QUESTIONS}, заданий: {NUM_TASKS}")

    txt_path, docx_path = write_answer_file(base, discipline_answers)
    print(f"Ответы (эталоны + задания): {txt_path.name}")
    print(f"Таблица ответов на задания: {docx_path.name}")


if __name__ == "__main__":
    main()
