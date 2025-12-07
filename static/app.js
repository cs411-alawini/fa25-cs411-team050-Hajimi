// -------------------------------
// get current user id from local storage or redirect to login
// -------------------------------
function getCurrentUserIdOrRedirect() {
    const userId = localStorage.getItem("user_id");
    if (!userId) {
        window.location.href = "/login";
        throw new Error("Not logged in");
    }
    return userId;
}

// -------------------------------
// search programs by conditions
// -------------------------------
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

    const userId = getCurrentUserIdOrRedirect();

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

// -------------------------------
// Add bookmark
// -------------------------------
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
        if (!res.ok) throw new Error(data.error || ('HTTP ' + res.status));
        setStatus('Bookmark added.');
        loadBookmarks();
    } catch (err) {
        console.error(err);
        setStatus('Error adding bookmark: ' + err.message);
    }
}


async function loadBookmarks() {
    const userId = getCurrentUserIdOrRedirect();
    setStatus(`Loading bookmarks for user ${userId}...`);

    try {
        const res = await fetch(`/api/users/${userId}/bookmarks`);
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        renderBookmarks(data, userId);
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

async function clearAllBookmarks() {
    const userId = getCurrentUserIdOrRedirect();
    if (!confirm(`Clear ALL bookmarks for user ${userId}?`)) return;

    try {
        const res = await fetch(`/api/users/${userId}/bookmarks`, {
            method: 'DELETE'
        });
        const data = await res.json();
        setStatus(`Cleared ${data.deleted} bookmarks for user ${userId}.`);
        loadBookmarks();
    } catch (err) {
        console.error(err);
        setStatus('Error clearing bookmarks: ' + err.message);
    }
}


// -------------------------------
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

// Clear Search Programs table
function clearSearchResults() {
    document.getElementById("programTableBody").innerHTML = "";
    setStatus("Search results cleared.");
}


// --------------------------------------------------
// New: Procedure -- RecommendProgramsForUser
// --------------------------------------------------
async function loadRecommendations() {
    const userId = getCurrentUserIdOrRedirect();
    const minSalary = document.getElementById('minSalaryInput').value;
    const maxTuition = document.getElementById("maxTuitionInput").value;

    setStatus(`Loading recommended programs for user ${userId}...`);

    try {
        const res = await fetch(
            `/api/users/${userId}/recommend?min_salary=${minSalary}&max_tuition=${maxTuition}`
        );

        if (!res.ok) throw new Error("HTTP " + res.status);

        const data = await res.json();
        renderRecommendedPrograms(data);
        setStatus(`Loaded ${data.length} recommended programs.`);
    } catch (err) {
        console.error(err);
        setStatus("Error loading recommendations: " + err.message);
    }
}


function renderRecommendedPrograms(programs) {
    const tbody = document.getElementById('recommendedProgramsTableBody');
    tbody.innerHTML = '';

    const userId = getCurrentUserIdOrRedirect();

    programs.forEach(p => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${p.ProgramID}</td>
            <td>${p.ProgramName}</td>
            <td>${p.UniversityName}</td>
            <td>${p.MajorName}</td>
            <td>${p.DegreeType || ''}</td>
            <td>${p.MedianSalary ?? ''}</td>
            <td>${p.Tuition ?? ''}</td>
            <td>${p.AvgTuitionForMajor ?? ''}</td>
            <td>
                <button onclick="addBookmark(${userId}, ${p.ProgramID})">
                    +
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}


// Clear Recommended Programs table
function clearRecommendedResults() {
    document.getElementById("recommendedProgramsTableBody").innerHTML = "";
    setStatus("Recommended results cleared.");
}

document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("recommendBtn");
    if (btn) btn.addEventListener("click", loadRecommendations);
});



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
// -------------------------------
// New: Compare Programs
let selectedLeft = null;
let selectedRight = null;

async function searchCompare() {
    const q = document.getElementById("compareSearchInput").value.trim();
    if (!q) return;

    const res = await fetch(`/api/programs/keyword-search?q=${encodeURIComponent(q)}`);
    const data = await res.json();

    let html = "<table><tr><th>Name</th><th>Action</th></tr>";
    data.forEach(p => {
        html += `<tr>
                    <td>${p.ProgramName}</td>
                    <td><button onclick="addToCompare(${p.ProgramID})">+ Compare</button></td>
                 </tr>`;
    });
    html += "</table>";

    document.getElementById("compareSearchResults").innerHTML = html;
}

async function addToCompare(programID) {
    const res = await fetch(`/api/programs/${programID}`);
    const p = await res.json();

    const formatted = `
        <p><b>${p.ProgramName}</b></p>
        <p>Major: ${p.MajorName}</p>
        <p>University: ${p.UniversityName}</p>
        <p>Location: ${p.Location}</p>
        <p>Degree: ${p.DegreeType}</p>
        <p>Salary: ${p.MedianSalary}</p>
    `;

    if (!selectedLeft) {
        selectedLeft = p.ProgramID;
        document.getElementById("compareLeft").innerHTML = formatted;
    } 
    else if (!selectedRight) {
        selectedRight = p.ProgramID;
        document.getElementById("compareRight").innerHTML = formatted;
    }

    updateSaveButton();
}

async function saveComparison() {
    const userId = getCurrentUserIdOrRedirect();
    const note = document.getElementById("compareNote").value;

    const res = await fetch("/api/comparisons", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            user_id: userId,
            program1_id: selectedLeft,
            program2_id: selectedRight,
            note: note
        })
    });

    const data = await res.json();
    alert(data.status);

    // reset UI
    selectedLeft = null;
    selectedRight = null;
    document.getElementById("compareLeft").innerHTML = "";
    document.getElementById("compareRight").innerHTML = "";
    document.getElementById("compareNote").value = "";
    updateSaveButton();

    loadSavedComparisons();
}

