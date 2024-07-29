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