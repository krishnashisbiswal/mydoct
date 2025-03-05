// Custom JavaScript for MyDoct application
document.addEventListener('DOMContentLoaded', function() {
    console.log('MyDoct scripts loaded');

    // Handle Mark Completed button clicks
    document.querySelectorAll('.mark-completed-btn').forEach(button => {
        button.addEventListener('click', function() {
            const appointmentId = this.dataset.appointmentId;
            updateAppointmentStatus(appointmentId, 'C');
        });
    });

    // Handle Mark Missed button clicks
    document.querySelectorAll('.mark-missed-btn').forEach(button => {
        button.addEventListener('click', function() {
            const appointmentId = this.dataset.appointmentId;
            updateAppointmentStatus(appointmentId, 'M');
        });
    });

    function updateAppointmentStatus(appointmentId, status) {
        console.log('Updating appointment status:', status); // Log the status being updated

        const url = window.location.origin + `/appointments/${appointmentId}/update_status/`;
        console.log('Making request to:', url); // Log the request URL

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({status: status})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Status updated successfully'); // Log success message
                // Refresh the page after a successful update
                location.reload();


                // Update the status display
                const statusCell = document.querySelector(`tr[data-appointment-id="${appointmentId}"] .status-cell`);
                if (statusCell) {
                    statusCell.textContent = status === 'C' ? 'Completed' : 'Missed';
                }
                // Hide the buttons after status change
                document.querySelectorAll(`[data-appointment-id="${appointmentId}"]`).forEach(btn => {
                    btn.style.display = 'none'; // Hide all buttons
                });
                // Refresh the page after a successful update
                location.reload();
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
