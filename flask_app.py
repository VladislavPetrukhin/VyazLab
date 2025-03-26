from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Абсолютный путь к базе данных
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

# Ограничения для валидации
VALIDATION_RULES = {
    'processors': {
        'model_name': {'min_length': 3, 'max_length': 100},  # 3-100 символов
        'release_year': {'min': 1970, 'max': 2025},
        'cores': {'min': 1, 'max': 128},
        'threads': {'min': 1, 'max': 256},
        'base_clock': {'min': 0.5, 'max': 7.0},
        'max_clock': {'min': 0.5, 'max': 10.0},
        'tdp': {'min': 0, 'max': 500}
    },
    'manufacturers': {
        'company_name': {'min_length': 3, 'max_length': 100},
        'country': {'min_length': 3, 'max_length': 50},
        'founded_year': {'min': 1900, 'max': 2025},
        'employees': {'min': 1, 'max': 1000000}
    },
    'config': {
        'motherboard_model': {'min_length': 3, 'max_length': 100},
        'ram_type': {'min_length': 3, 'max_length': 20},
        'ram_size': {'min': 1, 'max': 4096},
        'socket_type': {'min_length': 3, 'max_length': 20}
    },
    'performance_tests': {
        'single_core_score': {'min': 0, 'max': 10000},
        'multi_core_score': {'min': 0, 'max': 10000},
        'power_consumption': {'min': 1, 'max': 1000},
        'temperature': {'min': 20, 'max': 100},
        'test_duration': {'min': 0.1, 'max': 24},
        'test_stand_info': {'min_length': 5, 'max_length': 200},
        'ram_used': {'min_length': 3, 'max_length': 50},
        'storage_used': {'min_length': 3, 'max_length': 50},
        'gpu_used': {'min_length': 3, 'max_length': 50},
        'cooling_system': {'min_length': 3, 'max_length': 50}
    }
}

# Функция для валидации данных
def validate_data(data, rules):
    errors = []
    for field, value in data.items():
        if value is None or value == '':
            continue  # Пропускаем необязательные поля
        if field in rules:
            field_rules = rules[field]
            if 'min_length' in field_rules and len(value) < field_rules['min_length']:
                errors.append(f"{field}: длина должна быть не менее {field_rules['min_length']} символов")
            if 'max_length' in field_rules and len(value) > field_rules['max_length']:
                errors.append(f"{field}: длина не должна превышать {field_rules['max_length']} символов")
            if 'min' in field_rules or 'max' in field_rules:
                try:
                    num_value = float(value) if '.' in value else int(value)
                    if 'min' in field_rules and num_value < field_rules['min']:
                        errors.append(f"{field}: значение должно быть не менее {field_rules['min']}")
                    if 'max' in field_rules and num_value > field_rules['max']:
                        errors.append(f"{field}: значение не должно превышать {field_rules['max']}")
                except ValueError:
                    errors.append(f"{field}: должно быть числом")
    return errors

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Просмотр процессоров
@app.route('/view')
def view():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT p.id, p.model_name, p.release_year, m.company_name, 
                   p.cores, p.threads, p.base_clock, p.max_clock, p.tdp,
                   m.country, m.founded_year, m.employees,
                   conf.motherboard_model, conf.ram_type, conf.ram_size, conf.socket_type,
                   pt.single_core_score, pt.multi_core_score, pt.power_consumption, 
                   pt.temperature, pt.test_duration, pt.test_stand_info, 
                   pt.ram_used, pt.storage_used, pt.gpu_used, pt.cooling_system
            FROM processors p
            JOIN manufacturers m ON p.manufacturer_id = m.id
            LEFT JOIN config conf ON p.config_id = conf.id
            LEFT JOIN performance_tests pt ON p.performance_tests_id = pt.id
            ORDER BY p.id
        """
        processors = cursor.execute(query).fetchall()
    return render_template('view.html', processors=processors)

# Поиск процессоров
@app.route('/search', methods=['GET', 'POST'])
def search():
    results = None
    model_name = None
    company_name = None
    country = None
    motherboard_model = None

    if request.method == 'POST':
        model_name = request.form.get('model_name', '').strip()
        company_name = request.form.get('company_name', '').strip()
        country = request.form.get('country', '').strip()
        motherboard_model = request.form.get('motherboard_model', '').strip()

        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT p.id, p.model_name, p.release_year, m.company_name, 
                       p.cores, p.threads, p.base_clock, p.max_clock, p.tdp,
                       m.country, m.founded_year, m.employees,
                       conf.motherboard_model, conf.ram_type, conf.ram_size, conf.socket_type,
                       pt.single_core_score, pt.multi_core_score, pt.power_consumption, 
                       pt.temperature, pt.test_duration, pt.test_stand_info, 
                       pt.ram_used, pt.storage_used, pt.gpu_used, pt.cooling_system
                FROM processors p
                JOIN manufacturers m ON p.manufacturer_id = m.id
                LEFT JOIN config conf ON p.config_id = conf.id
                LEFT JOIN performance_tests pt ON p.performance_tests_id = pt.id
                WHERE 1=1
            """
            params = []

            if model_name:
                query += " AND p.model_name LIKE ?"
                params.append(f"%{model_name}%")
            if company_name:
                query += " AND m.company_name LIKE ?"
                params.append(f"%{company_name}%")
            if country:
                query += " AND m.country LIKE ?"
                params.append(f"%{country}%")
            if motherboard_model:
                query += " AND conf.motherboard_model LIKE ?"
                params.append(f"%{motherboard_model}%")

            results = cursor.execute(query, params).fetchall()

    return render_template('search.html', results=results, model_name=model_name, 
                          company_name=company_name, country=country, motherboard_model=motherboard_model)

