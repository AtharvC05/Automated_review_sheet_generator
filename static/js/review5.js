/* review5.js
   Final review page - collects totals from previous review pages and calculates final scores.
*/

document.addEventListener('DOMContentLoaded', function() {
  loadReviewData();
  calculateFinalTotals();
});

function loadReviewData() {
  const review1Data = window.loadSessionObject('review1_data');
  const review2Data = window.loadSessionObject('review2_data');
  const review3Data = window.loadSessionObject('review3_data');
  const review4Data = window.loadSessionObject('review4_data');

  // group id fallback
  const groupId = review1Data.group_id || review2Data.group_id || review3Data.group_id || review4Data.group_id || '';
  const gidEl = document.getElementById('group_id');
  if (gidEl) gidEl.value = groupId;

  // Review I totals (keys like "1.1.s1")
  const r1 = (k) => review1Data[k] || 0;
  const r2 = (k) => review2Data[k] || 0;
  const r3 = (k) => review3Data[k] || 0;
  const r4 = (k) => review4Data[k] || 0;

  // These element IDs are from your original page; keep them present in the HTML
  const rev1Els = ['review1-student1','review1-student2','review1-student3','review1-student4'];
  const rev2Els = ['review2-student1','review2-student2','review2-student3','review2-student4'];
  const rev3Els = ['review3-student1','review3-student2','review3-student3','review3-student4'];
  const rev4Els = ['review4-student1','review4-student2','review4-student3','review4-student4'];

  // Populate R1
  try {
    document.getElementById(rev1Els[0]).value = r1['1.1.s1'] || r1['1.1.s1'] === 0 ? r1['1.1.s1'] : 0;
    document.getElementById(rev1Els[1]).value = r1['1.2.s1'] || 0;
    document.getElementById(rev1Els[2]).value = r1['1.3.s1'] || 0;
    document.getElementById(rev1Els[3]).value = r1['1.4.s1'] || 0;
  } catch(e){}

  // Populate R2
  try {
    document.getElementById(rev2Els[0]).value = r2['2.1.s1'] || 0;
    document.getElementById(rev2Els[1]).value = r2['2.2.s1'] || 0;
    document.getElementById(rev2Els[2]).value = r2['2.3.s1'] || 0;
    document.getElementById(rev2Els[3]).value = r2['2.4.s1'] || 0;
  } catch(e){}

  // Populate R3 (keys used in review3 were f81,f82,f83,f84)
  try {
    document.getElementById(rev3Els[0]).value = r3['f81'] || 0;
    document.getElementById(rev3Els[1]).value = r3['f82'] || 0;
    document.getElementById(rev3Els[2]).value = r3['f83'] || 0;
    document.getElementById(rev3Els[3]).value = r3['f84'] || 0;
  } catch(e){}

  // Populate R4 (keys like f4.1.s1)
  try {
    document.getElementById(rev4Els[0]).value = r4['f4.1.s1'] || 0;
    document.getElementById(rev4Els[1]).value = r4['f4.2.s1'] || 0;
    document.getElementById(rev4Els[2]).value = r4['f4.3.s1'] || 0;
    document.getElementById(rev4Els[3]).value = r4['f4.4.s1'] || 0;
  } catch(e){}
}

function calculateFinalTotals() {
  for (let i = 1; i <= 4; i++) {
    const r1 = parseFloat(document.getElementById(`review1-student${i}`).value) || 0;
    const r2 = parseFloat(document.getElementById(`review2-student${i}`).value) || 0;
    const r3 = parseFloat(document.getElementById(`review3-student${i}`).value) || 0;
    const r4 = parseFloat(document.getElementById(`review4-student${i}`).value) || 0;
    const total = r1 + r2 + r3 + r4;
    const finalEl = document.getElementById(`final-student${i}`);
    if (finalEl) finalEl.value = total;
  }
}

function saveFormData() {
  const obj = {
    group_id: (document.getElementById('group_id') || {value:''}).value,
    final_comments: (document.getElementById('comments') || {value:''}).value
  };
  for (let i=1;i<=4;i++){
    for (let j=1;j<=4;j++){
      const el = document.getElementById(`review${i}-student${j}`);
      obj[`review${i}_${j}`] = el ? el.value : '';
    }
  }
  sessionStorage.setItem('review5_data', JSON.stringify(obj));
}

function previousReview() {
  saveFormData();
  window.location.href = '/review4';
}

async function submitForm() {
  try {
    const submitBtn = document.getElementById('generate-pdf');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Generating PDF...';
    }
    saveFormData();
    await window.submitPDFGeneric({
      endpoint: '/generate-pdf-review5',
      formId: 'form-data',
      submitBtnSelector: '#generate-pdf',
      downloadFilename: 'Final_Review_Summary.pdf'
    });
  } catch(e) {
    // error already handled in helper
  } finally {
    const submitBtn = document.getElementById('generate-pdf');
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Generate Final PDF';
    }
  }
}
