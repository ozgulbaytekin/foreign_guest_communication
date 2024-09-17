document.addEventListener('DOMContentLoaded', function () {
    

    // ---------------- GUEST TABLE AND FORM FUNCTIONALITY -----------------

    const table = document.getElementById('guestTable');
    const guestForm = document.getElementById('newGuestForm');

    // Handle guest table actions
    if (table) {
        table.addEventListener('click', function (event) {
            if (event.target.classList.contains('edit-btn')) {
                const row = event.target.closest('tr');
                toggleEditMode(row, true);
            }

            if (event.target.classList.contains('save-btn')) {
                const row = event.target.closest('tr');
                const guestId = row.getAttribute('data-guest-id');
                const updatedData = {
                    id: guestId,
                    name: row.querySelectorAll('.editable input')[0].value.trim(),
                    surname: row.querySelectorAll('.editable input')[1].value.trim(),
                    email: row.querySelectorAll('.editable input')[2].value.trim(),
                    expiration_date: row.querySelectorAll('.editable input')[3].value.trim()
                };
                saveGuestData(updatedData, row);
            }

            if (event.target.classList.contains('delete-btn')) {
                const guestId = event.target.getAttribute('data-id');
                deleteGuest(guestId);
            }
        });
    }

    // Handle guest form submission
    if (guestForm) {
        guestForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const formData = new FormData(guestForm);
            const newGuestData = {
                name: formData.get('name').trim(),
                surname: formData.get('surname').trim(),
                email: formData.get('email').trim(),
                expiration_date: formatDateForServer(formData.get('expiration_date').trim())
            };
            addGuestData(newGuestData);
        });
    }

    // Toggle edit mode for guest rows
    function toggleEditMode(row, isEditing) {
        const editBtn = row.querySelector('.edit-btn');
        const saveBtn = row.querySelector('.save-btn');
        const editableFields = row.querySelectorAll('.editable');

        if (isEditing) {
            editableFields.forEach(field => {
                const input = document.createElement('input');
                input.value = field.textContent.trim();
                input.classList.add('edit-input');
                field.textContent = '';
                field.appendChild(input);
            });
            editBtn.style.display = 'none';
            saveBtn.style.display = 'inline-block';
        } else {
            editableFields.forEach(field => {
                const input = field.querySelector('input');
                field.textContent = input.value.trim();
            });
            editBtn.style.display = 'inline-block';
            saveBtn.style.display = 'none';
        }
    }

    // Save updated guest data
    function saveGuestData(data, row) {
        fetch('/update_guest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                toggleEditMode(row, false);
            } else {
                alert('Error updating guest information.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Add new guest data
    function addGuestData(data) {
        fetch('/add_guest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                location.reload();
            } else {
                alert('Error adding guest.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Delete guest
    function deleteGuest(guestId) {
        if (confirm('Are you sure you want to delete this guest?')) {
            fetch(`/delete_guest/${guestId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    location.reload();
                } else {
                    alert('Error deleting guest.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    }

    // Format date for server
    function formatDateForServer(dateStr) {
        const [year, month, day] = dateStr.split('/');
        return `${year}-${month}-${day}`;
    }

    // ---------------- ADD REMINDER DAY FUNCTIONALITY -----------------

    const addReminderDayButton = document.getElementById('addReminderDay');
    const reminderDaysContainer = document.getElementById('reminderDaysContainer');

    // Function to add a new reminder day input field
    function addReminderDayInput() {
        const reminderCount = reminderDaysContainer.querySelectorAll('.reminder-day').length + 1;
        const newReminderDayDiv = document.createElement('div');
        newReminderDayDiv.classList.add('reminder-day');
        newReminderDayDiv.innerHTML = `
            <label> <i class="fa-solid fa-calendar-days"></i>Reminder ${reminderCount}:</label>
            <input type="number" name="reminder_days[]" min="1" required class="large-input">
        `;
        reminderDaysContainer.appendChild(newReminderDayDiv);
    }

    // Attach click event to the "Add Another Reminder Day" button
    if (addReminderDayButton) {
        addReminderDayButton.addEventListener('click', function () {
            addReminderDayInput();
        });
    }

    // Reset the reminder days to only one input field when the page is reloaded
    function resetReminderDays() {
        const reminderDays = reminderDaysContainer.querySelectorAll('.reminder-day');
        reminderDays.forEach((reminder, index) => {
            if (index > 0) {
                reminder.remove();
            }
        });
    }

    // Call the reset function when the page is loaded
    resetReminderDays();

    
});
