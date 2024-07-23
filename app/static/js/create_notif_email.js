document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registration-form');

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(form);
        const message = formData.get('message');

        fetch('/notification/send_notification_email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Notification sent:', data);

            Swal.fire({
                icon: 'success',
                title: 'Уведомление отправлено',
                text: `Количество пользователей, которые получат уведомление: ${data.user_count}`,
                showConfirmButton: true,
                customClass: {
                    container: 'swal2-custom',
                    popup: 'swal2-custom-popup',
                    title: 'swal2-custom-title',
                    content: 'swal2-custom-content'
                }
            });
        })
        .catch(error => {
            console.error('Error sending notification:', error);
            Swal.fire({
                icon: 'error',
                title: 'Ошибка',
                text: 'Произошла ошибка при отправке уведомления.',
                showConfirmButton: true,
                customClass: {
                    container: 'swal2-custom',
                    popup: 'swal2-custom-popup',
                    title: 'swal2-custom-title',
                    content: 'swal2-custom-content'
                }
            });
        });
    });
});