# Добавление процессора (простой режим)
@app.route('/add', methods=['GET', 'POST'])
def add():
    errors = []
    processors = None
    
    # Получаем списки для выпадающих меню
    with get_db_connection() as conn:
        manufacturers = conn.execute("SELECT id, company_name FROM manufacturers ORDER BY company_name").fetchall()
        configs = conn.execute("SELECT id, motherboard_model FROM config ORDER BY id").fetchall()
        performance_tests = conn.execute("SELECT id, single_core_score, multi_core_score FROM performance_tests ORDER BY id").fetchall()

    if request.method == 'POST':
        # Собираем данные для процессора
        processor_data = {
            'model_name': request.form.get('model_name', '').strip(),
            'release_year': request.form.get('release_year', '').strip(),
            'cores': request.form.get('cores', ''),
            'threads': request.form.get('threads', ''),
            'base_clock': request.form.get('base_clock', ''),
            'max_clock': request.form.get('max_clock', ''),
            'tdp': request.form.get('tdp', '')
        }
        manufacturer_id = request.form.get('manufacturer_id')
        config_id = request.form.get('config_id')
        performance_tests_id = request.form.get('performance_tests_id')

        # Валидация обязательных полей
        if not all([processor_data['model_name'], processor_data['release_year'], manufacturer_id]):
            errors.append("Обязательные поля (название модели, год выпуска, производитель) должны быть заполнены")
        else:
            # Валидация данных процессора
            validation_errors = validate_data(processor_data, VALIDATION_RULES['processors'])
            errors.extend(validation_errors)

            if not errors:
                try:
                    release_year = int(processor_data['release_year'])
                    manufacturer_id = int(manufacturer_id)
                    cores = int(processor_data['cores']) if processor_data['cores'] else None
                    threads = int(processor_data['threads']) if processor_data['threads'] else None
                    base_clock = float(processor_data['base_clock']) if processor_data['base_clock'] else None
                    max_clock = float(processor_data['max_clock']) if processor_data['max_clock'] else None
                    tdp = int(processor_data['tdp']) if processor_data['tdp'] else None
                    config_id = int(config_id) if config_id else None
                    performance_tests_id = int(performance_tests_id) if performance_tests_id else None

                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO processors (model_name, release_year, manufacturer_id, cores, threads, base_clock, max_clock, tdp, config_id, performance_tests_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (processor_data['model_name'], release_year, manufacturer_id, cores, threads, base_clock, max_clock, tdp, config_id, performance_tests_id))
                        conn.commit()
                        
                        # Получаем обновлённый список процессоров с дополнительной информацией
                        processors = cursor.execute("""
                            SELECT p.id, p.model_name, p.release_year, 
                                   m.company_name AS manufacturer_name,
                                   p.cores, p.threads,
                                   conf.motherboard_model,
                                   pt.single_core_score, pt.multi_core_score
                            FROM processors p
                            LEFT JOIN manufacturers m ON p.manufacturer_id = m.id
                            LEFT JOIN config conf ON p.config_id = conf.id
                            LEFT JOIN performance_tests pt ON p.performance_tests_id = pt.id
                            ORDER BY p.id
                        """).fetchall()
                except ValueError:
                    errors.append("Год выпуска и ID должны быть числами")
                except sqlite3.IntegrityError:
                    errors.append("Ошибка: такой процессор уже существует или указаны неверные ID")
    else:
        with get_db_connection() as conn:
            processors = conn.execute("""
                SELECT p.id, p.model_name, p.release_year, 
                       m.company_name AS manufacturer_name,
                       p.cores, p.threads,
                       conf.motherboard_model,
                       pt.single_core_score, pt.multi_core_score
                FROM processors p
                LEFT JOIN manufacturers m ON p.manufacturer_id = m.id
                LEFT JOIN config conf ON p.config_id = conf.id
                LEFT JOIN performance_tests pt ON p.performance_tests_id = pt.id
                ORDER BY p.id
            """).fetchall()

    return render_template('add.html', errors=errors, processors=processors, manufacturers=manufacturers, 
                          configs=configs, performance_tests=performance_tests)

