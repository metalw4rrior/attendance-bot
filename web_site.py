#!/usr/bin/env python3
import sqlite3
from sqlite_func import db_start
from flask import Flask, render_template,request
from datetime import datetime, date
import json
from collections import OrderedDict

app = Flask(__name__)

@app.route('/')
def index():
    current_date = date.today().isoformat()
    return render_template('index.html', current_date=current_date)

@app.route('/process_date', methods=['POST'])
def process_date():
    date_str = request.form['date']
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%Y-%m-%d')
    endings = get_groups_names(formatted_date)
    all_count = []
    for i in endings:
        all_count.append(stats_of_group(i, formatted_date))
    serialized_data = json.dumps(all_count)
    serialized_data_with_brackets = '[' + serialized_data[1:-1] + ']'
    return render_template('index.html', attendance_report=attendance_report(formatted_date,endings), all_TEST_count=serialized_data_with_brackets)

# Выводит стату по дате и в порядке групп
def attendance_report(formatted_date, endings):
    db = sqlite3.connect('database_project.db')         # Оно работает благодаря get_groups_names,
    cur = db.cursor()                                   # который собирает отсортированные группы по подразделениям
    result = []
    for group in endings:
        attendance_report = cur.execute(f"""SELECT * FROM attendance_report
        WHERE group_name LIKE '% {group}%' AND date_of_report == '{formatted_date}' ORDER BY group_name""").fetchall()
        for i in attendance_report:
            result.append(i)
    return result

# Достает имена и сортирует по подразделению
def get_groups_names(formatted_date):
    db = sqlite3.connect('database_project.db')
    cur = db.cursor()
    groups = cur.execute("SELECT group_name FROM groups ORDER BY branch_id").fetchall()
    groups = [list(i) for i in groups]
    name_of_group = []
    for i in groups:
        group = i[0].split()[1]
        name_of_group.append(group)
    groups_names = list(OrderedDict.fromkeys(name_of_group))
    return groups_names

# Собирает в список всю стату по группам одного типа
def stats_of_group(group, formatted_date):
    db = sqlite3.connect('database_project.db')
    cur = db.cursor()
    final_stats = [0,0,0,0]
    stats_of_one_type_of_group = cur.execute(f"""SELECT valid_reason, disrespectful_reason, disease_reason, who_is_present
FROM attendance_report WHERE group_name LIKE '% {group}%' and date_of_report = '{formatted_date}'""").fetchall()
    stats_of_one_type_of_group = [list(i) for i in stats_of_one_type_of_group]

    # Суммируем всю стату по категориям
    for stats_of_one_group in stats_of_one_type_of_group:
        for stat in range(len(stats_of_one_group)):
            if stats_of_one_group[stat] != "-":
                final_stats[stat]+=int(stats_of_one_group[stat])
    
    # Суммируем всех в одну переменную
    sum_all = 0
    for stat in range(len(final_stats)):
        if final_stats[stat] != "-":
            sum_all+=int(final_stats[stat])
    
    # Высчитываем общие проценты для группы
    if sum_all!=0 and final_stats[0] != "-":
        final_stats.append("")     # Комментарий
        final_stats.append(str(round(int(final_stats[3])/sum_all*100))+"%")
        final_stats.append(str(round((sum_all-int(final_stats[1]))/sum_all*100))+"%")
    else:
        final_stats.append("")     # Комментарий
        final_stats.append("0%")
        final_stats.append("0%")

    # Поле "Итого"
    final_stats.insert(0,"Итого")
    
    # Добавляем 3 пустых значения
    for i in range(3):
        final_stats.insert(0,"")
    
    print(final_stats, group) # Для удобства, можно посмотреть вывод в теримнале
    return final_stats


if __name__ == '__main__':
    db_start()
    app.run(host = '0.0.0.0')
