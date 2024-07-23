document.addEventListener('DOMContentLoaded', function() {
    var passwordInput = document.getElementById('password');
    var togglePassword = document.getElementById('toggle-password');

    togglePassword.addEventListener('click', function() {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
        } else {
            passwordInput.type = 'password';
        }
    });

    document.getElementById('registration-form').addEventListener('submit', function(event) {
        event.preventDefault();
        var formData = {
            'email': document.getElementById('email').value.trim(),
            'password': document.getElementById('password').value.trim(),
        };

        fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Unauthorized');
            }
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            window.location.href = '/';
        })
        .catch(error => {
            var loginErrorElement = document.getElementById('login-error');
            loginErrorElement.innerText = 'Неверный email/пароль.';
            loginErrorElement.style.display = 'block';
            console.error('Error:', error);
            setTimeout(function() {
                loginErrorElement.style.display = 'none';
            }, 2000);
        });
    });
});