# Редактирование процессора
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    errors = []
    if request.method == 'POST':
        processor_data = {
            'model_name': request.form['model_name'],
            'release_year': request.form['release_year'],
            'cores': request.form['cores'],
            'threads': request.form['threads'],
            'base_clock': request.form['base_clock'],
            'max_clock': request.form['max_clock'],
            'tdp': request.form['tdp']
        }
        errors = validate_data(processor_data, VALIDATION_RULES['processors'])
        if not errors:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE processors 
                    SET model_name = ?, release_year = ?, manufacturer_id = ?, cores = ?, threads = ?, base_clock = ?, max_clock = ?, tdp = ?, config_id = ?, performance_tests_id = ?
                    WHERE id = ?
                """, (processor_data['model_name'], processor_data['release_year'], request.form['manufacturer_id'], 
                      processor_data['cores'], processor_data['threads'], processor_data['base_clock'], processor_data['max_clock'], processor_data['tdp'], 
                      request.form['config_id'] or None, request.form['performance_tests_id'] or None, id))
                conn.commit()
            return redirect(url_for('view'))
    
    with get_db_connection() as conn:
        processor = conn.execute("""
            SELECT p.*, m.company_name
            FROM processors p 
            JOIN manufacturers m ON p.manufacturer_id = m.id 
            WHERE p.id = ?
        """, (id,)).fetchone()
        manufacturers = conn.execute("SELECT id, company_name FROM manufacturers").fetchall()
        configs = conn.execute("SELECT id, motherboard_model FROM config").fetchall()
        performance_tests = conn.execute("SELECT id, single_core_score, multi_core_score FROM performance_tests").fetchall()
    return render_template('edit.html', processor=processor, manufacturers=manufacturers, 
                          configs=configs, performance_tests=performance_tests, errors=errors)

# Производители
@app.route('/manufacturers', methods=['GET', 'POST'])
def manufacturers():
    errors = []
    if request.method == 'POST':
        data = {
            'company_name': request.form['company_name'],
            'country': request.form['country'],
            'founded_year': request.form['founded_year'],
            'employees': request.form['employees']
        }
        errors = validate_data(data, VALIDATION_RULES['manufacturers'])
        if not errors:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO manufacturers (company_name, country, founded_year, employees)
                    VALUES (?, ?, ?, ?)
                """, (data['company_name'], data['country'], data['founded_year'], data['employees']))
                conn.commit()
    with get_db_connection() as conn:
        manufacturers = conn.execute("SELECT id, company_name, country, founded_year, employees FROM manufacturers ORDER BY company_name").fetchall()
    return render_template('manufacturers.html', manufacturers=manufacturers, errors=errors)

