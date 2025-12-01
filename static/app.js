async function searchPrograms() {
    const major = document.getElementById('majorInput').value.trim();
    const location = document.getElementById('locationInput').value.trim();
    const minSalary = document.getElementById('minSalarySearchInput').value.trim();

    const params = new URLSearchParams();
    if (major)    params.append('major', major);
    if (location) params.append('location', location);
    if (minSalary) params.append('min_salary', minSalary);

    if (!major && !location && !minSalary) {
        setStatus('Please enter at least one condition (major, location, or min salary).');
        return;
    }

    setStatus('Searching programs by conditions...');
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
        loadBookmarks(); 
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

// -------------------------------
// New: keyword search
// -------------------------------
async function keywordSearch() {
    const q = document.getElementById('keywordInput').value.trim();
    if (!q) {
        setStatus('Please enter a keyword.');
        return;
    }

    setStatus(`Searching by keyword "${q}"...`);
    try {
        const params = new URLSearchParams({ q });
        const res = await fetch('/api/programs/keyword-search?' + params.toString());
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        renderPrograms(data);
        setStatus(`Keyword search: found ${data.length} programs.`);
    } catch (err) {
        console.error(err);
        setStatus('Error in keyword search: ' + err.message);
    }
}


// -------------------------------
// Admin: CRUD for Program
// -------------------------------
async function loadAllPrograms() {
    setStatus('Loading all programs (admin)...');
    try {
        const res = await fetch('/api/programs');
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        renderAdminPrograms(data);
        setStatus(`Loaded ${data.length} programs.`);
    } catch (err) {
        console.error(err);
        setStatus('Error loading programs: ' + err.message);
    }
}

function renderAdminPrograms(programs) {
    const tbody = document.getElementById('adminProgramTableBody');
    if (!tbody) return; 
    tbody.innerHTML = '';

    programs.forEach(p => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${p.ProgramID}</td>
            <td>${p.ProgramName}</td>
            <td>${p.UniversityName || ''}</td>
            <td>${p.MajorName || ''}</td>
            <td>${p.DegreeType || ''}</td>
            <td>${p.MedianSalary || ''}</td>
            <td><button type="button" onclick="selectProgramAdmin(${p.ProgramID})">Select</button></td>
        `;
        tbody.appendChild(tr);
    });
}

async function selectProgramAdmin(programId) {
    setStatus(`Loading program ${programId}...`);
    try {
        const res = await fetch(`/api/programs/${programId}`);
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const p = await res.json();

        // 填充表单
        document.getElementById('adminProgramIdInput').value = p.ProgramID;
        document.getElementById('adminProgramNameInput').value = p.ProgramName || '';
        document.getElementById('adminUniversityIdInput').value = p.UniversityID || '';
        document.getElementById('adminMajorIdInput').value = p.MajorID || '';
        document.getElementById('adminDegreeTypeInput').value = p.DegreeType || '';
        document.getElementById('adminMedianSalaryInput').value = p.MedianSalary || '';

        setStatus(`Program ${programId} loaded into form.`);
    } catch (err) {
        console.error(err);
        setStatus('Error loading program: ' + err.message);
    }
}

async function createProgramAdmin() {
    const name = document.getElementById('adminProgramNameInput').value.trim();
    const university_id = document.getElementById('adminUniversityIdInput').value;
    const major_id = document.getElementById('adminMajorIdInput').value;
    const degree_type = document.getElementById('adminDegreeTypeInput').value.trim();
    const median_salary = document.getElementById('adminMedianSalaryInput').value;

    if (!name || !university_id || !major_id || !degree_type || !median_salary) {
        setStatus('Please fill in all fields to create a program.');
        return;
    }

    setStatus('Creating new program...');
    try {
        const res = await fetch('/api/programs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                university_id: Number(university_id),
                major_id: Number(major_id),
                degree_type,
                median_salary: Number(median_salary)
            })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || ('HTTP ' + res.status));

        setStatus('Program created: ' + JSON.stringify(data));
        // 清空 ID，表示当前表单是“新建状态”
        document.getElementById('adminProgramIdInput').value = '';
        loadAllPrograms();
    } catch (err) {
        console.error(err);
        setStatus('Error creating program: ' + err.message);
    }
}

async function updateProgramAdmin() {
    const program_id = document.getElementById('adminProgramIdInput').value;
    if (!program_id) {
        setStatus('Please select a program first.');
        return;
    }

    const name = document.getElementById('adminProgramNameInput').value.trim();
    const university_id = document.getElementById('adminUniversityIdInput').value;
    const major_id = document.getElementById('adminMajorIdInput').value;
    const degree_type = document.getElementById('adminDegreeTypeInput').value.trim();
    const median_salary = document.getElementById('adminMedianSalaryInput').value;

    const payload = {};
    if (name) payload.name = name;
    if (university_id) payload.university_id = Number(university_id);
    if (major_id) payload.major_id = Number(major_id);
    if (degree_type) payload.degree_type = degree_type;
    if (median_salary) payload.median_salary = Number(median_salary);

    if (Object.keys(payload).length === 0) {
        setStatus('No fields to update.');
        return;
    }

    setStatus(`Updating program ${program_id}...`);
    try {
        const res = await fetch(`/api/programs/${program_id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || ('HTTP ' + res.status));

        setStatus('Program updated: ' + JSON.stringify(data));
        loadAllPrograms();
    } catch (err) {
        console.error(err);
        setStatus('Error updating program: ' + err.message);
    }
}

async function deleteProgramAdmin() {
    const program_id = document.getElementById('adminProgramIdInput').value;
    if (!program_id) {
        setStatus('Please select a program first.');
        return;
    }

    if (!confirm(`Are you sure you want to delete program ${program_id}?`)) {
        return;
    }

    setStatus(`Deleting program ${program_id}...`);
    try {
        const res = await fetch(`/api/programs/${program_id}`, {
            method: 'DELETE'
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || ('HTTP ' + res.status));

        setStatus('Program deleted.');
        // 清空表单
        document.getElementById('adminProgramIdInput').value = '';
        document.getElementById('adminProgramNameInput').value = '';
        document.getElementById('adminUniversityIdInput').value = '';
        document.getElementById('adminMajorIdInput').value = '';
        document.getElementById('adminDegreeTypeInput').value = '';
        document.getElementById('adminMedianSalaryInput').value = '';

        loadAllPrograms();
    } catch (err) {
        console.error(err);
        setStatus('Error deleting program: ' + err.message);
    }
}

