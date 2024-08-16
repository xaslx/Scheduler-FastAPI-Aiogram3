function showConfirmation(time) {
    document.getElementById('confirmTime').innerText = time;
    document.getElementById('customConfirmationModal').style.display = 'flex';
}

function hideConfirmation() {
    document.getElementById('customConfirmationModal').style.display = 'none';
}

async function confirmSelection() {
    const bookingId = document.getElementById('bookingId').value;
    const selectedTime = document.getElementById('confirmTime').innerText;
    const name = document.getElementById('userName').value;
    const email = document.getElementById('userEmail').value;
    const phone = document.getElementById('userPhone').value;
    const telegram = document.getElementById('userTelegram').value || null;

    const nameError = document.getElementById('nameError');
    if (!name || name.length < 2 || name.length > 20 || /\s/.test(name)) {
        nameError.style.display = 'block';
        setTimeout(() => {
            nameError.style.display = 'none';
        }, 2000);
        return;
    }

    if (!phone) {
        Swal.fire({
            icon: 'error',
            title: 'Ошибка!',
            text: 'Пожалуйста, укажите ваш телефон.',
        });
        return;
    }

    if (!/^\d+$/.test(phone)) {
        const phoneError = document.getElementById('phoneError');
        phoneError.style.display = 'block';
        setTimeout(() => {
            phoneError.style.display = 'none';
        }, 3000);
        return;
    }

    if (!email) {
        Swal.fire({
            icon: 'error',
            title: 'Ошибка!',
            text: 'Пожалуйста, укажите ваш email.',
        });
        return;
    }

    if (telegram && (!/^\d{5,15}$/.test(telegram))) {
        Swal.fire({
            icon: 'error',
            title: 'Ошибка!',
            text: 'Telegram ID должен содержать только цифры и быть длиной от 5 до 15 символов.',
        });
        return;
    }

    const data = {
        time: selectedTime,
        name: name,
        email: email,
        phone_number: phone,
        tg: telegram
    };

    try {
        const response = await fetch(`/booking/select_booking/${bookingId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Failed to update booking');
        }

        Swal.fire({
            icon: 'success',
            title: 'Успех!',
            text: 'Вы успешно сделали запись.',
            timer: 2000,
            showConfirmButton: false,
            onClose: () => {
                reloadPage();
            }
        });

        hideConfirmation();

    } catch (error) {
        console.error('Error updating booking:', error.message);

        Swal.fire({
            icon: 'error',
            title: 'Ошибка!',
            text: 'Не удалось сделать запись, возможно выбранное время уже недоступно.',
        });
    }
}

function reloadPage() {
    window.location.reload();
}

function showUnavailableNotification(time) {
    Swal.fire({
        icon: 'info',
        title: 'Внимание!',
        text: `Выбранное время (${time}) недоступно для записи.`,
    });
}
function getTelegramId() {
    const telegramInput = document.getElementById('userTelegram');
    telegramInput.disabled = false;

    telegramInput.value = '';
    telegramInput.placeholder = 'Вставьте сюда ваш Telegram ID';

    window.open('https://t.me/test_fast_shop_bot', '_blank');
}
