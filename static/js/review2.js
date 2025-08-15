/* review2.js
   Page-specific script for Review 2.
*/

document.addEventListener('DOMContentLoaded', function() {
  // Load saved data (try review2, fallback to review1/3 if present)
  const data = window.loadSessionObject('review2_data');
  if (!data || Object.keys(data).length === 0) {
    // attempt to load from other reviews if exists
    const alt = window.loadSessionObject('review1_data') || window.loadSessionObject('review3_data');
    if (Object.keys(alt).length) window.loadFormToId('review2_data', 'form-data'); // populate available fields
  } else {
    window.loadFormToId('review2_data', 'form-data');
  }

  // Setup listeners
  document.querySelectorAll('.marks').forEach(input => {
    input.addEventListener('input', calculateTotals);
    input.addEventListener('change', function() {
      validateInput(this);
      calculateTotals();
    });
  });

  calculateTotals();
});

function validateInput(input) {
  const max = parseFloat(input.getAttribute('max')) || Infinity;
  const min = parseFloat(input.getAttribute('min')) || 0;
  let value = parseFloat(input.value);
  if (isNaN(value)) {
    input.value = '';
    input.classList.add('error');
    return false;
  }
  value = Math.max(min, Math.min(value, max));
  input.value = value;
  input.classList.remove('error');
  return true;
}

function calculateTotals() {
  for (let i = 1; i <= 4; i++) {
    let total = 0;
    let isValid = true;
    document.querySelectorAll(`.marks[data-member="${i}"]`).forEach(input => {
      const val = parseFloat(input.value);
      if (isNaN(val)) {
        isValid = false;
        input.classList.add('error');
      } else {
        total += val;
        input.classList.remove('error');
      }
    });
    const totalField = document.querySelector(`.total[name="2.${i}.s1"]`);
    if (totalField) {
      totalField.value = isValid ? total : 'Invalid';
      totalField.classList.toggle('error', !isValid);
    }
  }
}

function validateFormReview2() {
  return window.validateRequiredFields(['group_id', 'date']);
}

async function submitForm() {
  if (!validateFormReview2()) return;
  await window.submitPDFGeneric({
    endpoint: '/generate-pdf-review2',
    formId: 'form-data',
    submitBtnSelector: '#generate-pdf',
    downloadFilename: 'Review-II_Form.pdf'
  }).catch(()=>{});
}

function saveFormData() {
  window.saveFormById('review2_data', 'form-data');
}

function nextReview() {
  saveFormData();
  window.location.href = '/review3';
}

function previousReview() {
  saveFormData();
  window.location.href = '/review1';
}
