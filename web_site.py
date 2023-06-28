#!/usr/bin/env python3
import sqlite3
from sqlite_func import db_start
from flask import Flask, render_template,request,redirect
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
    
    # Достает имена групп в порядке отделений 
    groups = get_groups_names(formatted_date)
    
    # Общая стата по группам
    group_stats = []
    for group in groups:
        group_stats.append(stats_of_group(group, formatted_date))
    
    report = attendance_report(formatted_date, groups) # Тут стата по каждой группе и группе групп :Р
    branches = stats_of_branch(group_stats) # Тут стата по отделениям
    last_row = last_row_stats(branches)
    # Цикл, который добавляет стату по отделениям
    for i in range(len(branches)):
        for j in range(len(report), 0, -1):
            if report[j-1][-1] == branches[i][-1]:
                report.insert(j, branches[i])
                break
    report.append(last_row) # Стата по ВСЕМ группам (самая последняя строка)
    return render_template('index.html', attendance_report=report)

# Выводит стату по дате и в порядке групп
def attendance_report(formatted_date, endings):
    db = sqlite3.connect('database_project.db')         # Оно работает благодаря get_groups_names,
    cur = db.cursor()                                   # который собирает отсортированные группы по отделениям
    result = []
    for group in endings:
        attendance_report = cur.execute(f"""SELECT attendance_report.*, branch_id
        FROM attendance_report
        JOIN groups ON attendance_report.group_name = groups.group_name
        WHERE attendance_report.group_name LIKE '% {group}%' AND attendance_report.date_of_report = '{formatted_date}'
        ORDER BY attendance_report.group_name""").fetchall()
        for current_group_stats in attendance_report:
            result.append(current_group_stats)
        current_group_final = stats_of_group(group, formatted_date)
        result.append(current_group_final)
    return result

@app.route('/month_report', methods=['GET','POST'])
def month_report():
    if request.method == 'GET':
        # Обработка GET запроса
        return render_template('index_sobaki.html')
    date_str = request.form['date']
# Изменяем формат даты
    date_obj = datetime.strptime(date_str, '%Y-%m')
    formatted_date = date_obj.strftime('%Y-%m')
    # Достает имена групп в порядке отделений 
    groups = get_groups_names(formatted_date)
    # Общая стата по группам
    group_stats = []
    for group in groups:
        group_stats.append(stats_of_group(group, formatted_date))
    report = month_result(formatted_date, groups) # Тут стата по каждой группе и группе групп :Р
    branches = stats_of_branch(group_stats) # Тут стата по отделениям
    last_row = last_row_stats(branches)
    # Цикл, который добавляет стату по отделениям
    for i in range(len(branches)):
        for j in range(len(report), 0, -1):
            if report[j-1][-1] == branches[i][-1]:
                report.insert(j, branches[i])
                break
    report.append(last_row) # Стата по ВСЕМ группам (самая последняя строка)
    if request.method == 'GET':
        # Обработка нажатия кнопки "Перейти к month_report"
        return redirect('/month_report')
    # Отображение страницы month_report
    print(report)
    return render_template('index_sobaki.html', month_result=report)

# Выводит стату по дате и в порядке групп
def month_result(formatted_date, endings):
    db = sqlite3.connect('database_project.db')         # Оно работает благодаря get_groups_names,
    cur = db.cursor()                                   # который собирает отсортированные группы по отделениям
    result = []
    for group in endings:
        attendance_report = cur.execute(f"""SELECT attendance_report.group_name,
        attendance_report.curator_fio,
        CAST(SUM(attendance_report.valid_reason) as INT),
        CAST(SUM(attendance_report.disease_reason) as INT),
        CAST(SUM(attendance_report.disease_reason) as INT),
        CAST(SUM(attendance_report.who_is_present) as INT),
        branch_id
        FROM attendance_report
        JOIN groups ON attendance_report.group_name = groups.group_name
        WHERE attendance_report.group_name LIKE '% {group}%' AND attendance_report.date_of_report LIKE '%{formatted_date}%'
        GROUP BY attendance_report.group_name, attendance_report.curator_fio, branch_id
        ORDER BY attendance_report.group_name""").fetchall()
        for current_group_stats in attendance_report:
            # print(list(current_group_stats), end="\n")
            # Суммируем всех в одну переменную
            group_stats = list(current_group_stats)
            sum_all = sum(current_group_stats[2:6])
            # print(group_stats[0], sum_all, group_stats[2:6])
            # Высчитываем общие проценты для группы
            if sum_all!=0 and group_stats[0] != "-":
                group_stats.insert(6,str(round((sum_all-int(group_stats[2]))/sum_all*100))+"%")
                group_stats.insert(6,str(round(int(group_stats[5])/sum_all*100))+"%")
                group_stats.insert(6,"")     # Комментарий
                group_stats.insert(2,"")     # Дата
                group_stats.insert(0,"")     # ID
            else:
                group_stats.insert(6,"0%")
                group_stats.insert(6,"0%")
                group_stats.insert(6,"")     # Комментарий
                group_stats.insert(2,"")     # Дата
                group_stats.insert(0,"")     # ID
            result.append(group_stats)
            # print(list(current_group_stats))
        current_group_final = stats_of_group(group, formatted_date)
        result.append(current_group_final)
    return result


