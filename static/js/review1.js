/* review1.js
   Page-specific script for Review 1.
   Assumes common.js already loaded.
*/

document.addEventListener('DOMContentLoaded', function() {
  // Load saved form data (if any)
  window.loadFormToId('review1_data', 'form-data');

  // Attach mark listeners
  document.querySelectorAll('.marks').forEach(input => {
    input.addEventListener('input', calculateTotals);
    input.addEventListener('change', function() {
      const max = parseFloat(this.getAttribute('max')) || Infinity;
      if (parseFloat(this.value) > max) this.value = max;
      calculateTotals();
    });
  });

  // Initial totals
  calculateTotals();
});

// Review1: calculate totals and write to .total[name="1.{i}.s1"]
function calculateTotals() {
  for (let i = 1; i <= 4; i++) {
    let total = 0;
    document.querySelectorAll(`.marks[data-member="${i}"]`).forEach(input => {
      total += parseFloat(input.value) || 0;
    });
    const totalEl = document.querySelector(`.total[name="1.${i}.s1"]`);
    if (totalEl) totalEl.value = total;
  }
}

function validateFormReview1() {
  return window.validateRequiredFields(['group_id', 'date']);
}

async function generatePDF() {
  if (!validateFormReview1()) return;
  await window.submitPDFGeneric({
    endpoint: '/generate-pdf-review1',
    formId: 'form-data',
    submitBtnSelector: '#generate-pdf',
    downloadFilename: 'Review-I_Form.pdf'
  }).catch(()=>{}); // errors already alerted in helper
}

function nextReview() {
  window.saveFormById('review1_data', 'form-data');
  window.location.href = '/review2';
}
