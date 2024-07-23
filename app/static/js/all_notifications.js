var modal = document.getElementById('deleteConfirmationModal');
var confirmButton = document.getElementById('confirmDelete');
var cancelButton = document.getElementById('cancelDelete');


var deleteIcons = document.querySelectorAll('.delete-icon');

deleteIcons.forEach(function(icon) {
    icon.addEventListener('click', function() {
        var notificationId = this.getAttribute('data-notification-id');


        modal.style.display = 'block';

        
        confirmButton.onclick = function() {
    
            fetch('/notification/' + notificationId, {
                method: 'DELETE',
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка удаления');
                }
        
                window.location.reload();
            })
            .catch(error => {
                console.error('Ошибка удаления:', error);
                alert('Произошла ошибка при удалении уведомления.');
            })
            .finally(() => {
                modal.style.display = 'none';
            });
        }

        cancelButton.onclick = function() {
            modal.style.display = 'none';
        }

        var closeIcon = document.querySelector('.close');
        closeIcon.onclick = function() {
            modal.style.display = 'none';
        }
    });
});
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}