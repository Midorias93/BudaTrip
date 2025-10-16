// ============================================
// TOGGLE PASSWORD VISIBILITY
// ============================================

function togglePassword(inputId = 'password') {
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
// SHOW/HIDE LOADING
// ============================================

function showLoading() {
    document.getElementById('loading').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// ============================================
// SHOW ERROR MESSAGE
// ============================================

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';

    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// ============================================
// SHOW SUCCESS MESSAGE
// ============================================

function showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    successDiv.textContent = message;
    successDiv.style.display = 'block';

    setTimeout(() => {
        successDiv.style.display = 'none';
    }, 3000);
}

// ============================================
// HANDLE LOGIN
// ============================================

async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!email || !password) {
        showError('Please fill in all fields');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (data.success) {
            showSuccess('Login successful! Redirecting...');

            // Store user data in localStorage
            localStorage.setItem('user', JSON.stringify(data.user));

            // Redirect to home page after 1.5 seconds
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showError(data.error || 'Login failed');
        }
    } catch (error) {
        showError('An error occurred. Please try again.');
        console.error('Login error:', error);
    } finally {
        hideLoading();
    }
}

// ============================================
// HANDLE SIGNUP
// ============================================

async function handleSignup(event) {
    event.preventDefault();

    const nom = document.getElementById('nom').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const terms = document.getElementById('terms').checked;

    // Validation
    if (!nom || !email || !password || !confirmPassword) {
        showError('Please fill in all fields');
        return;
    }

    if (password !== confirmPassword) {
        showError('Passwords do not match');
        return;
    }

    if (password.length < 6) {
        showError('Password must be at least 6 characters');
        return;
    }

    if (!terms) {
        showError('Please accept the Terms & Conditions');
        return;
    }

    showLoading();

    try {
        const response = await fetch('/api/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nom, email, password })
        });

        const data = await response.json();

        if (data.success) {
            showSuccess('Account created successfully! Redirecting to login...');

            // Redirect to login page after 2 seconds
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else {
            showError(data.error || 'Signup failed');
        }
    } catch (error) {
        showError('An error occurred. Please try again.');
        console.error('Signup error:', error);
    } finally {
        hideLoading();
    }
}

// ============================================
// AUTO-FILL FROM URL PARAMS (Optional)
// ============================================

window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const email = urlParams.get('email');

    if (email) {
        const emailInput = document.getElementById('email');
        if (emailInput) {
            emailInput.value = email;
        }
    }
});

// ============================================
// USER SESSION MANAGEMENT
// ============================================

// Check if user is logged in on page load
function checkUserSession() {
    const user = localStorage.getItem('user');

    if (user) {
        const userData = JSON.parse(user);
        showUserMenu(userData);
    } else {
        showGuestMenu();
    }
}

// Show user menu when logged in
function showUserMenu(userData) {
    document.getElementById('auth-bar-guest').style.display = 'none';
    document.getElementById('auth-bar-user').style.display = 'flex';

    // Display user name
    const userName = userData.nom || userData.email.split('@')[0];
    document.getElementById('user-name').textContent = userName;
}

// Show guest menu when not logged in
function showGuestMenu() {
    document.getElementById('auth-bar-guest').style.display = 'flex';
    document.getElementById('auth-bar-user').style.display = 'none';
}

// Toggle user dropdown menu
function toggleUserDropdown() {
    const userMenu = document.querySelector('.user-menu');
    userMenu.classList.toggle('active');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const userMenu = document.querySelector('.user-menu');
    const userBtn = document.querySelector('.user-btn');

    if (userMenu && !userMenu.contains(event.target)) {
        userMenu.classList.remove('active');
    }
});

// Handle logout
function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('user');
        showGuestMenu();

        // Show success message
        const successMsg = document.createElement('div');
        successMsg.className = 'logout-message';
        successMsg.innerHTML = '<i class="fas fa-check-circle"></i> Logged out successfully';
        document.body.appendChild(successMsg);

        setTimeout(() => {
            successMsg.remove();
        }, 3000);
    }
}

// Initialize on page load
checkUserSession();

