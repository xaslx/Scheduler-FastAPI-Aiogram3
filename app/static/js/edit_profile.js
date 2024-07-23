document.addEventListener('DOMContentLoaded', function() {
    function validateName(name) {
        return /^[A-Za-zА-Яа-яЁё]{2,15}$/.test(name);
    }

    function validateSurname(surname) {
        return /^[A-Za-zА-Яа-яЁё]{2,15}$/.test(surname);
    }

    function validateTelegramLink(link) {
        return /^[A-Za-z0-9_]{5,15}$/.test(link);
    }

    function clearErrors() {
        document.querySelectorAll('.error-message').forEach(el => {
            el.textContent = '';
            el.classList.remove('fade-out');
        });
    }

    function showError(id, message) {
        var errorElement = document.getElementById(id);
        errorElement.textContent = message;
        errorElement.classList.add('show');

        setTimeout(function() {
            errorElement.classList.remove('show');
            setTimeout(function() {
                errorElement.textContent = '';
            }, 500);
        }, 2000);
    }

    document.getElementById('registration-form').addEventListener('submit', async function(event) {
        event.preventDefault();
        clearErrors();

        var name = document.getElementById('name').value.trim();
        var surname = document.getElementById('surname').value.trim();
        var telegramLink = document.getElementById('telegram_link').value.trim();
        var description = document.getElementById('description').value.trim();

        var valid = true;

        if (!validateName(name)) {
            showError('name-error', 'Имя должно содержать от 2 до 15 букв и не может содержать пробелы.');
            valid = false;
        }

        if (!validateSurname(surname)) {
            showError('surname-error', 'Фамилия должна содержать от 2 до 15 букв и не может содержать пробелы.');
            valid = false;
        }

        if (telegramLink && !validateTelegramLink(telegramLink)) {
            showError('telegram-link-error', 'Имя пользователя в телеграм должно содержать только [англ.букв, цифры 0-9, знак _], быть минимум 4 символа и не должно превышать 15 символов.');
            valid = false;
        }

        if (valid) {
            var formData = {
                'name': name,
                'surname': surname,
                'telegram_link': telegramLink || null,
                'description': description
            };

            try {
                const response = await fetch('/user/edit_profile', {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData),
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }

                const data = await response.json();
                console.log('Success:', data);

                window.location.href = "{{ url_for('myprofile:page') }}";
            } catch (error) {
                console.error('Error:', error);
            }
        }
    });
});