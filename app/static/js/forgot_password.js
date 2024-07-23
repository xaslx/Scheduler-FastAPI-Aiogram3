document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('reset-password-form');
    const emailInput = document.getElementById('email');
    const emailError = document.getElementById('email-error');
    const successMessage = document.getElementById('success-message');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        emailError.textContent = '';

        const email = emailInput.value;

        fetch('/user/forgot_password/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        })
        .then(response => {
            if (!response.ok) {
                throw Error(response.statusText);
            }
            form.style.display = 'none';
            successMessage.style.display = 'block';
        })
        .catch(error => {
            if (error.message.includes('422')) {
                emailError.textContent = 'Email не найден.';
            } else {
                emailError.textContent = 'Email не найден.';
            }
            setTimeout(function() {
                emailError.textContent = '';
            }, 3000);
        });
    });
});