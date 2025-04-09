let currentLevel = '';

function updateFirstAttributes() {
    const table = document.getElementById('table').value;
    fetch('/get_attributes?table=' + table)
        .then(response => response.json())
        .then(data => {
            const firstAttrSelect = document.getElementById('first_attribute');
            firstAttrSelect.innerHTML = '';
            data.forEach(attr => {
                const option = document.createElement('option');
                option.value = attr;
                option.text = attr;
                firstAttrSelect.appendChild(option);
            });
            updateValues();
        });
}

function updateValues() {
    const table = document.getElementById('table').value;
    const attribute = document.getElementById('first_attribute').value;
    fetch('/get_values?table=' + table + '&attribute=' + attribute)
        .then(response => response.json())
        .then(data => {
            const valueSelect = document.getElementById('first_value');
            valueSelect.innerHTML = '';
            data.forEach(val => {
                const option = document.createElement('option');
                option.value = val;
                option.text = val;
                valueSelect.appendChild(option);
            });
            updateSecondAttributes();
        });
}

function updateSecondAttributes() {
    const table = document.getElementById('table').value;
    fetch('/get_attributes?table=' + table)
        .then(response => response.json())
        .then(data => {
            const secondAttrSelect = document.getElementById('second_attribute');
            secondAttrSelect.innerHTML = '';
            data.forEach(attr => {
                if (attr !== document.getElementById('first_attribute').value) {
                    const option = document.createElement('option');
                    option.value = attr;
                    option.text = attr;
                    secondAttrSelect.appendChild(option);
                }
            });
            updateSecondValues();
        });
}

function updateSecondValues() {
    const table = document.getElementById('table').value;
    const firstAttr = document.getElementById('first_attribute').value;
    const firstValue = document.getElementById('first_value').value;
    const secondAttr = document.getElementById('second_attribute').value;
    fetch('/get_filtered_values?table=' + table + '&first_attr=' + firstAttr + 
          '&first_value=' + firstValue + '&second_attr=' + secondAttr)
        .then(response => response.json())
        .then(data => {
            const valueSelect = document.getElementById('second_value');
            valueSelect.innerHTML = '';
            data.forEach(val => {
                const option = document.createElement('option');
                option.value = val;
                option.text = val;
                valueSelect.appendChild(option);
            });
        });
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
            if (currentLevel === 'first') updateValues();
            else updateSecondValues();
            document.getElementById('add_form').style.display = 'none';
            document.getElementById('new_value').value = '';
        } else {
            alert('Ошибка при добавлении значения');
        }
    });
}
