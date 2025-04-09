let currentLevel = '';

function updateAttributes() {
    const table = document.getElementById('table').value;
    fetch('/get_attributes?table=' + table)
        .then(response => response.json())
        .then(data => {
            const firstAttrSelect = document.getElementById('first_attribute');
            firstAttrSelect.innerHTML = '<option value="">-- Выберите атрибут --</option>';
            Object.keys(data).forEach(attr => {
                const option = document.createElement('option');
                option.value = attr;
                option.text = data[attr].label;
                firstAttrSelect.appendChild(option);
            });
            updateFirstValues();
        });
}

function updateFirstValues() {
    const table = document.getElementById('table').value;
    const attribute = document.getElementById('first_attribute').value;
    if (table && attribute) {
        fetch('/get_values?table=' + table + '&attribute=' + attribute)
            .then(response => response.json())
            .then(data => {
                const valueSelect = document.getElementById('first_value');
                valueSelect.innerHTML = '<option value="">-- Выберите значение --</option>';
                data.forEach(val => {
                    const option = document.createElement('option');
                    option.value = val;
                    option.text = val;
                    valueSelect.appendChild(option);
                });
                updateSecondAttributes();
            });
    }
}

function updateSecondAttributes() {
    const table = document.getElementById('table1').value;
    const firstAttr = document.getElementById('first_attribute').value;
    fetch('/get_attributes?table=' + table)
        .then(response => response.json())
        .then(data => {
            const secondAttrSelect = document.getElementById('second_attribute');
            secondAttrSelect.innerHTML = '<option value="">-- Выберите атрибут --</option>';
            Object.keys(data).forEach(attr => {
                if (attr !== firstAttr) {
                    const option = document.createElement('option');
                    option.value = attr;
                    option.text = data[attr].label;
                    secondAttrSelect.appendChild(option);
                }
            });
            updateSecondValues();
        });
}

function updateSecondValues() {
    const table0 = document.getElementById('table').value;  // Первая таблица
    const table1 = document.getElementById('table1').value; // Вторая таблица
    const firstAttr = document.getElementById('first_attribute').value;
    const firstValue = document.getElementById('first_value').value;
    const secondAttr = document.getElementById('second_attribute').value;

    if (table0 && firstAttr && firstValue && secondAttr) {  // Условие: первая таблица и атрибуты обязательны
        const url = table1
            ? `/get_filtered_values?table0=${table0}&table1=${table1}&first_attr=${firstAttr}&first_value=${firstValue}&second_attr=${secondAttr}`
            : `/get_filtered_values?table0=${table0}&first_attr=${firstAttr}&first_value=${firstValue}&second_attr=${secondAttr}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                const valueSelect = document.getElementById('second_value');
                valueSelect.innerHTML = '<option value="">-- Выберите значение --</option>';
                if (data.error) {
                    console.error('Ошибка от сервера:', data.error);
                } else {
                    data.forEach(val => {
                        const option = document.createElement('option');
                        option.value = val;
                        option.text = val;
                        valueSelect.appendChild(option);
                    });
                }
            })
            .catch(error => console.error('Ошибка:', error));
    }
}

function showAddForm(level) {
    currentLevel = level;
    document.getElementById('add_form').style.display = 'block';
}

function addValue() {
    const table = document.getElementById('table').value;
    const attribute = document.getElementById(currentLevel === 'first' ? 'first_attribute' : 'second_attribute').value;
    const newValue = document.getElementById('new_value').value;
    fetch('/add_value', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ table: table, attribute: attribute, value: newValue })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (currentLevel === 'first') updateFirstValues();
            else updateSecondValues();
            document.getElementById('add_form').style.display = 'none';
            document.getElementById('new_value').value = '';
        } else {
            alert('Ошибка при добавлении значения');
        }
    });
}
function updateAttributes2() {
    var table1 = document.getElementById('table1').value;
    var secondAttrSelect = document.getElementById('second_attribute');
    secondAttrSelect.innerHTML = '<option value="">-- Выберите атрибут --</option>';

    if (table1) {
        fetch('/get_attributes?table=' + table1)
            .then(response => response.json())
            .then(data => {
                for (var attr in data) {
                    var option = document.createElement('option');
                    option.value = attr;
                    option.text = data[attr].label;
                    secondAttrSelect.appendChild(option);
                }
            })
            .catch(error => console.error('Ошибка:', error));
    }
}
