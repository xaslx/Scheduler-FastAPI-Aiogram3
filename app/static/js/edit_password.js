function validatePassword(password) {
    return /^[A-Za-z0-9_-]{6,30}$/.test(password);
}

document.getElementById('registration-form').addEventListener('submit', function(event) {
    event.preventDefault();

    var newPassword = document.getElementById('new-password').value;
    var confirmPassword = document.getElementById('confirm-password').value;
    var errorElement = document.getElementById('password-error');
    var validationErrorElement = document.getElementById('password-validation-error');

    if (!validatePassword(newPassword)) {
        validationErrorElement.style.display = 'block';
        setTimeout(function() {
            validationErrorElement.style.display = 'none';
        }, 2000);
        return;
    }

    if (newPassword !== confirmPassword) {
        errorElement.style.display = 'block';
        setTimeout(function() {
            errorElement.style.display = 'none';
        }, 2000);
    } else {
        var userId = document.getElementById('user-id').value;
        var email = document.getElementById('user-email').value;
        var data = {
            user_id: userId,
            email: email,
            new_password: newPassword,
            repeat_password: confirmPassword
        };

        fetch('/user/edit_password', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка при изменении пароля');
            }

            Swal.fire({
                icon: 'success',
                title: 'Пароль изменен!',
                showConfirmButton: false,
                timer: 1500,
                customClass: {
                    popup: 'custom-swal',
                    title: 'custom-swal-title',
                    content: 'custom-swal-content'
                },
                width: '80%',
            });

            setTimeout(() => {
                location.reload();
            }, 2000);
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при изменении пароля');
        });
    }
});

var togglePassword = document.getElementById('toggle-password');
var togglePasswordConfirm = document.getElementById('toggle-password-confirm');
var newPasswordInput = document.getElementById('new-password');
var confirmPasswordInput = document.getElementById('confirm-password');

togglePassword.addEventListener('click', function() {
    var type = newPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    newPasswordInput.setAttribute('type', type);
    this.textContent = type === 'password' ? 'Показать пароль' : 'Скрыть пароль';
});

togglePasswordConfirm.addEventListener('click', function() {
    var type = confirmPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    confirmPasswordInput.setAttribute('type', type);
    this.textContent = type === 'password' ? 'Показать пароль' : 'Скрыть пароль';
});