document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('#loginForm form');
    const registerForm = document.querySelector('#registerForm form');
    const loginMessage = document.getElementById('loginMessage');
    const registerMessage = document.getElementById('registerMessage');

    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            try {
                const response = await fetch('http://localhost:8000/login', {
                    method: 'POST',
                    body: formData,
                    credentials: 'include' // Important for cookies
                });
                
                if (response.ok || response.status === 303) {
                    loginMessage.style.color = 'green';
                    loginMessage.textContent = 'Login successful!';
                    // Small delay to show the success message
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 500);
                } else {
                    const data = await response.json();
                    loginMessage.style.color = 'red';
                    loginMessage.textContent = data.detail || 'Login failed';
                }
            } catch (error) {
                // Only show error if we haven't already started redirecting
                if (!loginMessage.textContent.includes('successful')) {
                    loginMessage.style.color = 'red';
                    loginMessage.textContent = 'Error connecting to server';
                }
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            try {
                const response = await fetch('http://localhost:8000/register', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                
                if (response.ok) {
                    registerMessage.style.color = 'green';
                    registerMessage.textContent = 'Registration successful! Redirecting to login...';
                    setTimeout(() => {
                        document.getElementById('loginForm').style.display = 'block';
                        document.getElementById('registerForm').style.display = 'none';
                    }, 1000);
                } else {
                    registerMessage.style.color = 'red';
                    registerMessage.textContent = data.detail || 'Registration failed';
                }
            } catch (error) {
                registerMessage.style.color = 'red';
                registerMessage.textContent = 'Error connecting to server';
            }
        });
    }
});

async function handleLogout(event) {
    event.preventDefault();
    try {
        const response = await fetch('/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'  // Required for cookies
        });
        
        // Always redirect to auth page after logout attempt
        window.location.href = '/auth';
    } catch (error) {
        console.error('Logout failed:', error);
        // Still redirect to auth page even if there's an error
        window.location.href = '/auth';
    }
}