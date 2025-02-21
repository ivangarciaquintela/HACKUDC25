document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const message = document.getElementById('message');

    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(loginForm);
            
            try {
                const response = await fetch('http://localhost:8000/login', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                
                if (response.ok) {
                    // Store the token
                    localStorage.setItem('token', data.access_token);
                    message.style.color = 'green';
                    message.textContent = 'Login successful!';
                    // Redirect to home page after 1 second
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1000);
                } else {
                    message.style.color = 'red';
                    message.textContent = data.detail || 'Login failed';
                }
            } catch (error) {
                message.style.color = 'red';
                message.textContent = 'Error connecting to server';
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(registerForm);
            
            try {
                const response = await fetch('http://localhost:8000/register', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                
                if (response.ok) {
                    message.style.color = 'green';
                    message.textContent = 'Registration successful! Redirecting to login...';
                    // Redirect to login page after 1 second
                    setTimeout(() => {
                        window.location.href = '/login.html';
                    }, 1000);
                } else {
                    message.style.color = 'red';
                    message.textContent = data.detail || 'Registration failed';
                }
            } catch (error) {
                message.style.color = 'red';
                message.textContent = 'Error connecting to server';
            }
        });
    }
}); 