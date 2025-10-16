// ============================================
// INITIALIZATION
// ============================================

window.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadUserData();
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

function loadUserData() {
    const user = localStorage.getItem('user');

    if (!user) return;

    const userData = JSON.parse(user);

    document.getElementById('sidebar-name').textContent = userData.nom || 'User';
    document.getElementById('sidebar-email').textContent = userData.email;

    document.getElementById('name').value = userData.nom || '';
    document.getElementById('email-profile').value = userData.email;

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
                nom: name,
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
            nom: name,
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

    if (newPassword.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }

    showLoading();

    try {
        const user = JSON.parse(localStorage.getItem('user'));

        // Simulate API call to backend
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
