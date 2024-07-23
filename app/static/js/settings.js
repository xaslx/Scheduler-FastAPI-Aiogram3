document.addEventListener('DOMContentLoaded', function() {
    const toggleSwitch = document.querySelector('.switch input[type="checkbox"]');
    const editLink = document.querySelector('.edit-profile-button');
    const timeSettingsForm = document.getElementById('time-settings-form');
    const userId = editLink.getAttribute('data-user-id');
    
    toggleSwitch.addEventListener('change', function() {
        const isChecked = this.checked;
        
        fetch(`/user/edit_enabled/${userId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                enabled: isChecked
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('PATCH request successful', data);
            editLink.disabled = !isChecked;
        })
        .catch(error => {
            console.error('Error during PATCH request:', error);
        });
    });

    editLink.addEventListener('click', function(event) {
        event.preventDefault();

        const formData = new FormData(timeSettingsForm);
        const data = {
            start_time: formData.get('start_time'),
            end_time: formData.get('end_time'),
            interval: formData.get('interval')
        };

        fetch(`/user/edit_time/${userId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                console.log(JSON.stringify(data));
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('PATCH request successful', data);
            displayCustomNotification('Сохранено');
        })
        .catch(error => {
            console.error('Error during PATCH request:', error);
        });
    });

    function displayCustomNotification(message) {
        Swal.fire({
            icon: 'success',
            title: 'Успех!',
            text: message,
            timer: 2500,
            timerProgressBar: true,
            position: 'top',
            toast: true,
            customClass: {
                popup: 'custom-swal',
                title: 'custom-swal-title',
                content: 'custom-swal-content'
            },
            width: '70%',
            padding: '1rem',
            background: '#fff',
            textColor: '#333',
            showConfirmButton: false,
        });
    }
});
