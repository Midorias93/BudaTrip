// ============================================
// INITIALIZATION
// ============================================

window.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadUserData();
    loadUserPasses();
    loadUserTravels();
});

// ============================================
// AUTH CHECK
// ============================================

function checkAuth() {
    const user = localStorage.getItem('user');

    if (!user) {
        window.location.href = '/login';
        return;
    }
}

// ============================================
// LOAD USER DATA
// ============================================

function formatFrenchPhone(raw) {
    if (!raw) return '';
    let digits = String(raw).replace(/\D/g, ''); // keep only digits
    if (digits.startsWith('33')) digits = digits.slice(2); // remove FR country code if present
    if (digits.startsWith('0')) digits = digits.slice(1); // remove national 0
    digits = digits.slice(0, 9); // keep at most 9 digits (national format without 0)

    const parts = [];
    if (digits.length > 0) parts.push(digits.slice(0, 1));
    if (digits.length > 1) parts.push(digits.slice(1, 3));
    if (digits.length > 3) parts.push(digits.slice(3, 5));
    if (digits.length > 5) parts.push(digits.slice(5, 7));
    if (digits.length > 7) parts.push(digits.slice(7, 9));

    return parts.length ? '+33 ' + parts.join(' ') : '';
}

function loadUserData() {
    const user = localStorage.getItem('user');

    if (!user) return;

    const userData = JSON.parse(user);

    document.getElementById('sidebar-name').textContent = userData.name || 'User';
    document.getElementById('sidebar-email').textContent = userData.email;

    document.getElementById('name').value = userData.name || '';
    document.getElementById('email-profile').value = userData.email;
    phone = userData.phone || '';
    phone = formatFrenchPhone(phone);
    document.getElementById('phone').value = phone;


}

// ============================================
// SECTION NAVIGATION
// ============================================

function showSection(sectionName) {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });

    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });

    event.target.closest('.nav-item').classList.add('active');

    document.getElementById(`section-${sectionName}`).classList.add('active');
}

// ============================================
// TOGGLE PASSWORD VISIBILITY
// ============================================

