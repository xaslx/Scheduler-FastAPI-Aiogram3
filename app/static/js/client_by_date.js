document.addEventListener("DOMContentLoaded", function() {
    const cancelButtons = document.querySelectorAll(".custom-cancel-button");
    const modal = document.getElementById("cancel-modal");
    const closeModalButton = document.querySelector(".close");
    const confirmCancelButton = document.getElementById("confirm-cancel");
    const cancelCancelButton = document.getElementById("cancel-cancel");
    const date = document.getElementById('booking-date').value;
    let currentButton;

    cancelButtons.forEach(button => {
        button.addEventListener("click", function() {
            currentButton = this;
            modal.style.display = "block";
        });
    });

    closeModalButton.addEventListener("click", function() {
        modal.style.display = "none";
    });

    cancelCancelButton.addEventListener("click", function() {
        modal.style.display = "none";
    });

    confirmCancelButton.addEventListener("click", function() {
        const reason = document.getElementById("cancel-reason").value;
        if (reason.length < 10 || reason.length > 200) {
            alert("Причина отмены должна быть от 10 до 200 символов.");
            return;
        }
        
        const time = currentButton.dataset.time;
        const email = currentButton.dataset.email;
        const bookingId = currentButton.dataset.id;

        console.log({ date: date, time: time, email: email, description: reason });
        
        fetch(`/booking/cancel_booking?booking_id=${bookingId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ date: date, time: time, email: email, description: reason })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Ошибка при отмене записи');
            }
        })
        .then(data => {
            alert('Запись успешно отменена');
            modal.style.display = "none";
            currentButton.closest(".custom-booking-block").remove();
        })
        .catch(error => {
            alert(error.message);
        });
    });
});