function updateSaveButton() {
    const btn = document.getElementById("saveCompareBtn");
    btn.disabled = !(selectedLeft && selectedRight);
}

// Load saved comparisons for a user
async function loadSavedComparisons() {
    const userId = getCurrentUserIdOrRedirect();
    const container = document.getElementById("savedComparisons");

    try {
        const res = await fetch(`/api/comparisons/${userId}`);
        const data = await res.json();

        if (!Array.isArray(data)) {
            container.innerHTML = "<p>No comparisons found.</p>";
            return;
        }

        let html = `
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Program 1</th>
                    <th>Program 2</th>
                    <th>Note</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
        `;

        data.forEach(c => {
            html += `
                <tr>
                    <td>${c.Program1Name}</td>
                    <td>${c.Program2Name}</td>
                    <td>${c.NoteFromUser || "(none)"}</td>
                    <td><button class="delete-btn" onclick="deleteComparison(${c.ComparisonID})">Delete</button></td>
                </tr>
            `;
        });

        html += "</tbody></table>";
        container.innerHTML = html;

    } catch (err) {
        console.error(err);
        container.innerHTML = "<p>Error loading comparisons.</p>";
    }
}

async function deleteComparison(id) {
    if (!confirm("Delete this comparison?")) return;

    const res = await fetch(`/api/comparisons/${id}`, { method: "DELETE" });
    const data = await res.json();

    if (res.ok) {
        loadSavedComparisons();
    } else {
        alert(data.error);
    }
}



function clearLeftProgram() {
    selectedLeft = null;
    document.getElementById("compareLeft").innerHTML = "";
    updateSaveButton();
}

function clearRightProgram() {
    selectedRight = null;
    document.getElementById("compareRight").innerHTML = "";
    updateSaveButton();
}



// Clear Comparison search results
function clearCompareSearch() {
    document.getElementById("compareSearchResults").innerHTML = "";
    setStatus("Comparison search results cleared.");
}

// -------------------------------
// Transaction: auto bookmark top N recommended programs
// -------------------------------
async function autoBookmarkTopN() {
    const userId = getCurrentUserIdOrRedirect();
    const minSalary = document.getElementById('minSalaryInput').value || 60000;
    const topN = document.getElementById('autoBookmarkTopNInput').value || 5;

    setStatus(`Running transaction: auto-bookmark top ${topN} programs for user ${userId}...`);

    try {
        const res = await fetch(`/api/users/${userId}/auto-bookmark`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                min_salary: Number(minSalary),
                top_n: Number(topN)
            })
        });

        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.error || ('HTTP ' + res.status));
        }

        setStatus(
            `Transaction OK. Selected ${data.selected_count}, `
            + `inserted ${data.inserted_count} bookmarks. `
            + (data.avg_median_salary
                ? `Avg median salary = ${data.avg_median_salary}.`
                : '')
        );

        loadBookmarks();
    } catch (err) {
        console.error(err);
        setStatus("Error in auto-bookmark transaction: " + err.message);
    }
}


// -------------------------------
// Navigate to Alert Page
// -------------------------------
function goToAlertPage() {
    window.location.href = "/alert";
}

