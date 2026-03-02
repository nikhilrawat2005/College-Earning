// static/js/notifications.js
document.addEventListener('DOMContentLoaded', function() {
    const badge = document.getElementById('notification-badge');
    const list = document.getElementById('notification-list');
    const markAllBtn = document.getElementById('mark-all-read');

    if (!badge) return; // Notifications not present on this page

    function updateNotifications() {
        fetch('/notifications/unread')
            .then(res => {
                if (!res.ok) throw new Error('Network response was not ok');
                return res.json();
            })
            .then(data => {
                const count = data.count;
                if (count > 0) {
                    badge.textContent = count;
                    badge.style.display = 'inline';
                } else {
                    badge.style.display = 'none';
                }

                if (list) {
                    if (data.notifications.length === 0) {
                        list.innerHTML = '<li><span class="dropdown-item-text">No new notifications</span></li>';
                    } else {
                        let html = '';
                        data.notifications.forEach(n => {
                            let text = '';
                            if (n.type === 'message') {
                                text = 'New message';
                                if (n.reference_id) {
                                    // In a full implementation, you could link to conversation
                                    text = '<a href="/chat/">New message</a>';
                                }
                            } else {
                                text = n.type;
                            }
                            html += `<li><a class="dropdown-item" href="#">${text}</a></li>`;
                        });
                        list.innerHTML = html;
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching notifications:', error);
            });
    }

    updateNotifications();
    setInterval(updateNotifications, 10000); // every 10 seconds

    if (markAllBtn) {
        markAllBtn.addEventListener('click', function() {
            fetch('/notifications/mark-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.CSRF_TOKEN   // FIXED: added CSRF token
                },
                body: JSON.stringify({all: true})
            })
            .then(res => {
                if (!res.ok) throw new Error('Failed to mark read');
                updateNotifications();
            })
            .catch(error => {
                console.error('Error marking notifications as read:', error);
            });
        });
    }
});