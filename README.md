# statmaster
🤖Данный бот предназначен для автоматизации процесса отправки данных по посещаемости в учебных заведениях. Он находится в тесной связи с локальной базой данных, которая называется database_project.db.

🔒Бот оснащен надежной системой авторизации кураторов по паролям, которые могут быть установлены только администратором. Кроме того, имеется возможность выбора групп, к которым прикреплен куратор, и наличие нескольких групп у одного куратора.

🔍Вводимые данные обрабатываются ботом и заносятся прямо в базу данных. Если нужно, этот продукт можно легко адаптировать под свое учебное учреждение.

❗️💥Важно: перед запуском бота в базе данных должны быть заполнены таблицы с группами и кураторами, а заполнение должно быть выполнено строго в соответствии со столбцами.В файле config.py API_TOKEN должен быть взят у BotFather в телеграме.Утилиты, которые должны быть установлены на сервере: aiogram, Flask, scheduler, asyncio, sqlite3, python3.
❗️💥Важно: чтобы запустить бота на сервере, нужно запустить демона make_it_work.sh

📊Бот запущен вместе со специальным сайтом, который позволяет генерировать отчеты о посещаемости. Данный сайт позволяет делать выборку по дням с помощью календаря. Желтым цветом выделены кураторы, которые не ввели данные о посещаемости. Также для различного рода групп предусмотрено разделение в виде пустой строки, чтобы пользователю было проще ориентироваться в статистике.  

🖥️Все это можно запускать при помощи системы виртуализации, например, на Ubuntu сервере. Кроме того, в репозитории имеются демоны, которые обеспечивают постоянную работу бота.

💪Наконец, для работы бота не требуются большие ресурсы, что делает его экономичным и практичным решением для многих учебных заведений.
