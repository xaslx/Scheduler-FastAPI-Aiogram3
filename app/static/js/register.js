document.addEventListener('DOMContentLoaded', function() {
    var passwordInput = document.getElementById('password');
    var togglePassword = document.getElementById('toggle-password');
    var form = document.getElementById('registration-form');

    togglePassword.addEventListener('click', function() {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
        } else {
            passwordInput.type = 'password';
        }
    });

    function validateName(name) {
        return /^[A-Za-zА-Яа-яЁё]{2,15}$/.test(name);
    }

    function validateSurname(surname) {
        return /^[A-Za-zА-Яа-яЁё]{2,15}$/.test(surname);
    }

    function validatePassword(password) {
        return /^[A-Za-z0-9_-]{6,30}$/.test(password);
    }

    function validateTelegramLink(link) {
        return /^[A-Za-z0-9_]{4,15}$/.test(link);
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

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        clearErrors();

        var name = document.getElementById('name').value.trim();
        var surname = document.getElementById('surname').value.trim();
        var email = document.getElementById('email').value.trim();
        var password = document.getElementById('password').value.trim();
        var telegramLink = document.getElementById('telegram_link').value.trim();

        var valid = true;

        if (!validateName(name)) {
            showError('name-error', 'Имя должно содержать от 2 до 15 букв и не может содержать пробелы.');
            valid = false;
        }

        if (!validateSurname(surname)) {
            showError('surname-error', 'Фамилия должна содержать от 2 до 15 букв и не может содержать пробелы.');
            valid = false;
        }

        if (!validatePassword(password)) {
            showError('password-error', 'Пароль должен содержать только [англ.букв, цифры 0-9, знак _ -], быть минимум 6 символов и не должен превышать 30 символов.');
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
                'email': email,
                'password': password,
                'telegram_link': telegramLink || null
            };

            fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            })
            .then(response => {
                console.log('Response status:', response.status);
                return response.json().then(data => {
                    console.log('Response data:', data);
                    if (response.ok) {
                        window.location.href = '/auth/after_register';
                    } else {
                        showError('email-error', data.detail || 'Пользователь с таким email уже существует.');
                    }
                });
            })
            .catch(error => {
                console.error('Fetch error:', error);
            });
        }
    });
});