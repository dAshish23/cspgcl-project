/**
 * CSPGCL Management System - Frontend Controller
 * Chhattisgarh State Power Generation Company Limited (CSPGCL), Korba
 * Backed by RESTful API endpoints (Python Flask + SQLite/MySQL)
 */

// Application State
const state = {
  coalRecords: [],
  dieselRecords: [],
  employees: [],
  attendanceRecords: [],
  summary: null,
  currentTab: 'tab-dashboard'
};

// ==============================================================================
// Initialization on Page Load
// ==============================================================================
document.addEventListener('DOMContentLoaded', () => {
  initClock();
  initTabNavigation();
  initPresetDates();
  initSearchAndFilters();
  refreshAllData();

  // Polling / Periodic refresh every 30 seconds
  setInterval(refreshAllData, 30000);
});

// Live Clock
function initClock() {
  const clockEl = document.getElementById('liveClock');
  const updateClock = () => {
    const now = new Date();
    clockEl.textContent = now.toLocaleTimeString() + ' | ' + now.toLocaleDateString();
  };
  updateClock();
  setInterval(updateClock, 1000);
}

// Preset today's date in form date pickers
function initPresetDates() {
  const today = new Date().toISOString().split('T')[0];
  const nowIso = new Date().toISOString().slice(0, 16);
  
  const coalDate = document.getElementById('coalRecordedOn');
  if (coalDate) coalDate.value = today;

  const dieselDate = document.getElementById('dieselRecordedOn');
  if (dieselDate) dieselDate.value = today;

  const attIn = document.getElementById('attCheckIn');
  if (attIn) attIn.value = nowIso;
}

// Global Refresh Button
document.getElementById('btnRefreshAll')?.addEventListener('click', () => {
  refreshAllData();
  showToast('All system modules refreshed.', 'info');
});

function refreshAllData() {
  fetchHealth();
  fetchSummary();
  fetchCoal();
  fetchDiesel();
  fetchEmployees();
  fetchAttendance();
  fetchDbTablesInfo();
}

// ==============================================================================
// Tab Navigation
// ==============================================================================
function initTabNavigation() {
  const tabButtons = document.querySelectorAll('.nav-tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      switchTab(targetTab);
    });
  });
}