@app.route('/edit_manufacturer/<int:id>', methods=['GET', 'POST'])
def edit_manufacturer(id):
    errors = []
    if request.method == 'POST':
        data = {
            'company_name': request.form['company_name'],
            'country': request.form['country'],
            'founded_year': request.form['founded_year'],
            'employees': request.form['employees']
        }
        errors = validate_data(data, VALIDATION_RULES['manufacturers'])
        if not errors:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE manufacturers 
                    SET company_name = ?, country = ?, founded_year = ?, employees = ?
                    WHERE id = ?
                """, (data['company_name'], data['country'], data['founded_year'], data['employees'], id))
                conn.commit()
            return redirect(url_for('manufacturers'))
    with get_db_connection() as conn:
        manufacturer = conn.execute("SELECT id, company_name, country, founded_year, employees FROM manufacturers WHERE id = ?", (id,)).fetchone()
    return render_template('edit_manufacturer.html', manufacturer=manufacturer, errors=errors)

# Конфигурации
@app.route('/config', methods=['GET', 'POST'])
def config():
    errors = []
    if request.method == 'POST':
        data = {
            'processor_id': request.form['processor_id'],
            'motherboard_model': request.form['motherboard_model'],
            'ram_type': request.form['ram_type'],
            'ram_size': request.form['ram_size'],
            'socket_type': request.form['socket_type']
        }
        errors = validate_data(data, VALIDATION_RULES['config'])
        if not errors:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO config (processor_id, motherboard_model, ram_type, ram_size, socket_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (data['processor_id'], data['motherboard_model'], data['ram_type'], data['ram_size'], data['socket_type']))
                conn.commit()
    with get_db_connection() as conn:
        configs = conn.execute("SELECT id, processor_id, motherboard_model, ram_type, ram_size, socket_type FROM config ORDER BY id").fetchall()
        processors = conn.execute("SELECT id, model_name FROM processors").fetchall()
    return render_template('config.html', configs=configs, processors=processors, errors=errors)

@app.route('/edit_config/<int:id>', methods=['GET', 'POST'])
def edit_config(id):
    errors = []
    if request.method == 'POST':
        data = {
            'processor_id': request.form['processor_id'],
            'motherboard_model': request.form['motherboard_model'],
            'ram_type': request.form['ram_type'],
            'ram_size': request.form['ram_size'],
            'socket_type': request.form['socket_type']
        }
        errors = validate_data(data, VALIDATION_RULES['config'])
        if not errors:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE config 
                    SET processor_id = ?, motherboard_model = ?, ram_type = ?, ram_size = ?, socket_type = ?
                    WHERE id = ?
                """, (data['processor_id'], data['motherboard_model'], data['ram_type'], data['ram_size'], data['socket_type'], id))
                conn.commit()
            return redirect(url_for('config'))
    with get_db_connection() as conn:
        config = conn.execute("SELECT id, processor_id, motherboard_model, ram_type, ram_size, socket_type FROM config WHERE id = ?", (id,)).fetchone()
        processors = conn.execute("SELECT id, model_name FROM processors").fetchall()
    return render_template('edit_config.html', config=config, processors=processors, errors=errors)