//-------------------------------
// load alerts
function renderAlerts(alerts, userId) {
    const tbody = document.getElementById("alertTableBody");
    tbody.innerHTML = "";

    alerts.forEach(a => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${a.Message}</td>
            <td>
                <button class="delete-btn" onclick="deleteAlert(${userId}, ${a.AlertID})">
                    Delete
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}


async function loadAlerts(userId) {
    try {
        const res = await fetch(`/api/users/${userId}/alerts`);
        const alerts = await res.json();
        renderAlerts(alerts, userId);
    } catch (err) {
        console.error(err);
    }
}



// -------------------------------
// Delete alert
async function deleteAlert(userId, alertId) {
    const res = await fetch(`/api/users/${userId}/alerts/${alertId}`, {
        method: "DELETE"
    });

    const data = await res.json();

    if (res.ok) {
        alert("Alert deleted.");
        loadAlerts(userId);
    } else {
        alert("Delete failed: " + data.error);
    }
}

// -------------------------------
// Search alerts by user
function searchAlertsByUser() {
    const userId = getCurrentUserIdOrRedirect();

    if (!userId) {
        alert("Please enter a valid User ID.");
        return;
    }

    loadAlerts(userId);
}

// -------------------------------
// log in page
// -------------------------------
function getCurrentUserIdOrRedirect() {
    const userId = localStorage.getItem("user_id");
    if (!userId) {
        window.location.href = "/login";
        throw new Error("Not logged in");
    }
    return userId;
}

async function login() {
    const username = document.getElementById("loginUsername").value.trim();
    const password = document.getElementById("loginPassword").value.trim();
    const statusElem = document.getElementById("loginStatus");

    if (!username || !password) {
        statusElem.textContent = "Please enter username and password.";
        return;
    }

    try {
        const res = await fetch("/api/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (res.ok && data.status === "success") {
            localStorage.setItem("user_id", data.user_id);
            localStorage.setItem("username", data.username || username);

            statusElem.style.color = "green";
            statusElem.textContent = "Login successful! Redirecting...";

            setTimeout(() => {
                window.location.href = "/";
            }, 800);
        } else {
            statusElem.style.color = "red";
            statusElem.textContent = data.error || "Login failed.";
        }
    } catch (err) {
        console.error(err);
        statusElem.style.color = "red";
        statusElem.textContent = "Login error: " + err.message;
    }
}

function logout() {
    localStorage.removeItem("user_id");
    localStorage.removeItem("username");
    window.location.href = "/login";
}

/*
user info functions
*/
async function loadUserInfo() {
    const userId = getCurrentUserIdOrRedirect();
    const container = document.getElementById("userInfoContainer");

    try {
        const res = await fetch(`/api/users/${userId}/info`);
        const data = await res.json();

        container.innerHTML = `
            <p><strong>Username:</strong> ${data.Username}</p>
            <p><strong>Email:</strong> ${data.Email}</p>
            <p><strong>Preferred Major:</strong> ${data.PreferredMajor ?? "(none)"}</p>
            <p><strong>Preferred Location:</strong> ${data.PreferredLocation ?? "(none)"}</p>
            <p><strong>Preferred Job:</strong> ${data.PreferredJob ?? "(none)"}</p>
        `;
    } catch (err) {
        container.innerHTML = "<p>Error loading user info.</p>";
    }
}

async function changePassword() {
    const userId = getCurrentUserIdOrRedirect();
    const newPw = document.getElementById("newPasswordInput").value;

    if (!newPw) {
        alert("Enter a new password");
        return;
    }

    const res = await fetch(`/api/users/${userId}/password`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ new_password: newPw })
    });

    if (res.ok) {
        alert("Password updated successfully.");
    } else {
        alert("Unable to update password.");
    }
}

async function loadMajorsAndJobs(selectedMajor, selectedJob) {
    const majorSelect = document.getElementById("majorSelect");
    const jobSelect = document.getElementById("jobSelect");

    const majorRes = await fetch("/api/majors");
    const majors = await majorRes.json();
    majorSelect.innerHTML = majors.map(m =>
        `<option value="${m.MajorID}" ${m.MajorID == selectedMajor ? "selected" : ""}>
            ${m.MajorName}
         </option>`
    ).join("");

    const jobRes = await fetch("/api/jobs");
    const jobs = await jobRes.json();
    jobSelect.innerHTML = jobs.map(j =>
        `<option value="${j.JobID}" ${j.JobID == selectedJob ? "selected" : ""}>
            ${j.JobTitle}
         </option>`
    ).join("");
}

async function startEditPreferences() {
    const userId = getCurrentUserIdOrRedirect();

    const res = await fetch(`/api/users/${userId}/info`);
    const data = await res.json();

    document.getElementById("editPrefSection").style.display = "block";

    loadMajorsAndJobs(data.PreferredMajorID, data.PreferredJobID);
}

