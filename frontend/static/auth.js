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
                    body: formData
                });

                const data = await response.json();
                
                if (response.ok) {
                    localStorage.setItem('token', data.access_token);
                    loginMessage.style.color = 'green';
                    loginMessage.textContent = 'Login successful!';
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1000);
                } else {
                    loginMessage.style.color = 'red';
                    loginMessage.textContent = data.detail || 'Login failed';
                }
            } catch (error) {
                loginMessage.style.color = 'red';
                loginMessage.textContent = 'Error connecting to server';
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