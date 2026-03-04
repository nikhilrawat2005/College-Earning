// static/js/hire.js
document.addEventListener('DOMContentLoaded', function() {
    const hireBtn = document.getElementById('hire-btn');
    const recordBtn = document.getElementById('record-work-btn');
    const recordModal = new bootstrap.Modal(document.getElementById('recordModal'));
    const viewRecordModal = new bootstrap.Modal(document.getElementById('viewRecordModal'));
    const saveRecordBtn = document.getElementById('save-record');

    if (!hireBtn) return; // No hire button on this page

    const conversationId = hireBtn.dataset.conversationId;
    let currentRequestId = null;
    let autoPopupShown = false; // To avoid multiple popups

    // Fetch initial hire status
    fetch(`/chat/hire/status/${conversationId}`)
        .then(res => res.json())
        .then(data => {
            updateHireButton(data);
            checkAutoPopup(data);
        })
        .catch(err => console.error('Failed to fetch hire status:', err));

    // Hire button click
    hireBtn.addEventListener('click', function() {
        if (hireBtn.disabled) return;
        hireBtn.disabled = true;
        fetch(`/chat/hire/request/${conversationId}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': window.CSRF_TOKEN,
                'Content-Type': 'application/json'
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                currentRequestId = data.request_id;
                setButtonState('pending');
            } else {
                alert('Error: ' + data.error);
                hireBtn.disabled = false;
            }
        })
        .catch(err => {
            console.error(err);
            alert('Network error');
            hireBtn.disabled = false;
        });
    });

    // Record button click
    if (recordBtn) {
        recordBtn.addEventListener('click', function() {
            // Fetch latest status to show correct modal
            fetch(`/chat/hire/status/${conversationId}`)
                .then(res => res.json())
                .then(data => {
                    if (data.record_created) {
                        // Show view modal with details
                        document.getElementById('view-title').textContent = data.work_title || '—';
                        document.getElementById('view-start').textContent = data.start_date || '—';
                        document.getElementById('view-end').textContent = data.end_date || '—';
                        document.getElementById('view-description').textContent = data.work_description || '—';
                        viewRecordModal.show();
                    } else if (data.is_requester) {
                        // Only requester can create record
                        recordModal.show();
                    } else {
                        alert('The work record has not been created yet. Only the requester can create it.');
                    }
                });
        });
    }

    // Save record details
    saveRecordBtn.addEventListener('click', function() {
        const title = document.getElementById('work-title').value.trim();
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        const description = document.getElementById('work-description').value.trim();

        if (!title || !startDate || !endDate) {
            alert('Please fill in all required fields.');
            return;
        }

        fetch(`/chat/hire/record/${currentRequestId}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': window.CSRF_TOKEN,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: title,
                start_date: startDate,
                end_date: endDate,
                description: description
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                recordModal.hide();
                // Reset hire button to default (since active becomes false)
                setButtonState('default');
                // Update record button to now show view modal
                alert('Work record saved successfully.');
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(err => {
            console.error(err);
            alert('Network error');
        });
    });

    function updateHireButton(data) {
        if (!data.status) {
            setButtonState('default');
            if (recordBtn) recordBtn.style.display = 'none';
        } else if (data.status === 'pending') {
            setButtonState('pending');
            currentRequestId = data.request_id;
            if (recordBtn) recordBtn.style.display = 'none';
        } else if (data.status === 'accepted') {
            setButtonState('accepted');
            currentRequestId = data.request_id;
            // Show record button only if record_created or user is requester
            if (data.record_created || data.is_requester) {
                if (recordBtn) recordBtn.style.display = 'inline-block';
            } else {
                if (recordBtn) recordBtn.style.display = 'none';
            }
        } else {
            // Fallback
            setButtonState('default');
        }
    }

    function setButtonState(state) {
        hireBtn.classList.remove('hire-default', 'hire-pending', 'hire-accepted', 'hire-rejected');
        switch(state) {
            case 'default':
                hireBtn.textContent = 'Hire Worker';
                hireBtn.classList.add('hire-default');
                hireBtn.disabled = false;
                break;
            case 'pending':
                hireBtn.textContent = 'Pending';
                hireBtn.classList.add('hire-pending');
                hireBtn.disabled = true;
                break;
            case 'accepted':
                hireBtn.textContent = 'Ready to Work';
                hireBtn.classList.add('hire-accepted');
                hireBtn.disabled = true;
                break;
            case 'rejected':
                hireBtn.textContent = 'Rejected';
                hireBtn.classList.add('hire-rejected');
                hireBtn.disabled = true;
                // After a short delay, revert to default (page refresh will reset anyway)
                setTimeout(() => {
                    setButtonState('default');
                }, 3000);
                break;
        }
    }

    function checkAutoPopup(data) {
        // Auto-popup for requester when request accepted and record not yet created
        if (data.is_requester && data.status === 'accepted' && !data.record_created && !autoPopupShown) {
            autoPopupShown = true;
            setTimeout(() => {
                recordModal.show();
            }, 500); // slight delay for better UX
        }
    }
});