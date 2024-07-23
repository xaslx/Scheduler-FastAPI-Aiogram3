document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('notification-form');
    
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const formData = new FormData(form);
        const requestData = {
            title: formData.get('title'),
            description: formData.get('description')
        };
        
        try {
            const response = await fetch('/notification/create_notification_for_website', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData),
            });

            if (!response.ok) {
                throw new Error('Failed to create notification');
            }

            const responseData = await response.json();
            Swal.fire({
                icon: 'success',
                title: 'Уведомление создано успешно!',
                showConfirmButton: false,
                timer: 1500
            }).then(() => {
                window.location.reload();
            });
        } catch (error) {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Ошибка',
                text: 'Не удалось создать уведомление',
            });
        }
    });
});