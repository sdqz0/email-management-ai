/**
 * Main JavaScript file for Email Management AI Agent
 */

// DOM Elements
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the index page or dashboard page
    const isIndexPage = document.querySelector('.auth-container') !== null;
    const isDashboardPage = document.querySelector('.dashboard-container') !== null;
    
    if (isIndexPage) {
        initializeIndexPage();
    } else if (isDashboardPage) {
        initializeDashboardPage();
    }
});

/**
 * Initialize the index (authentication) page
 */
function initializeIndexPage() {
    const credentialsForm = document.getElementById('credentials-form');
    
    if (credentialsForm) {
        credentialsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            // Check if file is selected
            const fileInput = document.getElementById('credentials_file');
            if (fileInput.files.length === 0) {
                alert('Please select a credentials.json file');
                return;
            }
            
            // Upload credentials file
            fetch('/upload_credentials', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert('Credentials uploaded successfully. You can now authenticate with Gmail.');
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while uploading credentials.');
            });
        });
    }
}

/**
 * Initialize the dashboard page
 */
function initializeDashboardPage() {
    // Navigation
    const navLinks = document.querySelectorAll('.sidebar nav ul li a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            navLinks.forEach(l => l.parentElement.classList.remove('active'));
            
            // Add active class to clicked link
            this.parentElement.classList.add('active');
            
            // Show corresponding section
            const sectionId = this.getAttribute('data-section');
            const sections = document.querySelectorAll('.content-section');
            sections.forEach(section => {
                section.classList.remove('active');
            });
            document.getElementById(sectionId).classList.add('active');
        });
    });
    
    // Fetch emails button
    const fetchEmailsBtn = document.getElementById('fetch-emails');
    if (fetchEmailsBtn) {
        fetchEmailsBtn.addEventListener('click', fetchEmails);
    }
    
    // Generate digest button
    const generateDigestBtn = document.getElementById('generate-digest');
    if (generateDigestBtn) {
        generateDigestBtn.addEventListener('click', generateDigest);
    }
    
    // Email list filtering
    const priorityFilter = document.getElementById('priority-filter');
    const categoryFilter = document.getElementById('category-filter');
    const readFilter = document.getElementById('read-filter');
    
    if (priorityFilter && categoryFilter && readFilter) {
        priorityFilter.addEventListener('change', filterEmails);
        categoryFilter.addEventListener('change', filterEmails);
        readFilter.addEventListener('change', filterEmails);
    }
    
    // Settings forms
    const emailPreferencesForm = document.getElementById('email-preferences-form');
    const priorityKeywordsForm = document.getElementById('priority-keywords-form');
    
    if (emailPreferencesForm) {
        emailPreferencesForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Preferences saved successfully!');
        });
    }
    
    if (priorityKeywordsForm) {
        priorityKeywordsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Keywords saved successfully!');
        });
    }
    
    // Modal handling
    const modal = document.getElementById('email-detail-modal');
    const closeBtn = document.querySelector('.close');
    
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Initial data load
    fetchEmails();
}

/**
 * Fetch emails from the server
 */
function fetchEmails() {
    // Show loading state
    const emailListContainer = document.getElementById('email-list-container');
    if (emailListContainer) {
        emailListContainer.innerHTML = '<p class="empty-state">Loading emails...</p>';
    }
    
    // Fetch emails from server
    fetch('/fetch_emails')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update last updated time
                const lastUpdated = document.getElementById('last-updated');
                if (lastUpdated) {
                    const now = new Date();
                    lastUpdated.textContent = 'Last updated: ' + now.toLocaleTimeString();
                }
                
                // Get email list
                getEmailList();
            } else {
                if (emailListContainer) {
                    emailListContainer.innerHTML = `<p class="empty-state">Error: ${data.message}</p>`;
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (emailListContainer) {
                emailListContainer.innerHTML = '<p class="empty-state">An error occurred while fetching emails.</p>';
            }
        });
}

/**
 * Get the list of emails from the server
 */
