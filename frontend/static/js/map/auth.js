export function checkUserSession() {
    const user = localStorage.getItem('user');

    if (user) {
        const userData = JSON.parse(user);
        showUserMenu(userData);
    } else {
        showGuestMenu();
    }
}

function showUserMenu(userData) {
    document.getElementById('auth-bar-guest').style.display = 'none';
    document.getElementById('auth-bar-user').style.display = 'flex';

    const userName = userData.nom || userData.email.split('@')[0];
    document.getElementById('user-name').textContent = userName;
}

function showGuestMenu() {
    document.getElementById('auth-bar-guest').style.display = 'flex';
    document.getElementById('auth-bar-user').style.display = 'none';
}

export function toggleUserDropdown() {
    const userMenu = document.querySelector('.user-menu');
    userMenu.classList.toggle('active');
}

export function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('user');
        showGuestMenu();

        const successMsg = document.createElement('div');
        successMsg.className = 'logout-message';
        successMsg.innerHTML = '<i class="fas fa-check-circle"></i> Logged out successfully';
        document.body.appendChild(successMsg);

        setTimeout(() => successMsg.remove(), 3000);
    }
}

export function openLogin() {
    window.location.href = '/login';
}

export function openSignup() {
    window.location.href = '/signup';
}

export function initAuth() {
    checkUserSession();

    document.addEventListener('click', function(event) {
        const userMenu = document.querySelector('.user-menu');
        if (userMenu && !userMenu.contains(event.target)) {
            userMenu.classList.remove('active');
        }
    });
}