/* review4.js
   Page-specific script for Review 4.
*/

document.addEventListener('DOMContentLoaded', function() {
  window.loadFormToId('review4_data', 'form-data');
  setupEventListeners();
  calculateTotals();
});

function setupEventListeners() {
  document.querySelectorAll('.marks').forEach(input => {
    input.addEventListener('input', handleMarkInput);
  });

  const groupIdInput = document.getElementById('group_id');
  if (groupIdInput) groupIdInput.addEventListener('change', fetchGroupDetails);
}

function handleMarkInput(e) {
  const input = e.target;
  const max = parseFloat(input.getAttribute('max')) || Infinity;
  const value = parseFloat(input.value) || 0;
  if (value > max) input.value = max;
  calculateTotals();
}

function calculateTotals() {
  for (let i = 1; i <= 4; i++) {
    let total = 0;
    let valid = true;
    document.querySelectorAll(`.marks[data-member="${i}"]`).forEach(input => {
      const v = parseFloat(input.value);
      if (!isNaN(v)) total += v;
      else {
        valid = false;
        input.classList.add('error');
      }
    });
    const totalField = document.querySelector(`.total[name="f4.${i}.s1"]`);
    if (totalField) {
      totalField.value = valid ? total : 'Invalid';
      totalField.classList.toggle('error', !valid);
    }
  }
}

function validateFormReview4() {
  return window.validateRequiredFields(['group_id', 'date']);
}

async function submitForm() {
  if (!validateFormReview4()) return;
  await window.submitPDFGeneric({
    endpoint: '/generate-pdf-review4',
    formId: 'form-data',
    submitBtnSelector: 'button[onclick="submitForm()"]',
    downloadFilename: 'Review-IV_Form.pdf'
  }).catch(()=>{});
}

async function fetchGroupDetails() {
  const groupIdEl = document.getElementById('group_id');
  if (!groupIdEl) return;
  const groupId = groupIdEl.value.trim();
  if (!groupId) return;
  try {
    const resp = await fetch(`/fetch/${groupId}`);
    if (!resp.ok) throw new Error(await resp.text());
    const data = await resp.json();
    populateForm(data);
  } catch (err) {
    console.error('Failed to fetch group details:', err);
    alert('Failed to load group details. Please check the group ID.');
  }
}

function populateForm(data) {
  const fields = ['project_title','guide_name','mentor_name','mentor_email','mentor_mobile'];
  fields.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = data[id] || '';
  });

  if (data.members && Array.isArray(data.members)) {
    data.members.forEach((member, idx) => {
      const roll = document.getElementById(`roll_no_${idx+1}`);
      const name = document.getElementById(`student_name_${idx+1}`);
      const contact = document.getElementById(`contact_details_${idx+1}`);
      if (roll) roll.value = member.roll_no || '';
      if (name) name.value = member.student_name || '';
      if (contact) contact.value = member.contact_details || '';
    });
  }
}

function saveFormData() {
  window.saveFormById('review4_data', 'form-data');
}

function nextReview() {
  saveFormData();
  window.location.href = '/review5';
}

function previousReview() {
  saveFormData();
  window.location.href = '/review3';
}