function getEmailList() {
    fetch('/get_email_list')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update stats
                updateStats(data.emails);
                
                // Render email list
                renderEmailList(data.emails);
                
                // Render calendar events
                renderCalendarEvents(data.emails);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

/**
 * Update dashboard statistics
 */
function updateStats(emails) {
    // Count unread emails
    const unreadCount = emails.filter(email => email.is_unread).length;
    const unreadCountElement = document.getElementById('unread-count');
    if (unreadCountElement) {
        unreadCountElement.textContent = unreadCount;
    }
    
    // Count high priority emails
    const highPriorityCount = emails.filter(email => email.priority === 'high').length;
    const highPriorityCountElement = document.getElementById('high-priority-count');
    if (highPriorityCountElement) {
        highPriorityCountElement.textContent = highPriorityCount;
    }
    
    // Count calendar events
    const calendarEventsCount = emails.filter(email => email.has_calendar_event).length;
    const calendarEventsCountElement = document.getElementById('calendar-events-count');
    if (calendarEventsCountElement) {
        calendarEventsCountElement.textContent = calendarEventsCount;
    }
    
    // Count action items (placeholder - actual count would come from server)
    const actionItemsCountElement = document.getElementById('action-items-count');
    if (actionItemsCountElement) {
        actionItemsCountElement.textContent = '0'; // This would be updated with actual data
    }
}

/**
 * Render the email list
 */
function renderEmailList(emails) {
    const emailListContainer = document.getElementById('email-list-container');
    if (!emailListContainer) return;
    
    if (emails.length === 0) {
        emailListContainer.innerHTML = '<p class="empty-state">No emails to display.</p>';
        return;
    }
    
    // Apply filters
    const priorityFilter = document.getElementById('priority-filter');
    const categoryFilter = document.getElementById('category-filter');
    const readFilter = document.getElementById('read-filter');
    
    let filteredEmails = emails;
    
    if (priorityFilter && priorityFilter.value !== 'all') {
        filteredEmails = filteredEmails.filter(email => email.priority === priorityFilter.value);
    }
    
    if (categoryFilter && categoryFilter.value !== 'all') {
        filteredEmails = filteredEmails.filter(email => email.category === categoryFilter.value);
    }
    
    if (readFilter && readFilter.value !== 'all') {
        if (readFilter.value === 'unread') {
            filteredEmails = filteredEmails.filter(email => email.is_unread);
        } else {
            filteredEmails = filteredEmails.filter(email => !email.is_unread);
        }
    }
    
    // Generate HTML
    let html = '';
    
    filteredEmails.forEach(email => {
        html += `
            <div class="email-item ${email.is_unread ? 'unread' : ''}" data-id="${email.id}">
                <div class="email-priority ${email.priority}"></div>
                <div class="email-content">
                    <div class="email-subject">${email.subject}</div>
                    <div class="email-snippet">${email.sender} - ${email.snippet || 'No preview available'}</div>
                </div>
                <div class="email-meta">
                    <div class="email-date">${formatDate(email.date)}</div>
                    <div class="email-icons">
                        ${email.has_calendar_event ? '<span title="Calendar Event">📅</span>' : ''}
                        ${email.requires_response ? '<span title="Requires Response">↩️</span>' : ''}
                    </div>
                </div>
            </div>
        `;
    });
    
    emailListContainer.innerHTML = html;
    
    // Add click event to email items
    const emailItems = document.querySelectorAll('.email-item');
    emailItems.forEach(item => {
        item.addEventListener('click', function() {
            const emailId = this.getAttribute('data-id');
            showEmailDetails(emailId);
        });
    });
}

/**
 * Render calendar events
 */
function renderCalendarEvents(emails) {
    const calendarEventsContainer = document.getElementById('calendar-events-container');
    if (!calendarEventsContainer) return;
    
    // Filter emails with calendar events
    const emailsWithEvents = emails.filter(email => email.has_calendar_event);
    
    if (emailsWithEvents.length === 0) {
        calendarEventsContainer.innerHTML = '<p class="empty-state">No calendar events detected.</p>';
        return;
    }
    
    // Placeholder for calendar events (actual data would come from server)
    let html = '';
    
    html += `
        <div class="calendar-event">
            <div class="calendar-event-title">Team Meeting</div>
            <div class="calendar-event-time">Tomorrow, 10:00 AM</div>
            <div class="calendar-event-description">Weekly team sync to discuss project progress.</div>
            <div class="calendar-event-actions">
                <button class="button secondary">Accept</button>
                <button class="button secondary">Decline</button>
            </div>
        </div>
    `;
    
    html += `
        <div class="calendar-event">
            <div class="calendar-event-title">Project Review</div>
            <div class="calendar-event-time">Friday, 2:00 PM</div>
            <div class="calendar-event-description">Review project deliverables with the client.</div>
            <div class="calendar-event-actions">
                <button class="button secondary">Accept</button>
                <button class="button secondary">Decline</button>
            </div>
        </div>
    `;
    
    calendarEventsContainer.innerHTML = html;
}

/**
 * Show email details in modal
 */
function showEmailDetails(emailId) {
    fetch(`/get_email_details/${emailId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const email = data.email;
                const modal = document.getElementById('email-detail-modal');
                const container = document.getElementById('email-detail-container');
                
                let html = `
                    <div class="email-detail-header">
                        <div class="email-detail-subject">${email.subject}</div>
                        <div class="email-detail-meta">
                            <div class="email-detail-sender">From: ${email.sender}</div>
                            <div class="email-detail-date">${email.date}</div>
                        </div>
                    </div>
                    
                    <div class="email-detail-summary">
                        <h3>Summary</h3>
                        <p>${email.summary}</p>
                    </div>
                `;
                
                if (email.action_items && email.action_items.length > 0) {
                    html += `
                        <div class="email-detail-actions">
                            <h3>Action Items</h3>
                            <ul>
                                ${email.action_items.map(item => `<li>${item}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }
                
                if (email.calendar_proposals && email.calendar_proposals.length > 0) {
                    const proposal = email.calendar_proposals[0];
                    html += `
                        <div class="email-detail-calendar">
                            <h3>Calendar Event</h3>
                            <p><strong>${proposal.title}</strong></p>
                            <p>Time: ${proposal.start_time}</p>
                            <p>Duration: ${proposal.duration} minutes</p>
                            <p>Attendees: ${proposal.attendees.join(', ')}</p>
                            <div class="calendar-event-actions">
                                <button class="button secondary">Add to Calendar</button>
                            </div>
                        </div>
                    `;
                }
                
                html += `
                    <div class="email-detail-body">
                        <h3>Email Content</h3>
                        <div>${formatEmailBody(email.body)}</div>
                    </div>
                    
                    <div class="email-detail-buttons">
                        <button class="button secondary">Mark as Read</button>
                        <button class="button secondary">Reply</button>
                    </div>
                `;
                
                container.innerHTML = html;
                modal.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

/**
 * Generate email digest
 */
function generateDigest() {
    fetch('/get_digest')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Display digest in container
                const digestContainer = document.getElementById('digest-container');
                if (digestContainer) {
                    digestContainer.innerHTML = `
                        <p>Digest generated successfully!</p>
                        <p><a href="${data.digest_url}" target="_blank" c
(Content truncated due to size limit. Use line ranges to read in chunks)