# Достает имена и сортирует по отделениям
def get_groups_names(formatted_date):
    db = sqlite3.connect('database_project.db')
    cur = db.cursor()
    groups = cur.execute("SELECT group_name, branch_id FROM groups ORDER BY branch_id").fetchall()
    groups = [list(i) for i in groups]
    name_of_group = []
    for i in groups:
        group = i[0].split(" ")
        name_of_group.append(" ".join(group[1:]))
    groups_names = list(OrderedDict.fromkeys(name_of_group))
    return groups_names

# Собирает в список всю стату по группам одного типа
def stats_of_group(group, formatted_date):
    db = sqlite3.connect('database_project.db')
    cur = db.cursor()
    group_stats = [0,0,0,0]
    stats_of_one_type_of_group = cur.execute(f"""SELECT valid_reason, disrespectful_reason, disease_reason, who_is_present, branch_id
    FROM attendance_report
    JOIN groups ON attendance_report.group_name = groups.group_name
    WHERE attendance_report.group_name LIKE '% {group}%' AND attendance_report.date_of_report = '{formatted_date}'
    ORDER BY attendance_report.group_name""").fetchall()
    stats_of_one_type_of_group = [list(i) for i in stats_of_one_type_of_group]
    
    # Суммируем всю стату по категориям
    for stats_of_one_group in stats_of_one_type_of_group:
        for stat in range(len(stats_of_one_group)-1):
            if stats_of_one_group[stat] != "-":
                group_stats[stat]+=int(stats_of_one_group[stat])
    
    # Суммируем всех в одну переменную
    sum_all = 0
    for stat in range(len(group_stats)):
        if group_stats[stat] != "-":
            sum_all+=int(group_stats[stat])
    
    # Высчитываем общие проценты для группы
    if sum_all!=0 and group_stats[0] != "-":
        group_stats.append("")     # Комментарий
        group_stats.append(str(round(int(group_stats[3])/sum_all*100))+"%")
        group_stats.append(str(round((sum_all-int(group_stats[1]))/sum_all*100))+"%")
    else:
        group_stats.append("")     # Комментарий
        group_stats.append("0%")
        group_stats.append("0%")
    
    # Поля левее от статистики
    group_stats.insert(0,"ИТОГО:")
    group_stats.insert(0,"")
    group_stats.insert(0,f"Группа: {group}")
    group_stats.insert(0,"")
    
    group_stats.append(stats_of_one_type_of_group[0][4])
    return group_stats


def stats_of_branch(stats_of_groups):

    branches = []
    for i in stats_of_groups:
        branches.append(i[-1])
    branches = list(set(branches))
    
    branches_stats = []

    branch_stats = [0,0,0,0]
    for branch in branches:
        for group in stats_of_groups:
            if group[-1] == branch:
                branch_stats[0]+=group[4]
                branch_stats[1]+=group[5]
                branch_stats[2]+=group[6]
                branch_stats[3]+=group[7]
        sum_all = sum(branch_stats)
        
        # Пустое поле (которое коммент)
        branch_stats.append("")
        if sum_all!=0:
            branch_stats.append(str(round(int(branch_stats[3])/sum_all*100))+"%")
            branch_stats.append(str(round((sum_all-int(branch_stats[1]))/sum_all*100))+"%")
        else:
            branch_stats.append("0%")
            branch_stats.append("0%")
        
        # Номер отделения
        branch_stats.append(branch)
        
        db = sqlite3.connect('database_project.db')
        cur = db.cursor()
        branch_name = cur.execute(f"SELECT branch_name, manager_fio FROM branches WHERE branch_id = {branch}").fetchone()
        
        # Поле "Итого"
        branch_stats.insert(0,"ИТОГО по отделениям:")
        branch_stats.insert(0,branch_name[1]) # Заведующий отделением
        
        # Поля до статистики
        branch_stats.insert(0,branch_name[0]) # Название отделения
        branch_stats.insert(0,"")
        branches_stats.append(branch_stats)
        branch_stats = [0,0,0,0]
    return branches_stats

# Высчитывает все данные для последней строки
def last_row_stats(stats_of_branch):
    final_stats = [0,0,0,0]
    for stats in stats_of_branch:
        final_stats[0] += stats[4]
        final_stats[1] += stats[5]
        final_stats[2] += stats[6]
        final_stats[3] += stats[7]
    sum_all = sum(final_stats)
    final_stats.append("")
    
    if sum_all!=0:
        final_stats.append(str(round(int(final_stats[3])/sum_all*100))+"%")
        final_stats.append(str(round((sum_all-int(final_stats[1]))/sum_all*100))+"%")
    else:
        final_stats.append("0%")
        final_stats.append("0%")
    
    final_stats.insert(0,"ИТОГО ПО ВСЕМ ГРУППАМ:")
    for i in range(3):
        final_stats.insert(0,"")
    return final_stats



if __name__ == '__main__':
    db_start()
    app.run(host = '0.0.0.0')
