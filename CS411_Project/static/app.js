async function searchPrograms() {
    const major = document.getElementById('majorInput').value;
    const location = document.getElementById('locationInput').value;
    const params = new URLSearchParams();

    if (major) params.append('major', major);
    if (location) params.append('location', location);

    setStatus('Searching programs...');

    try {
        const res = await fetch('/api/programs/search?' + params.toString());
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        renderPrograms(data);
        setStatus(`Found ${data.length} programs.`);
    } catch (err) {
        console.error(err);
        setStatus('Error searching programs: ' + err.message);
    }
}

function renderPrograms(programs) {
    const tbody = document.getElementById('programTableBody');
    tbody.innerHTML = '';

    const userIdInput = document.getElementById('userIdInput');
    const userId = userIdInput.value || '1';

    programs.forEach(p => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${p.ProgramID}</td>
            <td>${p.ProgramName}</td>
            <td>${p.UniversityName}</td>
            <td>${p.Location}</td>
            <td>${p.MajorName}</td>
            <td>${p.DegreeType || ''}</td>
            <td>${p.MedianSalary || ''}</td>
            <td>
                <button onclick="addBookmark(${userId}, ${p.ProgramID})">
                    +
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function addBookmark(userId, programId) {
    setStatus(`Adding bookmark: user ${userId}, program ${programId}...`);
    try {
        const res = await fetch('/api/bookmarks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                program_id: programId
            })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'HTTP ' + res.status);
        setStatus('Bookmark added: ' + JSON.stringify(data));
        loadBookmarks(); // 刷新一下书签表
    } catch (err) {
        console.error(err);
        setStatus('Error adding bookmark: ' + err.message);
    }
}

async function loadBookmarks() {
    const userId = document.getElementById('userIdInput').value || '1';
    setStatus(`Loading bookmarks for user ${userId}...`);

    try {
        const res = await fetch(`/api/users/${userId}/bookmarks`);
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        renderBookmarks(data, userId);
        setStatus(`Loaded ${data.length} bookmarks for user ${userId}.`);
    } catch (err) {
        console.error(err);
        setStatus('Error loading bookmarks: ' + err.message);
    }
}

function renderBookmarks(bookmarks, userId) {
    const tbody = document.getElementById('bookmarkTableBody');
    tbody.innerHTML = '';

    bookmarks.forEach(p => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${p.ProgramID}</td>
            <td>${p.ProgramName}</td>
            <td>${p.UniversityName}</td>
            <td>${p.MajorName}</td>
            <td>${p.DegreeType || ''}</td>
            <td>${p.MedianSalary || ''}</td>
            <td>
                <button onclick="removeBookmark(${userId}, ${p.ProgramID})">
                    x
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function removeBookmark(userId, programId) {
    setStatus(`Removing bookmark: user ${userId}, program ${programId}...`);
    try {
        const res = await fetch('/api/bookmarks', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                program_id: programId
            })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'HTTP ' + res.status);
        setStatus('Bookmark removed.');
        loadBookmarks();
    } catch (err) {
        console.error(err);
        setStatus('Error removing bookmark: ' + err.message);
    }
}

function setStatus(text) {
    const box = document.getElementById('statusBox');
    box.textContent = text;
}
