document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login.html';
        return;
    }

    // Fetch skills and populate the dropdown
    async function fetchSkills() {
        try {
            const response = await fetch('http://localhost:8000/skills/search');
            const skills = await response.json();
            const skillSelect = document.getElementById('skillId');

            skills.forEach(skill => {
                const option = document.createElement('option');
                option.value = skill.id;
                option.textContent = `${skill.name}`;
                skillSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching skills:', error);
        }
    }

    fetchSkills();

    // Fetch versions based on selected skill and populate the dropdown
    document.getElementById('skillId').addEventListener('change', async function() {
        const skillName = this.options[this.selectedIndex].text;
        const versionSelect = document.getElementById('skillVersion');
        versionSelect.innerHTML = '<option value="" disabled selected>Select a version</option>'; // Reset version dropdown

        try {
            const response = await fetch(`http://localhost:8000/skills/${skillName}/versions`);
            const versions = await response.json();

            versions.forEach(version => {
                const option = document.createElement('option');
                option.value = version;
                option.textContent = version;
                versionSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching skill versions:', error);
        }
    });


    // Handle new guide submission
    document.getElementById('addIssueForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const message = document.getElementById('message');

        try {
            const response = await fetch(`http://localhost:8000/guides`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: formData.get('issueTitle'),
                    description: formData.get('issueDescription'),
                    skill_id: formData.get('skillId'),
                    user_id: token
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                message.style.color = 'green';
                message.textContent = 'Guide added successfully';
                this.reset();
            } else {
                message.style.color = 'red';
                message.textContent = data.detail || 'Error adding Guide';
            }
        } catch (error) {
            message.style.color = 'red';
            message.textContent = 'Error connecting to server';
        }
    });

    // Handle logout
    document.getElementById('logoutLink').addEventListener('click', function(e) {
        e.preventDefault();
        localStorage.removeItem('token');
        window.location.href = '/';
    });
});