# Тесты производительности
@app.route('/performance', methods=['GET', 'POST'])
def performance():
    errors = []
    if request.method == 'POST':
        data = {
            'processor_id': request.form['processor_id'],
            'single_core_score': request.form['single_core_score'],
            'multi_core_score': request.form['multi_core_score'],
            'power_consumption': request.form['power_consumption'],
            'temperature': request.form['temperature'],
            'test_duration': request.form['test_duration'],
            'test_stand_info': request.form['test_stand_info'],
            'ram_used': request.form['ram_used'],
            'storage_used': request.form['storage_used'],
            'gpu_used': request.form['gpu_used'],
            'cooling_system': request.form['cooling_system']
        }
        errors = validate_data(data, VALIDATION_RULES['performance_tests'])
        if not errors:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO performance_tests (processor_id, single_core_score, multi_core_score, power_consumption, temperature,
                                                   test_duration, test_stand_info, ram_used, storage_used, gpu_used, cooling_system)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (data['processor_id'], data['single_core_score'], data['multi_core_score'], data['power_consumption'], 
                      data['temperature'], data['test_duration'], data['test_stand_info'], data['ram_used'], 
                      data['storage_used'], data['gpu_used'], data['cooling_system']))
                conn.commit()
    with get_db_connection() as conn:
        tests = conn.execute("""
            SELECT id, processor_id, single_core_score, multi_core_score, power_consumption, temperature, 
                   test_duration, test_stand_info, ram_used, storage_used, gpu_used, cooling_system 
            FROM performance_tests 
            ORDER BY id
        """).fetchall()
        processors = conn.execute("SELECT id, model_name FROM processors").fetchall()
    return render_template('performance.html', tests=tests, processors=processors, errors=errors)

