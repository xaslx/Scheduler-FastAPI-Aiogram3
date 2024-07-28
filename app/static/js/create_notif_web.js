document.addEventListener('DOMContentLoaded', function() {
    console.log('Document loaded, initializing CKEditor...');

    CKEDITOR.replace('editor-container');

    const form = document.getElementById('notification-form');

    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        console.log('Form submission prevented.');

        const description = CKEDITOR.instances['editor-container'].getData();
        console.log('Description from CKEditor:', description);

        if (description.length < 15 || description.length > 500) {
            document.getElementById('description-error').textContent = 'Описание должно быть от 15 до 500 символов.';
            console.log('Description length error.');
            return;
        } else {
            document.getElementById('description-error').textContent = '';
        }

        const title = form.querySelector('#title').value;
        if (title.length < 5 || title.length > 60) {
            document.getElementById('title-error').textContent = 'Заголовок должен быть от 5 до 60 символов.';
            console.log('Title length error.');
            return;
        } else {
            document.getElementById('title-error').textContent = '';
        }

        const hiddenDescriptionField = document.getElementById('description');
        hiddenDescriptionField.value = description;

        const requestData = {
            title: title,
            description: description
        };
        console.log('Request data:', requestData);

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
            console.log('Response data:', responseData);
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
