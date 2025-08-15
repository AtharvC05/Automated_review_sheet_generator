/* common.js
   Shared helpers: header scroll behavior, menu toggle, session storage helpers,
   PDF submit helper, and small validators.
   Keep this file included on every review page BEFORE the page-specific script.
*/

/* ---------- Header Hide/Show on Scroll ---------- */
(function(){
  let lastScrollTop = 0;
  const scrollThreshold = 5;
  let isHeaderVisible = true;
  let scrollTimer = null;

  function handleScroll() {
    const header = document.querySelector('.page-header');
    if (!header) return;
    const currentScrollTop = window.pageYOffset || document.documentElement.scrollTop;
    if (Math.abs(currentScrollTop - lastScrollTop) < scrollThreshold) return;

    if (currentScrollTop > lastScrollTop && currentScrollTop > 100 && isHeaderVisible) {
      header.classList.add('hidden');
      isHeaderVisible = false;
    } else if (currentScrollTop < lastScrollTop && !isHeaderVisible) {
      header.classList.remove('hidden');
      isHeaderVisible = true;
    }

    if (currentScrollTop > 80) header.classList.add('scrolled');
    else header.classList.remove('scrolled');

    lastScrollTop = currentScrollTop;
  }

  function throttledScroll() {
    if (scrollTimer) return;
    scrollTimer = setTimeout(() => {
      handleScroll();
      scrollTimer = null;
    }, 10);
  }

  // Expose init function to attach listener
  window.commonInitScroll = function() {
    window.addEventListener('scroll', throttledScroll, { passive: true });
  };
})();

/* ---------- Menu toggle & highlight ---------- */
(function(){
  let menuOpen = false;

  function toggleMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const menuDropdown = document.getElementById('menuDropdown');
    if (!menuToggle || !menuDropdown) return;

    menuOpen = !menuOpen;
    if (menuOpen) {
      menuToggle.classList.add('active');
      menuDropdown.classList.add('show');
    } else {
      menuToggle.classList.remove('active');
      menuDropdown.classList.remove('show');
    }
  }

  function setupMenuListeners() {
    // outside click
    document.addEventListener('click', function(event) {
      const menuContainer = document.querySelector('.menu-container');
      if (!menuContainer) return;
      if (!menuContainer.contains(event.target) && menuOpen) {
        toggleMenu();
      }
    });

    // Escape key
    document.addEventListener('keydown', function(event) {
      if (event.key === 'Escape' && menuOpen) toggleMenu();
    });

    // Highlight current path
    const currentPath = window.location.pathname;
    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
      try {
        if (item.getAttribute('href') === currentPath) item.classList.add('current');
      } catch (e) { /* ignore */ }
    });

    // Expose toggle to global (page markup can call toggleMenu())
    window.toggleMenu = toggleMenu;
  }

  window.commonInitMenu = setupMenuListeners;
})();

/* ---------- Session storage helpers (form-level) ---------- */
(function(){
  /**
   * Save a whole form's fields (name or id) into sessionStorage under `key`.
   * Uses FormData to capture inputs with name attributes. Also includes elements
   * that have id but no name (their id used as key).
   *
   * Usage: saveFormById('review1_data', 'form-data')
   */
  window.saveFormById = function(key, formId) {
    try {
      const form = document.getElementById(formId);
      if (!form) {
        // Fallback: save all inputs on page
        const inputs = document.querySelectorAll('input,select,textarea');
        const obj = {};
        inputs.forEach(el => {
          const k = el.name || el.id;
          if (!k) return;
          obj[k] = el.value;
        });
        sessionStorage.setItem(key, JSON.stringify(obj));
        return;
      }
      const fd = new FormData(form);
      const obj = Object.fromEntries(fd.entries());
      // Also add inputs without name (use id)
      form.querySelectorAll('input:not([name]), textarea:not([name]), select:not([name])').forEach(el => {
        if (el.id) obj[el.id] = el.value;
      });
      sessionStorage.setItem(key, JSON.stringify(obj));
    } catch (e) {
      console.error('saveFormById error', e);
    }
  };

  /**
   * Load saved data from sessionStorage key and populate a form (by id).
   * It sets by name first, then by id if name not found.
   *
   * Usage: loadFormToId('review1_data', 'form-data')
   */
  window.loadFormToId = function(key, formId) {
    try {
      const raw = sessionStorage.getItem(key);
      if (!raw) return {};
      const data = JSON.parse(raw);
      const form = document.getElementById(formId);
      Object.entries(data).forEach(([k, v]) => {
        if (form) {
          // Try query by name then by id
          const elByName = form.querySelector(`[name="${CSS.escape(k)}"]`);
          if (elByName) {
            elByName.value = v;
            return;
          }
        }
        // fallback to document-level
        const elByNameDoc = document.querySelector(`[name="${CSS.escape(k)}"]`);
        if (elByNameDoc) {
          elByNameDoc.value = v;
          return;
        }
        const elById = document.getElementById(k);
        if (elById) elById.value = v;
      });
      return data;
    } catch (e) {
      console.error('loadFormToId error', e);
      return {};
    }
  };

  /**
   * Return parsed object from sessionStorage by key
   */
  window.loadSessionObject = function(key) {
    try {
      return JSON.parse(sessionStorage.getItem(key) || '{}');
    } catch (e) {
      console.error('loadSessionObject error', e);
      return {};
    }
  };
})();

/* ---------- Generic PDF submit helper ---------- */
(function(){
  /**
   * submitPDFGeneric(options)
   * options: {
   *   endpoint: string (POST url),
   *   formId: string (id of form to read data from),
   *   submitBtnSelector: string (selector to disable / change text) optional,
   *   downloadFilename: string (filename to save) optional
   * }
   */
  window.submitPDFGeneric = async function(options = {}) {
    const { endpoint, formId='form-data', submitBtnSelector='#generate-pdf', downloadFilename } = options;
    try {
      const submitBtn = document.querySelector(submitBtnSelector);
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Generating PDF...';
      }

      const form = document.getElementById(formId);
      const formData = form ? new FormData(form) : new FormData();
      const payload = Object.fromEntries(formData.entries());
      const resp = await fetch(endpoint, {
        method: 'POST',
        body: JSON.stringify(payload),
        headers: { 'Content-Type': 'application/json' }
      });
      if (!resp.ok) throw new Error(await resp.text());
      const blob = await resp.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = downloadFilename || 'download.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF generation failed:', err);
      alert(`Failed to generate PDF: ${err.message || err}`);
      throw err;
    } finally {
      const submitBtn = document.querySelector(submitBtnSelector);
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Generate PDF';
      }
    }
  };
})();

/* ---------- Small helpers ---------- */
(function(){
  window.validateRequiredFields = function(ids = []) {
    let ok = true;
    ids.forEach(id => {
      const el = document.getElementById(id);
      if (!el) return; // if field not on the page, ignore
      if (!el.value || !el.value.toString().trim()) {
        el.classList.add('error');
        ok = false;
      } else {
        el.classList.remove('error');
      }
    });
    if (!ok) alert('Please fill all required fields');
    return ok;
  };
})();

/* ---------- Auto-init common bits on DOM ready ---------- */
document.addEventListener('DOMContentLoaded', function() {
  // init scroll and menu/highlight by default
  try { window.commonInitScroll(); } catch(e) {}
  try { window.commonInitMenu(); } catch(e) {}
});
