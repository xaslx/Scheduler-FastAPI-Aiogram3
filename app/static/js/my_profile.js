document.addEventListener('DOMContentLoaded', function() {
    const editButton = document.querySelector('.edit-description-button');
    const descriptionForm = document.querySelector('.description-form');
    const confirmDeleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));

    editButton.addEventListener('click', function(e) {
        e.preventDefault();
        editButton.style.display = 'none';
        descriptionForm.style.display = 'block';
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const deleteButton = document.querySelector('.delete_profile');
    const modal = document.getElementById('confirmDeleteModal');
    const closeBtn = document.querySelector('.close');
    const cancelBtn = document.getElementById('cancelDelete');
    const confirmBtn = document.getElementById('confirmDelete');

    deleteButton.addEventListener('click', function() {
        modal.style.display = 'block';
    });

    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    cancelBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    confirmBtn.addEventListener('click', async function() {
        const userId = document.getElementById('userIdInput').value;
        try {
            const response = await fetch(`/user/delete_user/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) {
                throw new Error('Ошибка удаления пользователя');
            }
            location.reload();
        } catch (error) {
            console.error('Ошибка при удалении пользователя:', error);
        } finally {
            modal.style.display = 'none';
        }
    });

    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });
});

function copyToClipboard(selector) {
    const el = document.querySelector(selector);
    const tempInput = document.createElement('input');
    tempInput.value = el.tagName === 'A' ? el.href : el.innerText;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);
}
document.addEventListener('DOMContentLoaded', function() {
    var modalTg = document.getElementById("bindTelegramModal-tg");
    var btnOpenTg = document.querySelector('.add-tg-button[data-bs-target="#bindTelegramModal-tg"]');
    var btnCloseTg = document.getElementById("closeBindModal-tg");
    var spanCloseTg = document.getElementsByClassName("close-tg")[0];

    btnOpenTg.onclick = function() {
        modalTg.style.display = "block";
    }

    btnCloseTg.onclick = function() {
        modalTg.style.display = "none";
    }

    spanCloseTg.onclick = function() {
        modalTg.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modalTg) {
            modalTg.style.display = "none";
        }
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const confirmUnlinkModal = document.getElementById('confirmUnlinkModal');
    const openModalBtn = document.querySelector('[data-bs-target="#confirmUnlinkModal"]');
    const closeModalBtn = confirmUnlinkModal.querySelector('.close');

    openModalBtn.addEventListener('click', function () {
        confirmUnlinkModal.style.display = 'block';
    });

    closeModalBtn.addEventListener('click', function () {
        confirmUnlinkModal.style.display = 'none';
    });

    window.addEventListener('click', function (event) {
        if (event.target === confirmUnlinkModal) {
            confirmUnlinkModal.style.display = 'none';
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const confirmUnlinkModal = document.getElementById('confirmUnlinkModal');
    const confirmUnlinkBtn = document.getElementById('confirmUnlink');
    const cancelUnlinkBtn = document.getElementById('cancelUnlink');
    const closeModalBtn = confirmUnlinkModal.querySelector('.close');

    function closeModal() {
        confirmUnlinkModal.style.display = 'none';
    }
    confirmUnlinkBtn.addEventListener('click', async function () {
        const userId = document.getElementById('userIdInput').value;

        try {
            const response = await fetch('/user/disconnect_tg', {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_id: userId })
            });

            const data = await response.json();

            if (response.ok) {
                location.reload();
            } else {
                alert(`Ошибка: ${data.detail || 'Не удалось отвязать Telegram.'}`);
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при отвязке Telegram.');
        }
    });


    cancelUnlinkBtn.addEventListener('click', closeModal);

    closeModalBtn.addEventListener('click', closeModal);

    window.addEventListener('click', function (event) {
        if (event.target === confirmUnlinkModal) {
            closeModal();
        }
    });
});
