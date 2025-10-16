// ============================================
// LOAD USER DATA
// ============================================

function loadUserData() {
    const user = localStorage.getItem('user');

    if (!user) {
        window.location.href = '/login';
        return;
    }

    const userData = JSON.parse(user);

    // Display user info
    document.getElementById('display-name').textContent = userData.nom || 'User';
    document.getElementById('display-email').textContent = userData.email;

    // Fill form fields
    document.getElementById('name').value = userData.nom || '';
    document.getElementById('email-profile').value = userData.email;

    // Set member since date
    if (userData.created_at) {
        const date = new Date(userData.created_at);
        document.getElementById('member-since').textContent = date.getFullYear();
    }
}

// Load data on page load
window.addEventListener('DOMContentLoaded', loadUserData);

// ============================================
// TAB SWITCHING
// ============================================

function showAccountTab(tabName) {
    // Remove active class from all tabs and contents
    document.querySelectorAll('.account-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.account-tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // Add active class to selected tab and content
    event.target.classList.add('active');
    document.getElementById(`tab-${tabName}`).classList.add('active');
}

// ============================================
// TOGGLE PASSWORD VISIBILITY
// ============================================

function togglePasswordField(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.parentElement.querySelector('.toggle-password');

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

    if (!name) {
        showError('Please enter your name');
        return;
    }

    showLoading();

    try {
        // Get current user
        const user = JSON.parse(localStorage.getItem('user'));

        // Update user data
        const updatedUser = {
            ...user,
            nom: name
        };

        // Save to localStorage (in production, send to backend)
        localStorage.setItem('user', JSON.stringify(updatedUser));

        showSuccess('Profile updated successfully!');
        loadUserData();

    } catch (error) {
        showError('Failed to update profile');
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
    const confirmPassword = document.getElementById('confirm-new-password').value;

    // Validation
    if (!currentPassword || !newPassword || !confirmPassword) {
        showError('Please fill in all password fields');
        return;
    }

    if (newPassword !== confirmPassword) {
        showError('New passwords do not match');
        return;
    }

    if (newPassword.length < 6) {
        showError('Password must be at least 6 characters');
        return;
    }

    showLoading();

    try {
        // In production, send to backend
        // const response = await fetch('/api/update-password', { ... });

        // Simulate success
        setTimeout(() => {
            showSuccess('Password updated successfully!');
            document.getElementById('password-form').reset();
            hideLoading();
        }, 1000);

    } catch (error) {
        showError('Failed to update password');
        console.error('Password update error:', error);
        hideLoading();
    }
}

// ============================================
// DELETE ACCOUNT
// ============================================

function deleteAccount() {
    const confirmed = confirm(
        '⚠️ WARNING: This action is irreversible!\n\n' +
        'Are you sure you want to delete your account?\n' +
        'All your data will be permanently removed.'
    );

    if (confirmed) {
        const doubleConfirm = confirm(
            'This is your last chance!\n\n' +
            'Click OK to permanently delete your account.'
        );

        if (doubleConfirm) {
            showLoading();

            // In production, send delete request to backend
            setTimeout(() => {
                localStorage.removeItem('user');
                showSuccess('Account deleted successfully. Redirecting...');

                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);
            }, 1000);
        }
    }
}

// ============================================
// HELPER FUNCTIONS
// ============================================

function showLoading() {
    document.getElementById('loading').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';

    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    successDiv.textContent = message;
    successDiv.style.display = 'block';

    setTimeout(() => {
        successDiv.style.display = 'none';
    }, 3000);
}
