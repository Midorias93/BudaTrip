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
            }, 500);
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
    const email = document.getElementById('email').value.toLowerCase();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    // Validation
    if (!nom || !email || !password || !confirmPassword) {
        showError('Please fill in all fields');
        return;
    }

    if (password !== confirmPassword) {
        showError('Passwords do not match');
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
            setTimeout(() => {
            window.location.href = '/login'}, 500);
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