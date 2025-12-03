export function showLoading() {
    document.getElementById('loading').classList.add('active');
}

export function hideLoading() {
    document.getElementById('loading').classList.remove('active');
}

export function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.classList.add('active');
    setTimeout(() => {
        errorDiv.classList.remove('active');
    }, 5000);
}

export function switchTabLocomotion(tabName) {
    document.querySelectorAll('.tab-btn-locomotion').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-content-locomotion').forEach(content => {
        content.classList.remove('active');
    });

    event.target.classList.add('active');
    document.getElementById(`tab-${tabName}`).classList.add('active');

    if (tabName === 'bike') {
        import('./weather.js').then(module => module.checkRainAndShowAlert());
    }
}

export function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    event.target.classList.add('active');
    document.getElementById(`tab-${tabName}`).classList.add('active');
}

export function showSearchNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => notification.remove(), 3000);
}