function switchTab(tabId) {
  state.currentTab = tabId;

  // Toggle buttons
  document.querySelectorAll('.nav-tab-btn').forEach(btn => {
    if (btn.getAttribute('data-tab') === tabId) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  // Toggle panes
  document.querySelectorAll('.tab-pane').forEach(pane => {
    if (pane.id === tabId) {
      pane.classList.add('active');
    } else {
      pane.classList.remove('active');
    }
  });

  // Special triggers for certain tabs
  if (tabId === 'tab-reports') {
    updateReportsView();
  }
}

// ==============================================================================
// API: System Health Check (Table 5.1)
// ==============================================================================
async function fetchHealth() {
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    const badge = document.getElementById('dbStatusBadge');
    const text = document.getElementById('dbStatusText');

    if (data.status === 'healthy') {
      badge.className = 'status-badge status-online';
      text.textContent = `Online (${data.db_type.toUpperCase()})`;
    } else {
      badge.className = 'status-badge status-offline';
      text.textContent = 'Disconnected';
    }
  } catch (err) {
    console.error('Health check failed:', err);
  }
}

// ==============================================================================
// API: Dashboard Summary (Fig 6.1)
// ==============================================================================
async function fetchSummary() {
  try {
    const res = await fetch('/api/summary');
    const json = await res.json();
    if (!json.success) return;

    state.summary = json.data;
    const s = state.summary;

    // Update KPI values
    document.getElementById('dashCoalNet').textContent = Number(s.coal.net_stock_mt).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
    document.getElementById('dashCoalIn').textContent = Number(s.coal.total_in_mt).toLocaleString();
    document.getElementById('dashCoalOut').textContent = Number(s.coal.total_out_mt).toLocaleString();

    document.getElementById('dashDieselNet').textContent = Number(s.diesel.net_stock_litres).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
    document.getElementById('dashDieselIn').textContent = Number(s.diesel.total_in_litres).toLocaleString();
    document.getElementById('dashDieselOut').textContent = Number(s.diesel.total_out_litres).toLocaleString();

    document.getElementById('dashTotalEmp').textContent = s.total_employees;
    document.getElementById('dashPresentToday').textContent = s.present_today;
    document.getElementById('dashActiveOnDuty').textContent = s.active_on_duty;

    // Badges in sidebar
    document.getElementById('navCoalBadge').textContent = `${Math.round(s.coal.net_stock_mt)} MT`;
    document.getElementById('navDieselBadge').textContent = `${Math.round(s.diesel.net_stock_litres)} L`;
    document.getElementById('navEmpBadge').textContent = s.total_employees;
    document.getElementById('navAttBadge').textContent = `${s.present_today} on duty`;

    // Gauges (assuming 15,000 MT max coal storage buffer & 50,000 L diesel tank capacity)
    const coalCap = 15000;
    const dieselCap = 50000;
    const coalPct = Math.min(100, Math.max(0, (s.coal.net_stock_mt / coalCap) * 100));
    const dieselPct = Math.min(100, Math.max(0, (s.diesel.net_stock_litres / dieselCap) * 100));

    document.getElementById('gaugeCoalVal').textContent = Number(s.coal.net_stock_mt).toLocaleString(undefined, {minimumFractionDigits: 2});
    document.getElementById('gaugeCoalBar').style.width = `${coalPct}%`;

    document.getElementById('gaugeDieselVal').textContent = Number(s.diesel.net_stock_litres).toLocaleString(undefined, {minimumFractionDigits: 2});
    document.getElementById('gaugeDieselBar').style.width = `${dieselPct}%`;

  } catch (err) {
    console.error('Error fetching summary:', err);
  }
}

// ==============================================================================
// Coal Storage Module (Fig 6.2, Table 4.1, Table 5.1)
// ==============================================================================
async function fetchCoal() {
  try {
    const res = await fetch('/api/coal');
    const json = await res.json();
    if (!json.success) return;

    state.coalRecords = json.data;
    const summary = json.summary;

    // Update Coal Banner
    document.getElementById('coalBannerNet').innerHTML = `${Number(summary.net_stock_mt).toLocaleString(undefined, {minimumFractionDigits: 2})} <span class="inv-unit">MT</span>`;
    document.getElementById('coalBannerIn').innerHTML = `${Number(summary.total_in_mt).toLocaleString(undefined, {minimumFractionDigits: 2})} <span class="inv-unit">MT</span>`;
    document.getElementById('coalBannerOut').innerHTML = `${Number(summary.total_out_mt).toLocaleString(undefined, {minimumFractionDigits: 2})} <span class="inv-unit">MT</span>`;
    document.getElementById('coalBannerCount').textContent = summary.total_transactions;

    renderCoalTable(state.coalRecords);
    renderRecentCoal(state.coalRecords.slice(0, 5));
  } catch (err) {
    console.error('Error fetching coal:', err);
  }
}

function renderCoalTable(records) {
  const tbody = document.getElementById('coalTableBody');
  if (!records || records.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No coal transaction records found.</td></tr>';
    return;
  }

  tbody.innerHTML = records.map(r => `
    <tr>
      <td class="font-mono">#${r.id}</td>
      <td><strong>${r.recorded_on}</strong></td>
      <td>
        <span class="type-pill ${r.type === 'IN' ? 'type-in' : 'type-out'}">
          ${r.type === 'IN' ? '▲ IN' : '▼ OUT'}
        </span>
      </td>
      <td class="font-mono" style="font-weight: 700; color: ${r.type === 'IN' ? '#15803d' : '#b91c1c'};">
        ${r.type === 'IN' ? '+' : '-'}${Number(r.quantity_mt).toFixed(2)} MT
      </td>
      <td>${escapeHtml(r.remarks || '—')}</td>
      <td class="text-muted text-sm">${r.created_at || '—'}</td>
      <td class="text-muted text-sm">${r.updated_at || '—'}</td>
      <td class="text-right">
        <button class="btn btn-outline btn-xs" onclick="editCoalRecord(${r.id})">Edit</button>
        <button class="btn btn-danger btn-xs" onclick="deleteCoalRecord(${r.id})">Delete</button>
      </td>
    </tr>
  `).join('');
}

function renderRecentCoal(records) {
  const tbody = document.getElementById('dashCoalRecentBody');
  if (!records || records.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No recent coal transactions.</td></tr>';
    return;
  }
  tbody.innerHTML = records.map(r => `
    <tr>
      <td>${r.recorded_on}</td>
      <td>
        <span class="type-pill ${r.type === 'IN' ? 'type-in' : 'type-out'}">${r.type}</span>
      </td>
      <td class="font-mono" style="font-weight: 600;">${Number(r.quantity_mt).toFixed(2)} MT</td>
      <td class="text-muted">${escapeHtml(r.remarks || '—')}</td>
    </tr>
  `).join('');
}

async function handleCoalSubmit(e) {
  e.preventDefault();
  const editId = document.getElementById('coalEditId').value;
  const payload = {
    type: document.getElementById('coalType').value,
    quantity_mt: parseFloat(document.getElementById('coalQuantity').value),
    recorded_on: document.getElementById('coalRecordedOn').value,
    remarks: document.getElementById('coalRemarks').value
  };

  try {
    let res;
    if (editId) {
      res = await fetch(`/api/coal/${editId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } else {
      res = await fetch('/api/coal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    }

    const data = await res.json();
    if (res.ok && data.success) {
      showToast(editId ? 'Coal record updated successfully' : 'Coal transaction logged successfully');
      closeModal('modal-coal');
      document.getElementById('coalForm').reset();
      document.getElementById('coalEditId').value = '';
      fetchCoal();
      fetchSummary();
    } else {
      showToast(data.error || 'Failed to save coal record', 'danger');
    }
  } catch (err) {
    showToast('Network or server error', 'danger');
  }
}

function editCoalRecord(id) {
  const rec = state.coalRecords.find(r => r.id === id);
  if (!rec) return;

  document.getElementById('coalEditId').value = rec.id;
  document.getElementById('coalType').value = rec.type;
  document.getElementById('coalQuantity').value = rec.quantity_mt;
  document.getElementById('coalRecordedOn').value = rec.recorded_on;
  document.getElementById('coalRemarks').value = rec.remarks || '';
  document.getElementById('modalCoalTitle').textContent = `Edit Coal Record #${rec.id}`;

  openModal('modal-coal');
}

async function deleteCoalRecord(id) {
  if (!confirm(`Are you sure you want to delete Coal record #${id}?`)) return;
  try {
    const res = await fetch(`/api/coal/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast('Coal record deleted successfully');
      fetchCoal();
      fetchSummary();
    } else {
      showToast(data.error || 'Failed to delete record', 'danger');
    }
  } catch (err) {
    showToast('Network error while deleting', 'danger');
  }
}

// ==============================================================================
// Diesel Storage Module (Fig 6.3, Table 4.2, Table 5.1)
// ==============================================================================
async function fetchDiesel() {
  try {
    const res = await fetch('/api/diesel');
    const json = await res.json();
    if (!json.success) return;

    state.dieselRecords = json.data;
    const summary = json.summary;

    // Update Diesel Banner
    document.getElementById('dieselBannerNet').innerHTML = `${Number(summary.net_stock_litres).toLocaleString(undefined, {minimumFractionDigits: 2})} <span class="inv-unit">Litres</span>`;
    document.getElementById('dieselBannerIn').innerHTML = `${Number(summary.total_in_litres).toLocaleString(undefined, {minimumFractionDigits: 2})} <span class="inv-unit">Litres</span>`;
    document.getElementById('dieselBannerOut').innerHTML = `${Number(summary.total_out_litres).toLocaleString(undefined, {minimumFractionDigits: 2})} <span class="inv-unit">Litres</span>`;
    document.getElementById('dieselBannerCount').textContent = summary.total_transactions;

    renderDieselTable(state.dieselRecords);
  } catch (err) {
    console.error('Error fetching diesel:', err);
  }
}

function renderDieselTable(records) {
  const tbody = document.getElementById('dieselTableBody');
  if (!records || records.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No diesel transaction records found.</td></tr>';
    return;
  }

  tbody.innerHTML = records.map(r => `
    <tr>
      <td class="font-mono">#${r.id}</td>
      <td><strong>${r.recorded_on}</strong></td>
      <td>
        <span class="type-pill ${r.type === 'IN' ? 'type-in' : 'type-out'}">
          ${r.type === 'IN' ? '▲ IN' : '▼ OUT'}
        </span>
      </td>
      <td class="font-mono" style="font-weight: 700; color: ${r.type === 'IN' ? '#15803d' : '#b91c1c'};">
        ${r.type === 'IN' ? '+' : '-'}${Number(r.quantity_litres).toFixed(2)} L
      </td>
      <td>${escapeHtml(r.remarks || '—')}</td>
      <td class="text-muted text-sm">${r.created_at || '—'}</td>
      <td class="text-muted text-sm">${r.updated_at || '—'}</td>
      <td class="text-right">
        <button class="btn btn-outline btn-xs" onclick="editDieselRecord(${r.id})">Edit</button>
        <button class="btn btn-danger btn-xs" onclick="deleteDieselRecord(${r.id})">Delete</button>
      </td>
    </tr>
  `).join('');
}

async function handleDieselSubmit(e) {
  e.preventDefault();
  const editId = document.getElementById('dieselEditId').value;
  const payload = {
    type: document.getElementById('dieselType').value,
    quantity_litres: parseFloat(document.getElementById('dieselQuantity').value),
    recorded_on: document.getElementById('dieselRecordedOn').value,
    remarks: document.getElementById('dieselRemarks').value
  };

  try {
    let res;
    if (editId) {
      res = await fetch(`/api/diesel/${editId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } else {
      res = await fetch('/api/diesel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    }

    const data = await res.json();
    if (res.ok && data.success) {
      showToast(editId ? 'Diesel record updated successfully' : 'Diesel transaction logged successfully');
      closeModal('modal-diesel');
      document.getElementById('dieselForm').reset();
      document.getElementById('dieselEditId').value = '';
      fetchDiesel();
      fetchSummary();
    } else {
      showToast(data.error || 'Failed to save diesel record', 'danger');
    }
  } catch (err) {
    showToast('Network or server error', 'danger');
  }
}

function editDieselRecord(id) {
  const rec = state.dieselRecords.find(r => r.id === id);
  if (!rec) return;

  document.getElementById('dieselEditId').value = rec.id;
  document.getElementById('dieselType').value = rec.type;
  document.getElementById('dieselQuantity').value = rec.quantity_litres;
  document.getElementById('dieselRecordedOn').value = rec.recorded_on;
  document.getElementById('dieselRemarks').value = rec.remarks || '';
  document.getElementById('modalDieselTitle').textContent = `Edit Diesel Record #${rec.id}`;

  openModal('modal-diesel');
}

async function deleteDieselRecord(id) {
  if (!confirm(`Are you sure you want to delete Diesel record #${id}?`)) return;
  try {
    const res = await fetch(`/api/diesel/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast('Diesel record deleted successfully');
      fetchDiesel();
      fetchSummary();
    } else {
      showToast(data.error || 'Failed to delete record', 'danger');
    }
  } catch (err) {
    showToast('Network error while deleting', 'danger');
  }
}

// ==============================================================================
// Employees Module (Fig 6.4, Table 4.3, Listing 5.1)
// ==============================================================================
async function fetchEmployees() {
  try {
    const res = await fetch('/api/employees');
    const json = await res.json();
    if (!json.success) return;

    state.employees = json.data;
    renderEmployeesTable(state.employees);
    populateEmployeeDropdowns(state.employees);
  } catch (err) {
    console.error('Error fetching employees:', err);
  }
}

function renderEmployeesTable(records) {
  const tbody = document.getElementById('empTableBody');
  if (!records || records.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No employee records registered.</td></tr>';
    return;
  }

  tbody.innerHTML = records.map(e => `
    <tr>
      <td class="font-mono"><strong>#${e.emp_id}</strong></td>
      <td><strong>${escapeHtml(e.name)}</strong></td>
      <td>${escapeHtml(e.designation || '—')}</td>
      <td><span class="badge badge-info">${escapeHtml(e.department || '—')}</span></td>
      <td class="font-mono">${escapeHtml(e.contact_number || '—')}</td>
      <td>${e.date_of_joining || '—'}</td>
      <td class="text-muted text-sm">${e.created_at ? e.created_at.split(' ')[0] : '—'}</td>
      <td class="text-right">
        <button class="btn btn-outline btn-xs" onclick="viewEmployeeDetails(${e.emp_id})">Profile</button>
        <button class="btn btn-outline btn-xs" onclick="editEmployeeRecord(${e.emp_id})">Edit</button>
        <button class="btn btn-danger btn-xs" onclick="deleteEmployeeRecord(${e.emp_id})">Delete</button>
      </td>
    </tr>
  `).join('');
}

function populateEmployeeDropdowns(employees) {
  const attSelect = document.getElementById('attEmpSelect');
  const quickSelect = document.getElementById('quickPunchEmpSelect');
  const filterSelect = document.getElementById('attEmpFilter');

  const options = employees.map(e => `
    <option value="${e.emp_id}">${e.name} (${e.designation || 'Staff'} - ${e.department || 'Dept'})</option>
  `).join('');

  if (attSelect) {
    attSelect.innerHTML = '<option value="">-- Choose Employee --</option>' + options;
  }
  if (quickSelect) {
    quickSelect.innerHTML = options;
  }
  if (filterSelect) {
    filterSelect.innerHTML = '<option value="">All Employees</option>' + options;
  }
}

async function handleEmployeeSubmit(e) {
  e.preventDefault();
  const editId = document.getElementById('empEditId').value;
  const payload = {
    name: document.getElementById('empName').value.trim(),
    designation: document.getElementById('empDesignation').value.trim(),
    department: document.getElementById('empDepartment').value,
    contact_number: document.getElementById('empContact').value.trim(),
    date_of_joining: document.getElementById('empJoining').value
  };

  try {
    let res;
    if (editId) {
      res = await fetch(`/api/employees/${editId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } else {
      res = await fetch('/api/employees', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    }

    const data = await res.json();
    if (res.ok && data.success) {
      showToast(editId ? 'Employee updated successfully' : 'Employee registered successfully');
      closeModal('modal-employee');
      document.getElementById('employeeForm').reset();
      document.getElementById('empEditId').value = '';
      fetchEmployees();
      fetchSummary();
    } else {
      showToast(data.error || 'Failed to save employee', 'danger');
    }
  } catch (err) {
    showToast('Network error while saving employee', 'danger');
  }
}

function editEmployeeRecord(id) {
  const emp = state.employees.find(e => e.emp_id === id);
  if (!emp) return;

  document.getElementById('empEditId').value = emp.emp_id;
  document.getElementById('empName').value = emp.name;
  document.getElementById('empDesignation').value = emp.designation || '';
  document.getElementById('empDepartment').value = emp.department || 'Coal Handling';
  document.getElementById('empContact').value = emp.contact_number || '';
  document.getElementById('empJoining').value = emp.date_of_joining || '';
  document.getElementById('modalEmpTitle').textContent = `Edit Employee #${emp.emp_id}`;

  openModal('modal-employee');
}

async function deleteEmployeeRecord(id) {
  if (!confirm(`Warning: Deleting Employee #${id} will also CASCADE delete all their attendance records. Proceed?`)) return;
  try {
    const res = await fetch(`/api/employees/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast('Employee deleted successfully');
      fetchEmployees();
      fetchAttendance();
      fetchSummary();
    } else {
      showToast(data.error || 'Failed to delete employee', 'danger');
    }
  } catch (err) {
    showToast('Network error while deleting', 'danger');
  }
}

async function viewEmployeeDetails(empId) {
  try {
    const res = await fetch(`/api/employees/${empId}`);
    const json = await res.json();
    if (!json.success) return;

    const emp = json.data;
    const history = json.attendance_history || [];

    document.getElementById('empDetailTitle').textContent = `${emp.name} (EMP-${emp.emp_id})`;
    document.getElementById('empProfileCard').innerHTML = `
      <div class="kpi-card emp-theme" style="margin-bottom: 0;">
        <div class="kpi-data">
          <div style="font-size: 18px; font-weight: 700;">${emp.name}</div>
          <div class="text-muted">${emp.designation || 'Staff'} • <strong>${emp.department || 'General'}</strong></div>
          <div style="margin-top: 8px; font-size: 13px;">
            <span>📞 Contact: <strong>${emp.contact_number || 'N/A'}</strong></span> | 
            <span>📅 Joined: <strong>${emp.date_of_joining || 'N/A'}</strong></span>
          </div>
        </div>
      </div>
    `;

    const tbody = document.getElementById('empDetailAttBody');
    if (history.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No attendance logs found for this employee.</td></tr>';
    } else {
      tbody.innerHTML = history.map(h => `
        <tr>
          <td>${h.check_in.split(' ')[0]}</td>
          <td class="font-mono">${h.check_in.split(' ')[1] || h.check_in}</td>
          <td class="font-mono">${h.check_out ? (h.check_out.split(' ')[1] || h.check_out) : '<span class="badge badge-warning">Clocked In</span>'}</td>
          <td><span class="badge ${getStatusBadgeClass(h.status)}">${h.status}</span></td>
        </tr>
      `).join('');
    }

    openModal('modal-emp-details');
  } catch (err) {
    showToast('Failed to load employee details', 'danger');
  }
}

// ==============================================================================
// Attendance Module (Fig 6.5, Table 4.4, Listing 4.3 & Listing 5.2)
// ==============================================================================
async function fetchAttendance() {
  try {
    const date = document.getElementById('attDateFilter')?.value;
    const empId = document.getElementById('attEmpFilter')?.value;
    const status = document.getElementById('attStatusFilter')?.value;

    let url = '/api/attendance?';
    if (date) url += `date=${encodeURIComponent(date)}&`;
    if (empId) url += `emp_id=${encodeURIComponent(empId)}&`;
    if (status) url += `status=${encodeURIComponent(status)}&`;

    const res = await fetch(url);
    const json = await res.json();
    if (!json.success) return;

    state.attendanceRecords = json.data;
    renderAttendanceTable(state.attendanceRecords);

    // Also populate dashboard recent attendance with today's items
    const today = new Date().toISOString().split('T')[0];
    const todays = state.attendanceRecords.filter(a => a.check_in && a.check_in.startsWith(today)).slice(0, 6);
    renderRecentAttendance(todays.length > 0 ? todays : state.attendanceRecords.slice(0, 6));

  } catch (err) {
    console.error('Error fetching attendance:', err);
  }
}

function renderAttendanceTable(records) {
  const tbody = document.getElementById('attTableBody');
  if (!records || records.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">No attendance records match the criteria.</td></tr>';
    return;
  }

  tbody.innerHTML = records.map(a => `
    <tr>
      <td class="font-mono">#${a.attendance_id}</td>
      <td><strong>${escapeHtml(a.employee_name)}</strong> <small class="text-muted">(#${a.emp_id})</small></td>
      <td><span class="badge badge-info">${escapeHtml(a.department || '—')}</span></td>
      <td class="font-mono">${a.check_in || '—'}</td>
      <td class="font-mono">
        ${a.check_out ? a.check_out : '<span class="badge badge-warning">Active On Duty</span>'}
      </td>
      <td>
        <span class="badge ${getStatusBadgeClass(a.status)}">${a.status}</span>
      </td>
      <td class="text-muted text-sm">${a.created_at || '—'}</td>
      <td class="text-right">
        ${!a.check_out ? `<button class="btn btn-secondary btn-xs" onclick="quickClockOutSpecific(${a.attendance_id}, ${a.emp_id})">Punch Out</button>` : ''}
        <button class="btn btn-outline btn-xs" onclick="editAttendanceRecord(${a.attendance_id})">Edit</button>
        <button class="btn btn-danger btn-xs" onclick="deleteAttendanceRecord(${a.attendance_id})">Delete</button>
      </td>
    </tr>
  `).join('');
}

function renderRecentAttendance(records) {
  const tbody = document.getElementById('dashAttRecentBody');
  if (!records || records.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No attendance records for today.</td></tr>';
    return;
  }
  tbody.innerHTML = records.map(a => `
    <tr>
      <td><strong>${escapeHtml(a.employee_name)}</strong></td>
      <td><span class="badge badge-info">${escapeHtml(a.department || '—')}</span></td>
      <td class="font-mono text-sm">${a.check_in ? a.check_in.split(' ')[1] : '—'}</td>
      <td>
        <span class="badge ${getStatusBadgeClass(a.status)}">${a.status}</span>
      </td>
    </tr>
  `).join('');
}

function getStatusBadgeClass(status) {
  if (status === 'Present') return 'badge-success';
  if (status === 'Absent') return 'badge-danger';
  if (status === 'Half-Day') return 'badge-warning';
  return 'badge-info';
}

async function handleAttendanceSubmit(e) {
  e.preventDefault();
  const editId = document.getElementById('attEditId').value;
  const payload = {
    emp_id: parseInt(document.getElementById('attEmpSelect').value),
    check_in: document.getElementById('attCheckIn').value,
    check_out: document.getElementById('attCheckOut').value || null,
    status: document.getElementById('attStatus').value
  };

  try {
    let res;
    if (editId) {
      res = await fetch(`/api/attendance/${editId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } else {
      res = await fetch('/api/attendance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    }

    const data = await res.json();
    if (res.ok && data.success) {
      showToast(editId ? 'Attendance record updated successfully' : 'Attendance record created');
      closeModal('modal-attendance');
      document.getElementById('attendanceForm').reset();
      document.getElementById('attEditId').value = '';
      fetchAttendance();
      fetchSummary();
    } else {
      showToast(data.error || 'Failed to save attendance record', 'danger');
    }
  } catch (err) {
    showToast('Network error', 'danger');
  }
}

function editAttendanceRecord(id) {
  const rec = state.attendanceRecords.find(a => a.attendance_id === id);
  if (!rec) return;

  document.getElementById('attEditId').value = rec.attendance_id;
  document.getElementById('attEmpSelect').value = rec.emp_id;
  document.getElementById('attCheckIn').value = rec.check_in ? rec.check_in.replace(' ', 'T').slice(0, 16) : '';
  document.getElementById('attCheckOut').value = rec.check_out ? rec.check_out.replace(' ', 'T').slice(0, 16) : '';
  document.getElementById('attStatus').value = rec.status || 'Present';
  document.getElementById('modalAttTitle').textContent = `Edit Attendance Record #${rec.attendance_id}`;

  openModal('modal-attendance');
}

async function deleteAttendanceRecord(id) {
  if (!confirm(`Are you sure you want to delete Attendance record #${id}?`)) return;
  try {
    const res = await fetch(`/api/attendance/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast('Attendance record deleted');
      fetchAttendance();
      fetchSummary();
    } else {
      showToast(data.error || 'Failed to delete record', 'danger');
    }
  } catch (err) {
    showToast('Network error while deleting', 'danger');
  }
}

// Quick Punch In & Out Handlers
async function submitQuickCheckIn() {
  const empId = document.getElementById('quickPunchEmpSelect').value;
  if (!empId) {
    showToast('Please select an employee first', 'warning');
    return;
  }
  try {
    const res = await fetch('/api/attendance/check-in', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ emp_id: parseInt(empId) })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(`Clocked IN employee #${empId} successfully!`, 'success');
      closeModal('modal-quick-attendance');
      fetchAttendance();
      fetchSummary();
    } else {
      showToast(data.error || 'Check-in failed', 'danger');
    }
  } catch (err) {
    showToast('Network error during check-in', 'danger');
  }
}

async function submitQuickCheckOut() {
  const empId = document.getElementById('quickPunchEmpSelect').value;
  if (!empId) {
    showToast('Please select an employee first', 'warning');
    return;
  }
  try {
    const res = await fetch('/api/attendance/check-out', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ emp_id: parseInt(empId) })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(`Clocked OUT employee #${empId} successfully!`, 'success');
      closeModal('modal-quick-attendance');
      fetchAttendance();
      fetchSummary();
    } else {
      showToast(data.error || 'No active check-in found today for this employee', 'danger');
    }
  } catch (err) {
    showToast('Network error during check-out', 'danger');
  }
}

async function quickClockOutSpecific(attendanceId, empId) {
  const nowStr = new Date().toISOString().replace('T', ' ').slice(0, 19);
  try {
    const res = await fetch(`/api/attendance/${attendanceId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ check_out: nowStr })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      showToast(`Recorded checkout for employee #${empId}`);
      fetchAttendance();
      fetchSummary();
    } else {
      showToast(data.error || 'Failed to checkout', 'danger');
    }
  } catch (err) {
    showToast('Network error', 'danger');
  }
}

function clearAttendanceFilters() {
  document.getElementById('attDateFilter').value = '';
  document.getElementById('attEmpFilter').value = '';
  document.getElementById('attStatusFilter').value = '';
  fetchAttendance();
}

// ==============================================================================
// Search & Filter Bindings
// ==============================================================================
function initSearchAndFilters() {
  // Coal Search & Type Filter
  const coalSearch = document.getElementById('coalSearchInput');
  const coalType = document.getElementById('coalTypeFilter');
  const filterCoal = () => {
    const term = coalSearch.value.toLowerCase();
    const type = coalType.value;
    const filtered = state.coalRecords.filter(r => {
      const matchTerm = (r.remarks && r.remarks.toLowerCase().includes(term)) ||
                        r.recorded_on.includes(term) ||
                        String(r.id).includes(term);
      const matchType = !type || r.type === type;
      return matchTerm && matchType;
    });
    renderCoalTable(filtered);
  };
  coalSearch?.addEventListener('input', filterCoal);
  coalType?.addEventListener('change', filterCoal);

  // Diesel Search & Type Filter
  const dieselSearch = document.getElementById('dieselSearchInput');
  const dieselType = document.getElementById('dieselTypeFilter');
  const filterDiesel = () => {
    const term = dieselSearch.value.toLowerCase();
    const type = dieselType.value;
    const filtered = state.dieselRecords.filter(r => {
      const matchTerm = (r.remarks && r.remarks.toLowerCase().includes(term)) ||
                        r.recorded_on.includes(term) ||
                        String(r.id).includes(term);
      const matchType = !type || r.type === type;
      return matchTerm && matchType;
    });
    renderDieselTable(filtered);
  };
  dieselSearch?.addEventListener('input', filterDiesel);
  dieselType?.addEventListener('change', filterDiesel);

  // Employee Search & Dept Filter
  const empSearch = document.getElementById('empSearchInput');
  const empDept = document.getElementById('empDeptFilter');
  const filterEmp = () => {
    const term = empSearch.value.toLowerCase();
    const dept = empDept.value;
    const filtered = state.employees.filter(e => {
      const matchTerm = e.name.toLowerCase().includes(term) ||
                        (e.designation && e.designation.toLowerCase().includes(term)) ||
                        String(e.emp_id).includes(term);
      const matchDept = !dept || e.department === dept;
      return matchTerm && matchDept;
    });
    renderEmployeesTable(filtered);
  };
  empSearch?.addEventListener('input', filterEmp);
  empDept?.addEventListener('change', filterEmp);

  // Attendance Filters
  document.getElementById('attDateFilter')?.addEventListener('change', fetchAttendance);
  document.getElementById('attEmpFilter')?.addEventListener('change', fetchAttendance);
  document.getElementById('attStatusFilter')?.addEventListener('change', fetchAttendance);
}

// ==============================================================================
// Reports & Logs Module (Fig 6.9)
// ==============================================================================
function updateReportsView() {
  document.querySelectorAll('.reportTimestamp').forEach(el => {
    el.textContent = new Date().toLocaleString();
  });

  if (state.summary) {
    const s = state.summary;
    document.getElementById('repCoalIn').textContent = Number(s.coal.total_in_mt).toLocaleString();
    document.getElementById('repCoalOut').textContent = Number(s.coal.total_out_mt).toLocaleString();
    document.getElementById('repCoalNet').textContent = Number(s.coal.net_stock_mt).toLocaleString(undefined, {minimumFractionDigits: 2});

    document.getElementById('repDieselIn').textContent = Number(s.diesel.total_in_litres).toLocaleString();
    document.getElementById('repDieselOut').textContent = Number(s.diesel.total_out_litres).toLocaleString();
    document.getElementById('repDieselNet').textContent = Number(s.diesel.net_stock_litres).toLocaleString(undefined, {minimumFractionDigits: 2});

    document.getElementById('repEmpCount').textContent = s.total_employees;
    document.getElementById('repEmpPresent').textContent = s.present_today;
    document.getElementById('repEmpActive').textContent = s.active_on_duty;
    const turnout = s.total_employees > 0 ? Math.round((s.present_today / s.total_employees) * 100) : 0;
    document.getElementById('repTurnout').textContent = `${turnout}%`;
  }

  // Populate report attendance listing
  const repTbody = document.getElementById('repAttBody');
  if (!state.attendanceRecords || state.attendanceRecords.length === 0) {
    repTbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No attendance logs available.</td></tr>';
  } else {
    repTbody.innerHTML = state.attendanceRecords.slice(0, 15).map(a => `
      <tr>
        <td><strong>${escapeHtml(a.employee_name)}</strong></td>
        <td>${escapeHtml(a.department || '—')}</td>
        <td>${escapeHtml(a.designation || '—')}</td>
        <td class="font-mono">${a.check_in}</td>
        <td class="font-mono">${a.check_out || '<span class="badge badge-warning">On Duty</span>'}</td>
        <td><span class="badge ${getStatusBadgeClass(a.status)}">${a.status}</span></td>
      </tr>
    `).join('');
  }
}

// ==============================================================================
// REST API & Database Query Explorer (Fig 6.6, Fig 6.7, Fig 6.8)
// ==============================================================================
async function testSelectedApi() {
  const endpoint = document.getElementById('apiEndpointSelector').value;
  const viewer = document.getElementById('apiResponseViewer');
  const statusBadge = document.getElementById('apiStatusBadge');

  viewer.textContent = `Calling ${endpoint}...`;

  try {
    const startTime = performance.now();
    const res = await fetch(endpoint);
    const duration = Math.round(performance.now() - startTime);
    const data = await res.json();

    statusBadge.textContent = `${res.status} ${res.statusText} (${duration}ms)`;
    statusBadge.className = res.ok ? 'text-success' : 'text-danger';
    viewer.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    statusBadge.textContent = 'Error';
    statusBadge.className = 'text-danger';
    viewer.textContent = `Fetch error: ${err.message}`;
  }
}

function copyApiOutput() {
  const viewer = document.getElementById('apiResponseViewer');
  navigator.clipboard.writeText(viewer.textContent)
    .then(() => showToast('API JSON copied to clipboard!'))
    .catch(() => showToast('Could not copy to clipboard', 'warning'));
}

// Presets for SQL runner
const SQL_PRESETS = {
  coal_calc: `SELECT 
  SUM(CASE WHEN type = 'IN' THEN quantity_mt ELSE 0 END) - 
  SUM(CASE WHEN type = 'OUT' THEN quantity_mt ELSE 0 END) AS net_stock_mt 
FROM coal_storage;`,
  diesel_calc: `SELECT 
  SUM(CASE WHEN type = 'IN' THEN quantity_litres ELSE 0 END) - 
  SUM(CASE WHEN type = 'OUT' THEN quantity_litres ELSE 0 END) AS net_stock_litres 
FROM diesel_storage;`,
  join_att: `SELECT e.name, e.department, a.check_in, a.check_out, a.status 
FROM attendance a 
JOIN employees e ON a.emp_id = e.emp_id 
ORDER BY a.check_in DESC 
LIMIT 10;`,
  all_emp: `SELECT emp_id, name, designation, department, contact_number, date_of_joining 
FROM employees 
ORDER BY emp_id ASC;`,
  recent_tx: `SELECT 'COAL' AS fuel, recorded_on, type, quantity_mt AS quantity, remarks 
FROM coal_storage 
UNION ALL 
SELECT 'DIESEL' AS fuel, recorded_on, type, quantity_litres AS quantity, remarks 
FROM diesel_storage 
ORDER BY recorded_on DESC 
LIMIT 10;`
};

function loadPresetSql() {
  const sel = document.getElementById('sqlPresetSelector').value;
  if (SQL_PRESETS[sel]) {
    document.getElementById('sqlQueryInput').value = SQL_PRESETS[sel];
  }
}

async function runSqlRunnerQuery() {
  const query = document.getElementById('sqlQueryInput').value.trim();
  const meta = document.getElementById('sqlResultMeta');
  const table = document.getElementById('sqlDynamicTable');

  if (!query) {
    showToast('Please enter a SQL query', 'warning');
    return;
  }

  meta.textContent = 'Executing query...';

  try {
    const res = await fetch('/api/raw-query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    const result = await res.json();

    if (!res.ok || !result.success) {
      meta.innerHTML = `<span class="text-danger">Error: ${result.error || 'Query failed'}</span>`;
      table.innerHTML = '';
      return;
    }

    meta.textContent = `Returned ${result.row_count} rows in response.`;

    if (result.row_count === 0) {
      table.innerHTML = '<thead><tr><th>Result</th></tr></thead><tbody><tr><td>Query returned 0 rows.</td></tr></tbody>';
      return;
    }

    const cols = result.columns;
    let headerHtml = '<thead><tr>' + cols.map(c => `<th>${escapeHtml(c)}</th>`).join('') + '</tr></thead>';
    let rowsHtml = '<tbody>' + result.data.map(row => {
      return '<tr>' + cols.map(c => `<td>${escapeHtml(String(row[c] !== null ? row[c] : 'NULL'))}</td>`).join('') + '</tr>';
    }).join('') + '</tbody>';

    table.innerHTML = headerHtml + rowsHtml;
  } catch (err) {
    meta.innerHTML = `<span class="text-danger">Execution error: ${err.message}</span>`;
  }
}

async function fetchDbTablesInfo() {
  try {
    const res = await fetch('/api/db-tables');
    const json = await res.json();
    if (!json.success) return;

    const grid = document.getElementById('dbTablesGrid');
    if (!grid) return;

    grid.innerHTML = Object.entries(json.tables).map(([tableName, info]) => {
      const colList = info.columns.map(col => `
        <div style="font-size: 11px; padding: 2px 0; display: flex; justify-content: space-between;">
          <span class="font-mono">${col.name}</span>
          <span class="text-muted font-mono">${col.type} ${col.pk ? '<strong>(PK)</strong>' : ''}</span>
        </div>
      `).join('');

      return `
        <div class="table-schema-card">
          <div class="table-schema-title">
            <span>${tableName}</span>
            <span class="badge badge-primary">${info.row_count} rows</span>
          </div>
          <div class="schema-col-list">
            ${colList}
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    console.error('Error fetching table schema:', err);
  }
}

// ==============================================================================
// CSV Export Utility
// ==============================================================================
function exportTableToCSV(tableId, filename) {
  const table = document.getElementById(tableId);
  if (!table) return;

  const rows = [];
  for (let i = 0; i < table.rows.length; i++) {
    const row = [];
    const cells = table.rows[i].cells;
    // Skip the last column if it's actions
    const maxCols = cells.length > 0 && cells[cells.length - 1].classList.contains('text-right') ? cells.length - 1 : cells.length;

    for (let j = 0; j < maxCols; j++) {
      let text = cells[j].innerText.replace(/(\r\n|\n|\r)/gm, '').trim();
      text = text.replace(/"/g, '""');
      row.push(`"${text}"`);
    }
    rows.push(row.join(','));
  }

  const csvContent = 'data:text/csv;charset=utf-8,' + encodeURIComponent(rows.join('\n'));
  const link = document.createElement('a');
  link.setAttribute('href', csvContent);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast(`Exported ${filename} successfully!`);
}

// ==============================================================================
// Modal Control
// ==============================================================================
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add('show');
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('show');
}

// Close modals when clicking outside
window.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-backdrop')) {
    e.target.classList.remove('show');
  }
});

// ==============================================================================
// Toast Notifications
// ==============================================================================
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${escapeHtml(message)}</span>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Helper to sanitize HTML
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

