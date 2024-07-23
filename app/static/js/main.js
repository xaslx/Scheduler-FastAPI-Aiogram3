document.addEventListener('DOMContentLoaded', function() {
    const notificationItems = document.querySelectorAll('.notification-item');
    const userPhoto = document.querySelector('.user-photo');
    const notificationIcon = document.querySelector('.notification-icon');
    const dropdowns = ['notification-list', 'user-dropdown'];

    notificationItems.forEach(item => {
        item.addEventListener('click', function(event) {
            event.stopPropagation(); 
            const notificationUrl = item.querySelector('a').getAttribute('href');
            window.location.href = notificationUrl;
        });
    });

    function handleUserPhotoClick(event) {
        event.stopPropagation();
        toggleDropdown('user-dropdown');
    }

    function handleNotificationIconClick(event) {
        event.stopPropagation();
        toggleDropdown('notification-list');
    }
    

    userPhoto.addEventListener('click', handleUserPhotoClick);
    notificationIcon.addEventListener('click', handleNotificationIconClick);

    if (window.innerWidth > 600) {
        userPhoto.addEventListener('mouseover', function() {
            showDropdown('user-dropdown');
        });
        userPhoto.addEventListener('mouseout', function() {
            hideDropdown('user-dropdown');
        });

        notificationIcon.addEventListener('mouseover', function() {
            showDropdown('notification-list');
        });
        notificationIcon.addEventListener('mouseout', function() {
            hideDropdown('notification-list');
        });
    }

    let activeDropdown = null;

    function showDropdown(dropdownId) {
        hideDropdowns();
        const dropdown = document.getElementById(dropdownId);
        dropdown.classList.add('active');
        activeDropdown = dropdownId;
    }

    function hideDropdown(dropdownId) {
        const dropdown = document.getElementById(dropdownId);
        if (dropdown) {
            dropdown.classList.remove('active');
            if (activeDropdown === dropdownId) {
                activeDropdown = null;
            }
        }
    }

    function hideDropdowns() {
        dropdowns.forEach(id => hideDropdown(id));
    }

    function toggleDropdown(dropdownId) {
        if (activeDropdown === dropdownId) {
            hideDropdown(dropdownId);
        } else {
            showDropdown(dropdownId);
        }
    }


    document.addEventListener('click', function(event) {
        if (!event.target.closest('.notification-icon') && activeDropdown === 'notification-list') {
            hideDropdown('notification-list');
        }
        if (!event.target.closest('.user-photo') && activeDropdown === 'user-dropdown') {
            hideDropdown('user-dropdown');
        }
    });
});
function logout(event) {
event.preventDefault(); 

fetch('/auth/logout', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
})
.then(response => {
    if (response.ok) {
        window.location.href = '/auth/login';
    } else {
        return response.text().then(text => {
            throw new Error(text);
        });
    }
})
.catch(error => {
    Swal.fire('Ошибка', 'Не удалось выполнить выход', 'error');
});
}