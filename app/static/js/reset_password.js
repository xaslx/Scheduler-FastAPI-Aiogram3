document.getElementById('reset-password-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const userId = document.getElementById('user-id').value;
    const userEmail = document.getElementById('user-email').value;

    try {
        const response = await fetch('/user/forgot_password/reset', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: parseInt(userId, 10), email: userEmail })
        });

        if (response.ok) {
            window.location.href = '/user/reset/success_update_password';
        } else {
            const errorData = await response.json();
            console.error('Ошибка сброса пароля:', errorData);
            alert('Ошибка сброса пароля.');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка сброса пароля.');
    }
});