document.getElementById('helpForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const form = event.target;
    const description = form.description.value;

    if (description.length < 10 || description.length > 500) {
        Swal.fire({
            title: 'Ошибка!',
            text: 'Описание должно быть не менее 10 и не более 500 символов.',
            icon: 'error',
            timer: 2000,
            showConfirmButton: false,
            customClass: {
                popup: 'swal2-popup-red'
            }
        });
        return;
    }

    const formData = new FormData(form);

    const data = {
        email: formData.get('email'),
        description: formData.get('description')
    };

    try {
        const response = await fetch('/help', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (response.ok) {
            Swal.fire({
                title: 'Успешно!',
                text: 'Ваш запрос был успешно отправлен.',
                icon: 'success',
                confirmButtonText: 'OK'
            });
            form.reset();
        } else {
            const result = await response.json();
            Swal.fire({
                title: 'Ошибка!',
                text: result.detail || 'Произошла ошибка при отправке формы.',
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
    } catch (error) {
        Swal.fire({
            title: 'Ошибка!',
            text: 'Произошла ошибка при отправке формы.',
            icon: 'error',
            confirmButtonText: 'OK'
        });
    }
});