function togglePasswordField(inputId) {
    const input = document.getElementById(inputId);
    const button = input.parentElement.querySelector('.toggle-password');
    const icon = button.querySelector('i');

    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// ============================================
// UPDATE PROFILE
// ============================================

async function updateProfile(event) {
    event.preventDefault();

    const name = document.getElementById('name').value;
    const email = document.getElementById('email-profile').value;
    const phone = document.getElementById('phone').value;

    if (!name) {
        showToast('Please enter your name', 'error');
        return;
    }

    showLoading();

    try {
        const user = JSON.parse(localStorage.getItem('user'));

        const response = await fetch(`/api/users/${user.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                email: email,
                phone: phone
            })
        });

        const data = await response.json();

        if (!data.success) {
            showToast(data.error || 'Failed to update profile', 'error');
            return;
        }


        const updatedUser = {
            ...user,
            name: name,
            email: email,
            phone: phone
        };

        localStorage.setItem('user', JSON.stringify(updatedUser));

        loadUserData();

        showToast('Profile updated successfully!', 'success');

    } catch (error) {
        showToast('Failed to update profile', 'error');
        console.error('Update error:', error);
    } finally {
        hideLoading();
    }
}

// ============================================
// UPDATE PASSWORD
// ============================================

async function updatePassword(event) {
    event.preventDefault();

    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    // Validation
    if (!currentPassword || !newPassword || !confirmPassword) {
        showToast('Please fill in all password fields', 'error');
        return;
    }

    if (newPassword !== confirmPassword) {
        showToast('New passwords do not match', 'error');
        return;
    }

    showLoading();

    try {
        const user = JSON.parse(localStorage.getItem('user'));

        const response = await fetch(`/api/users/${user.id}/password`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                current_password: currentPassword,
                password: newPassword
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast('Password updated successfully!', 'success');
            document.getElementById('password-form').reset();
        } else {
            showToast(data.error || 'Failed to update password', 'error');
        }

    } catch (error) {
        showToast('An error occurred. Please try again.', 'error');
        console.error('Password update error:', error);
    } finally {
        hideLoading();
    }
}

// ============================================
// DELETE ACCOUNT
// ============================================

async function deleteAccount() {
    const confirmed = confirm(
        '⚠️ WARNING: This action is irreversible!\n\n' +
        'Are you sure you want to delete your account?\n' +
        'All your data will be permanently removed.'
    );

    if (!confirmed) return;

    const doubleConfirm = confirm(
        'This is your last chance!\n\n' +
        'Type your password to confirm account deletion.\n' +
        'Click OK to proceed.'
    );

    if (!doubleConfirm) return;

    showLoading();

    try {
        const user = JSON.parse(localStorage.getItem('user'));

        // Simulate API call
        const response = await fetch(`/api/users/${user.id}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            localStorage.removeItem('user');
            showToast('Account deleted successfully. Redirecting...', 'success');

            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        } else {
            showToast(data.error || 'Failed to delete account', 'error');
        }

    } catch (error) {
        showToast('An error occurred. Please try again.', 'error');
        console.error('Delete account error:', error);
    } finally {
        hideLoading();
    }
}

// ============================================
// LOGOUT
// ============================================

function handleLogout() {
    const confirmed = confirm('Are you sure you want to logout?');

    if (confirmed) {
        localStorage.removeItem('user');
        showToast('Logged out successfully', 'success');

        setTimeout(() => {
            window.location.href = '/';
        }, 1500);
    }
}

// ============================================
// HELPER FUNCTIONS
// ============================================

function showLoading() {
    document.getElementById('loading-overlay').classList.add('show');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.remove('show');
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');

    // Set icon based on type
    const icon = type === 'success'
        ? '<i class="fas fa-check-circle"></i>'
        : '<i class="fas fa-exclamation-circle"></i>';

    toast.innerHTML = `${icon} <span>${message}</span>`;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// ============================================
// PASSES MANAGEMENT
// ============================================

async function loadUserPasses() {
    try {
        const user = JSON.parse(localStorage.getItem('user'));
        if (!user) return;

        const response = await fetch(`/api/passes/user/${user.id}`);
        const data = await response.json();

        const passesList = document.getElementById('passes-list');

        if (data.success && data.passes && data.passes.length > 0) {
            passesList.innerHTML = `
                <div class="table-responsive">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Price</th>
                                <th>Date Added</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.passes.map(pass => `
                                <tr>
                                    <td><i class="fas fa-ticket-alt"></i> ${capitalizeFirstLetter(pass.type)}</td>
                                    <td>${pass.price} HUF</td>
                                    <td>${formatDate(pass.date)}</td>
                                    <td>
                                        <button class="btn-icon btn-danger" onclick="deletePass(${pass.id})" title="Delete">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } else {
            passesList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-ticket-alt"></i>
                    <p>No passes found. Add your first pass using the form above!</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading passes:', error);
        document.getElementById('passes-list').innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-circle"></i>
                <p>Failed to load passes</p>
            </div>
        `;
    }
}

async function addNewPass(event) {
    event.preventDefault();

    const passType = document.getElementById('pass-type').value;
    const passPrice = document.getElementById('pass-price').value;

    if (!passType || !passPrice) {
        showToast('Please fill in all fields', 'error');
        return;
    }

    showLoading();

    try {
        const user = JSON.parse(localStorage.getItem('user'));

        const response = await fetch('/api/passes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: passType,
                price: parseFloat(passPrice),
                user_id: user.id
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast('Pass added successfully!', 'success');
            document.getElementById('pass-form').reset();
            loadUserPasses();
        } else {
            showToast(data.error || 'Failed to add pass', 'error');
        }

    } catch (error) {
        showToast('An error occurred. Please try again.', 'error');
        console.error('Add pass error:', error);
    } finally {
        hideLoading();
    }
}

async function deletePass(passId) {
    const confirmed = confirm('Are you sure you want to delete this pass?');

    if (!confirmed) return;

    showLoading();

    try {
        const response = await fetch(`/api/passes/${passId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast('Pass deleted successfully', 'success');
            loadUserPasses();
        } else {
            showToast(data.error || 'Failed to delete pass', 'error');
        }

    } catch (error) {
        showToast('An error occurred. Please try again.', 'error');
        console.error('Delete pass error:', error);
    } finally {
        hideLoading();
    }
}

// ============================================
// TRAVELS MANAGEMENT
// ============================================

async function loadUserTravels() {
    try {
        const user = JSON.parse(localStorage.getItem('user'));
        if (!user) return;

        const response = await fetch(`/api/travels/user/${user.id}`);
        const data = await response.json();

        const travelsList = document.getElementById('travels-list');

        if (data.success && data.travels && data.travels.length > 0) {
            travelsList.innerHTML = `
                <div class="table-responsive">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Transport Type</th>
                                <th>Distance</th>
                                <th>Duration</th>
                                <th>Cost</th>
                                <th>CO₂ Emissions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.travels.map(travel => `
                                <tr>
                                    <td>${formatDate(travel.date)}</td>
                                    <td><i class="fas fa-${getTransportIcon(travel.transportType)}"></i> ${capitalizeFirstLetter(travel.transportType || 'N/A')}</td>
                                    <td>${travel.distance ? travel.distance.toFixed(2) + ' km' : 'N/A'}</td>
                                    <td>${travel.duration ? formatDuration(travel.duration) : 'N/A'}</td>
                                    <td>${travel.cost ? travel.cost.toFixed(2) + ' HUF' : 'N/A'}</td>
                                    <td>${travel.CO2Emissions ? travel.CO2Emissions.toFixed(2) + ' kg' : 'N/A'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } else {
            travelsList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-route"></i>
                    <p>No travel history found. Start planning your trips!</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading travels:', error);
        document.getElementById('travels-list').innerHTML = `
            <div class="error-state">
                <i class="fas fa-exclamation-circle"></i>
                <p>Failed to load travel history</p>
            </div>
        `;
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function capitalizeFirstLetter(string) {
    if (!string) return '';
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatDuration(minutes) {
    if (!minutes) return 'N/A';
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    if (hours > 0) {
        return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
}

function getTransportIcon(transportType) {
    const icons = {
        'bike': 'bicycle',
        'bicycle': 'bicycle',
        'car': 'car',
        'bus': 'bus',
        'train': 'train',
        'walking': 'walking',
        'walk': 'walking'
    };
    return icons[transportType?.toLowerCase()] || 'route';
}
}