function cancelEditPreferences() {
    document.getElementById("editPrefSection").style.display = "none";
}

async function savePreferences() {
    const userId = getCurrentUserIdOrRedirect();
    const majorId = document.getElementById("majorSelect").value;
    const jobId = document.getElementById("jobSelect").value;

    await fetch(`/api/users/${userId}/preferences`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            preferred_major: majorId,
            preferred_job: jobId
        })
    });

    alert("Preferences updated!");

    document.getElementById("editPrefSection").style.display = "none";

    loadUserInfo();
}

// New: Admin Transaction to update major-job links
async function runMajorJobTransaction() {
    const majorId = document.getElementById("txnMajorSelect").value;
    const job1 = document.getElementById("txnJob1Select").value;
    const job2 = document.getElementById("txnJob2Select").value;
    const threshold = document.getElementById("txnThresholdInput").value || 15000;

    if (!majorId || !job1 || !job2) {
        setStatus("Please select Major, Job1 and Job2.");
        return;
    }

    setStatus("Running...");

    try {
        const res = await fetch("/api/admin/update-major-jobs", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                major_id: Number(majorId),
                job1: Number(job1),
                job2: Number(job2),
                threshold: Number(threshold)
            })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.error);

        // Status now only shows ONE line
        setStatus("Transaction OK");

        // Update Result Table
        updateTxnResultTable(data);

        // If switched, refresh Job1 list
        loadMajorJobs(majorId);

    } catch (err) {
        setStatus("Error: " + err.message);
    }
}

function updateTxnResultTable(data) {
    const tbody = document.getElementById("txnResultBody");

    const fmt = (v) => {
        if (v === null || v === undefined) return "-";
        const n = Number(v);
        if (Number.isNaN(n)) return "-";
        return n.toFixed(0);
    };

    tbody.innerHTML = `
        <tr>
            <td>${data.major && data.major.name ? data.major.name : "-"}</td>
            <td>${data.job1 && data.job1.title ? data.job1.title : "-"}</td>
            <td>${data.job2 && data.job2.title ? data.job2.title : "-"}</td>
            <td>${fmt(data.major && data.major.avg_salary)}</td>
            <td>${fmt(data.job1 && data.job1.avg_salary)}</td>
            <td>${fmt(data.job2 && data.job2.avg_salary)}</td>
            <td>${fmt(data.diff_major_job1)}</td>
            <td>${data.switched ? "YES" : "NO"}</td>
        </tr>
    `;
}




async function loadMajorsForTransaction() {
    const majorSelect = document.getElementById("txnMajorSelect");
    const res = await fetch("/api/majors");
    const data = await res.json();

    majorSelect.innerHTML = data.map(m =>
        `<option value="${m.MajorID}">${m.MajorName}</option>`
    ).join("");
}

async function loadJobsForTransaction() {
    const job2 = document.getElementById("txnJob2Select");

    const res = await fetch("/api/jobs");
    const data = await res.json();

    const options = data.map(j =>
        `<option value="${j.JobID}">${j.JobTitle}</option>`
    ).join("");

    job2.innerHTML = options;
}


document.addEventListener("DOMContentLoaded", () => {
    loadMajorsForTransaction();
    loadJobsForTransaction();

    const majorSelect = document.getElementById("txnMajorSelect");
    majorSelect.addEventListener("change", () => {
        const majorId = majorSelect.value;
        loadMajorJobs(majorId);
    });

    setTimeout(() => {
        if (majorSelect.value) loadMajorJobs(majorSelect.value);
    }, 200);
});

async function loadMajorJobs(majorId) {
    const tbody = document.getElementById("majorJobsTableBody");
    tbody.innerHTML = "<tr><td>Loading...</td></tr>";

    const job1Select = document.getElementById("txnJob1Select");

    try {
        const res = await fetch(`/api/admin/major-jobs/${majorId}`);
        const jobs = await res.json();

        // Render current job list
        tbody.innerHTML = "";
        if (jobs.length === 0) {
            tbody.innerHTML = `<tr><td>No jobs linked to this major.</td></tr>`;
        } else {
            jobs.forEach(j => {
                const tr = document.createElement("tr");
                tr.innerHTML = `<td>${j.JobTitle}</td>`;
                tbody.appendChild(tr);
            });
        }

        // ALSO UPDATE Job1 dropdown (only jobs linked to this major)
        job1Select.innerHTML =
            jobs.map(j => `<option value="${j.JobID}">${j.JobTitle}</option>`).join("");

    } catch (err) {
        tbody.innerHTML = `<tr><td>Error loading jobs.</td></tr>`;
        console.error(err);
    }
}






