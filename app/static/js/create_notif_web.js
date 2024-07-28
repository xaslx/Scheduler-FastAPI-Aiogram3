document.addEventListener('DOMContentLoaded', function() {
    var quill = new Quill('#editor-container', {
        theme: 'snow'
    });


    const form = document.getElementById('notification-form');

    form.addEventListener('submit', async function(event) {
        event.preventDefault();
    

        const description = quill.root.innerHTML;
    

        if (description.length < 15 || description.length > 500) {
            document.getElementById('description-error').textContent = 'Описание должно быть от 15 до 500 символов.';

            return;
        } else {
            document.getElementById('description-error').textContent = '';
        }

        const title = form.querySelector('#title').value;
        if (title.length < 5 || title.length > 60) {
            document.getElementById('title-error').textContent = 'Заголовок должен быть от 5 до 60 символов.';

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