@app.route('/edit_performance/<int:id>', methods=['GET', 'POST'])
def edit_performance(id):
    errors = []
    if request.method == 'POST':
        data = {
            'processor_id': request.form['processor_id'],
            'single_core_score': request.form['single_core_score'],
            'multi_core_score': request.form['multi_core_score'],
            'power_consumption': request.form['power_consumption'],
            'temperature': request.form['temperature'],
            'test_duration': request.form['test_duration'],
            'test_stand_info': request.form['test_stand_info'],
            'ram_used': request.form['ram_used'],
            'storage_used': request.form['storage_used'],
            'gpu_used': request.form['gpu_used'],
            'cooling_system': request.form['cooling_system']
        }
        errors = validate_data(data, VALIDATION_RULES['performance_tests'])
        if not errors:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE performance_tests 
                    SET processor_id = ?, single_core_score = ?, multi_core_score = ?, power_consumption = ?, temperature = ?,
                        test_duration = ?, test_stand_info = ?, ram_used = ?, storage_used = ?, gpu_used = ?, cooling_system = ?
                    WHERE id = ?
                """, (data['processor_id'], data['single_core_score'], data['multi_core_score'], data['power_consumption'], 
                      data['temperature'], data['test_duration'], data['test_stand_info'], data['ram_used'], 
                      data['storage_used'], data['gpu_used'], data['cooling_system'], id))
                conn.commit()
            return redirect(url_for('performance'))
    with get_db_connection() as conn:
        test = conn.execute("""
            SELECT id, processor_id, single_core_score, multi_core_score, power_consumption, temperature, 
                   test_duration, test_stand_info, ram_used, storage_used, gpu_used, cooling_system 
            FROM performance_tests 
            WHERE id = ?
        """, (id,)).fetchone()
        processors = conn.execute("SELECT id, model_name FROM processors").fetchall()
    return render_template('edit_performance.html', test=test, processors=processors, errors=errors)

# Статистика
@app.route('/stats')
def stats():
    with get_db_connection() as conn:
        by_manufacturer = conn.execute("""
            SELECT m.company_name, COUNT(p.id) AS processor_count 
            FROM processors p 
            JOIN manufacturers m ON p.manufacturer_id = m.id 
            GROUP BY m.company_name
        """).fetchall()
        by_motherboard = conn.execute("""
            SELECT c.motherboard_model, COUNT(p.id) AS processor_count 
            FROM processors p 
            JOIN config c ON p.config_id = c.id 
            GROUP BY c.motherboard_model
        """).fetchall()
    return render_template('stats.html', by_manufacturer=by_manufacturer, by_motherboard=by_motherboard)

# Запросы
@app.route('/queries', methods=['GET', 'POST'])
def queries():
    attributes = {
        'model_name': {'table': 'p', 'column': 'model_name', 'type': 'text', 'label': 'Название модели'},
        'release_year': {'table': 'p', 'column': 'release_year', 'type': 'number', 'label': 'Год выпуска'},
        'cores': {'table': 'p', 'column': 'cores', 'type': 'number', 'label': 'Количество ядер'},
        'threads': {'table': 'p', 'column': 'threads', 'type': 'number', 'label': 'Количество потоков'},
        'base_clock': {'table': 'p', 'column': 'base_clock', 'type': 'float', 'label': 'Базовая частота (GHz)'},
        'max_clock': {'table': 'p', 'column': 'max_clock', 'type': 'float', 'label': 'Макс. частота (GHz)'},
        'tdp': {'table': 'p', 'column': 'tdp', 'type': 'number', 'label': 'Тепловыделение (Вт)'},
        'company_name': {'table': 'm', 'column': 'company_name', 'type': 'text', 'label': 'Производитель'},
        'country': {'table': 'm', 'column': 'country', 'type': 'text', 'label': 'Страна'},
        'founded_year': {'table': 'm', 'column': 'founded_year', 'type': 'number', 'label': 'Год основания'},
        'employees': {'table': 'm', 'column': 'employees', 'type': 'number', 'label': 'Количество сотрудников'},
        'motherboard_model': {'table': 'conf', 'column': 'motherboard_model', 'type': 'text', 'label': 'Модель материнской платы'},
        'ram_type': {'table': 'conf', 'column': 'ram_type', 'type': 'text', 'label': 'Тип RAM'},
        'ram_size': {'table': 'conf', 'column': 'ram_size', 'type': 'number', 'label': 'Объем RAM (ГБ)'},
        'socket_type': {'table': 'conf', 'column': 'socket_type', 'type': 'text', 'label': 'Тип сокета'},
        'single_core_score': {'table': 'pt', 'column': 'single_core_score', 'type': 'number', 'label': 'Однопоточный балл'},
        'multi_core_score': {'table': 'pt', 'column': 'multi_core_score', 'type': 'number', 'label': 'Многопоточный балл'},
        'power_consumption': {'table': 'pt', 'column': 'power_consumption', 'type': 'number', 'label': 'Потребляемая мощность (Вт)'},
        'temperature': {'table': 'pt', 'column': 'temperature', 'type': 'number', 'label': 'Температура (°C)'},
        'test_duration': {'table': 'pt', 'column': 'test_duration', 'type': 'float', 'label': 'Длительность теста (ч)'},
        'test_stand_info': {'table': 'pt', 'column': 'test_stand_info', 'type': 'text', 'label': 'Информация о стенде'},
        'ram_used': {'table': 'pt', 'column': 'ram_used', 'type': 'text', 'label': 'Используемая RAM'},
        'storage_used': {'table': 'pt', 'column': 'storage_used', 'type': 'text', 'label': 'Используемое хранилище'},
        'gpu_used': {'table': 'pt', 'column': 'gpu_used', 'type': 'text', 'label': 'Используемый GPU'},
        'cooling_system': {'table': 'pt', 'column': 'cooling_system', 'type': 'text', 'label': 'Система охлаждения'}
    }
    
    numeric_attributes = [key for key, attr in attributes.items() if attr['type'] in ['number', 'float']]
    
    results = None
    selected_attribute1 = None
    search_min1 = None
    search_max1 = None
    selected_attribute2 = None
    search_min2 = None
    search_max2 = None
    errors = []

    with get_db_connection() as conn:
        countries = conn.execute("SELECT DISTINCT country FROM manufacturers ORDER BY country").fetchall()
        companies = conn.execute("SELECT DISTINCT company_name FROM manufacturers ORDER BY company_name").fetchall()
    countries = [row['country'] for row in countries]
    companies = [row['company_name'] for row in companies]

    if request.method == 'POST':
        selected_attribute1 = request.form.get('attribute1')
        search_min1 = request.form.get('search_min1')
        search_max1 = request.form.get('search_max1') or search_min1
        selected_attribute2 = request.form.get('attribute2')
        search_min2 = request.form.get('search_min2')
        search_max2 = request.form.get('search_max2') or search_min2

        if not selected_attribute1 or selected_attribute1 not in attributes:
            errors.append("Выберите корректный первый атрибут")
        elif not search_min1:
            errors.append("Введите минимальное значение для первого атрибута")
        elif selected_attribute2 and selected_attribute2 not in attributes:
            errors.append("Выберите корректный второй атрибут")
        elif selected_attribute2 and not search_min2:
            errors.append("Введите минимальное значение для второго атрибута")
        else:
            attr_info1 = attributes[selected_attribute1]
            table1 = attr_info1['table']
            column1 = attr_info1['column']
            attr_type1 = attr_info1['type']

            try:
                if attr_type1 in ['number', 'float'] and selected_attribute1 not in ['company_name', 'country']:
                    search_min1 = int(search_min1) if attr_type1 == 'number' else float(search_min1)
                    if search_max1:
                        search_max1 = int(search_max1) if attr_type1 == 'number' else float(search_max1)
                        if search_max1 < search_min1:
                            errors.append(f"Максимальное значение для '{attr_info1['label']}' должно быть больше минимального")
                            raise ValueError
                elif selected_attribute1 not in ['company_name', 'country']:
                    search_max1 = search_min1

                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    query = """
                        SELECT p.id, p.model_name, p.release_year, m.company_name, 
                               p.cores, p.threads, p.base_clock, p.max_clock, p.tdp,
                               m.country, m.founded_year, m.employees,
                               conf.motherboard_model, conf.ram_type, conf.ram_size, conf.socket_type,
                               pt.single_core_score, pt.multi_core_score, pt.power_consumption, 
                               pt.temperature, pt.test_duration, pt.test_stand_info, 
                               pt.ram_used, pt.storage_used, pt.gpu_used, pt.cooling_system
                        FROM processors p
                        JOIN manufacturers m ON p.manufacturer_id = m.id
                        LEFT JOIN config conf ON p.config_id = conf.id
                        LEFT JOIN performance_tests pt ON p.performance_tests_id = pt.id
                        WHERE {table1}.{column1} >= ? AND {table1}.{column1} <= ?
                    """.format(table1=table1, column1=column1)
                    params = [search_min1, search_max1]

                    if selected_attribute2 and search_min2:
                        attr_info2 = attributes[selected_attribute2]
                        table2 = attr_info2['table']
                        column2 = attr_info2['column']
                        attr_type2 = attr_info2['type']

                        if attr_type2 in ['number', 'float'] and selected_attribute2 not in ['company_name', 'country']:
                            search_min2 = int(search_min2) if attr_type2 == 'number' else float(search_min2)
                            if search_max2:
                                search_max2 = int(search_max2) if attr_type2 == 'number' else float(search_max2)
                                if search_max2 < search_min2:
                                    errors.append(f"Максимальное значение для '{attr_info2['label']}' должно быть больше минимального")
                                    raise ValueError
                        elif selected_attribute2 not in ['company_name', 'country']:
                            search_max2 = search_min2

                        query += " AND {table2}.{column2} >= ? AND {table2}.{column2} <= ?".format(table2=table2, column2=column2)
                        params.extend([search_min2, search_max2])

                    results = cursor.execute(query, tuple(params)).fetchall()

            except ValueError:
                if not errors:
                    errors.append(f"Значение для '{attr_info1['label']}' должно быть {'числом' if attr_type1 in ['number', 'float'] else 'текстом'}")
            except sqlite3.OperationalError as e:
                errors.append(f"Ошибка базы данных: {str(e)}")

    return render_template('queries.html', attributes=attributes, results=results, 
                          selected_attribute1=selected_attribute1, search_min1=search_min1, search_max1=search_max1,
                          selected_attribute2=selected_attribute2, search_min2=search_min2, search_max2=search_max2,
                          errors=errors, countries=countries, companies=companies, numeric_attributes=numeric_attributes)

# Подробный режим добавления процессора
@app.route('/add_detailed', methods=['GET', 'POST'])
def add_detailed():
    errors = []
    with get_db_connection() as conn:
        companies = [row['company_name'] for row in conn.execute("SELECT company_name FROM manufacturers ORDER BY company_name").fetchall()]

    if request.method == 'POST':
        processor_data = {
            'model_name': request.form.get('model_name', '').strip(),
            'release_year': request.form.get('release_year', '').strip(),
            'cores': request.form.get('cores', ''),
            'threads': request.form.get('threads', ''),
            'base_clock': request.form.get('base_clock', ''),
            'max_clock': request.form.get('max_clock', ''),
            'tdp': request.form.get('tdp', '')
        }
        company_name = request.form.get('company_name')
        config_data = {
            'motherboard_model': request.form.get('motherboard_model', ''),
            'ram_type': request.form.get('ram_type', ''),
            'ram_size': request.form.get('ram_size', ''),
            'socket_type': request.form.get('socket_type', '')
        }
        perf_data = {
            'single_core_score': request.form.get('single_core_score', ''),
            'multi_core_score': request.form.get('multi_core_score', ''),
            'power_consumption': request.form.get('power_consumption', ''),
            'temperature': request.form.get('temperature', ''),
            'test_duration': request.form.get('test_duration', ''),
            'test_stand_info': request.form.get('test_stand_info', ''),
            'ram_used': request.form.get('ram_used', ''),
            'storage_used': request.form.get('storage_used', ''),
            'gpu_used': request.form.get('gpu_used', ''),
            'cooling_system': request.form.get('cooling_system', '')
        }

        if not all([processor_data['model_name'], processor_data['release_year'], company_name]):
            errors.append("Обязательные поля для процессора должны быть заполнены")
        elif company_name not in companies:
            errors.append("Выберите существующего производителя из списка")
        else:
            errors.extend(validate_data(processor_data, VALIDATION_RULES['processors']))
            errors.extend(validate_data(config_data, VALIDATION_RULES['config']))
            errors.extend(validate_data(perf_data, VALIDATION_RULES['performance_tests']))

            if not errors:
                try:
                    release_year = int(processor_data['release_year']) if processor_data['release_year'] else None
                    cores = int(processor_data['cores']) if processor_data['cores'] else None
                    threads = int(processor_data['threads']) if processor_data['threads'] else None
                    base_clock = float(processor_data['base_clock']) if processor_data['base_clock'] else None
                    max_clock = float(processor_data['max_clock']) if processor_data['max_clock'] else None
                    tdp = int(processor_data['tdp']) if processor_data['tdp'] else None
                    ram_size = int(config_data['ram_size']) if config_data['ram_size'] else None
                    single_core_score = int(perf_data['single_core_score']) if perf_data['single_core_score'] else None
                    multi_core_score = int(perf_data['multi_core_score']) if perf_data['multi_core_score'] else None
                    power_consumption = int(perf_data['power_consumption']) if perf_data['power_consumption'] else None
                    temperature = int(perf_data['temperature']) if perf_data['temperature'] else None
                    test_duration = float(perf_data['test_duration']) if perf_data['test_duration'] else None

                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT id FROM manufacturers WHERE company_name = ?", (company_name,))
                        manufacturer_id = cursor.fetchone()['id']

                        cursor.execute("""
                            INSERT INTO config (motherboard_model, ram_type, ram_size, socket_type)
                            VALUES (?, ?, ?, ?)
                        """, (config_data['motherboard_model'], config_data['ram_type'], ram_size, config_data['socket_type']))
                        config_id = cursor.lastrowid

                        cursor.execute("""
                            INSERT INTO performance_tests (single_core_score, multi_core_score, power_consumption, temperature,
                                                           test_duration, test_stand_info, ram_used, storage_used, gpu_used, cooling_system)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (single_core_score, multi_core_score, power_consumption, temperature, test_duration,
                              perf_data['test_stand_info'], perf_data['ram_used'], perf_data['storage_used'], 
                              perf_data['gpu_used'], perf_data['cooling_system']))
                        performance_tests_id = cursor.lastrowid

                        cursor.execute("""
                            INSERT INTO processors (model_name, release_year, manufacturer_id, cores, threads, base_clock, max_clock, tdp, config_id, performance_tests_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (processor_data['model_name'], release_year, manufacturer_id, cores, threads, base_clock, max_clock, tdp, config_id, performance_tests_id))
                        conn.commit()
                    return redirect(url_for('view'))
                except ValueError:
                    errors.append("Все числовые поля должны содержать корректные значения (целые или дробные числа)")
                except sqlite3.IntegrityError:
                    errors.append("Ошибка: такой процессор уже существует")

    return render_template('add_detailed.html', errors=errors, companies=companies)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)