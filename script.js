async function fetchTelemetry() {
    try {
        // Points to the Vercel serverless function
        const res = await fetch('/api');
        const data = await res.json();
        
        document.getElementById('userCount').textContent = data.totalUsers;
        
        const list = document.getElementById('userList');
        list.innerHTML = '';
        
        if (data.users.length === 0) {
            list.innerHTML = '<li class="loading">No users currently online.</li>';
        } else {
            data.users.forEach(user => {
                const li = document.createElement('li');
                li.textContent = user;
                list.appendChild(li);
            });
        }
    } catch (e) {
        console.error("Failed to fetch telemetry:", e);
    }
}

// Fetch immediately and then every 10 seconds
fetchTelemetry();
setInterval(fetchTelemetry, 10000);
