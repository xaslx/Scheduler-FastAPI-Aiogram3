function blockUser(userId) {
    fetch(`/user/ban/${userId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Пользователь заблокирован:', data);
        location.reload();
    })
    .catch(error => {
        console.error('Произошла ошибка при блокировке пользователя:', error);
    });
}

function unblockUser(userId) {
    fetch(`/user/unban/${userId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Пользователь разблокирован:', data);
        location.reload();
    })
    .catch(error => {
        console.error('Произошла ошибка при разблокировке пользователя:', error);
    });
}

function saveNewRole(userId) {
    const newRole = document.getElementById('new-role-select').value;
    fetch(`/user/edit_role/${userId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ role: newRole })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Роль пользователя изменена:', data);
        location.reload(true);
    })
    .catch(error => {
        console.error('Произошла ошибка при изменении роли пользователя:', error);
    });
}

let userIdToDelete;

function showDeleteModal(userId) {
    userIdToDelete = userId;
    document.getElementById('deleteModal').style.display = 'block';
}

function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
}

function deleteUser() {
    fetch(`/user/delete_user_for_admin/${userIdToDelete}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Пользователь удален:', data);
        window.location.href = '{{ url_for("allusers:page") }}';
    })
    .catch(error => {
        console.error('Произошла ошибка при удалении пользователя:', error);
    });
}

window.onclick = function(event) {
    if (event.target == document.getElementById('deleteModal')) {
        closeDeleteModal();
    }
}