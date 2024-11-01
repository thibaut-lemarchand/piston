// Configuration
const CONFIG = {
    RELOAD_DELAY: 2000,
    TOASTR_OPTIONS: {
      closeButton: true,
      debug: false,
      newestOnTop: false,
      progressBar: true,
      positionClass: "toast-top-right",
      preventDuplicates: false,
      onclick: null,
      showDuration: "300",
      hideDuration: "1000",
      timeOut: "5000",
      extendedTimeOut: "1000",
      showEasing: "swing",
      hideEasing: "linear",
      showMethod: "fadeIn",
      hideMethod: "fadeOut"
    }
  };
  
  // DOM Elements
  const DOM = {
    addCustomWebsiteForm: () => document.getElementById('addCustomWebsiteForm'),
    customWebsiteName: () => document.getElementById('customWebsiteName'),
    customWebsiteUrl: () => document.getElementById('customWebsiteUrl'),
    deleteWebsiteButtons: () => document.querySelectorAll('.delete-website-btn'),
    manualScrapeButtons: () => document.querySelectorAll('.manual-scrape-btn'),
    intervalSelects: () => document.querySelectorAll('.interval-select'),
    searchInput: () => document.getElementById('search'),
    filterSelect: () => document.getElementById('filter'),
    jobTableBody: () => document.getElementById('jobTable').getElementsByTagName('tbody')[0]
  };
  
  // API Endpoints
  const API = {
    ADD_CUSTOM_WEBSITE: '/add_custom_website',
    DELETE_CUSTOM_WEBSITE: (id) => `/delete_custom_website/${id}`,
    UPDATE_WEBSITE: (id) => `/scrape/${id}`,
    UPDATE_INTERVAL: (id) => `/update_interval/${id}`,
    UPLOAD_SCRAPER: '/upload_scraper'
  };
  
  // Utility Functions
  const utils = {
    reloadPage: () => setTimeout(() => location.reload(), CONFIG.RELOAD_DELAY),
    showError: (message) => {
      console.error('Error:', message);
      toastr.error(message);
    }
  };
  
  // API Functions
  const api = {
    addCustomWebsite: async (name, url) => {
      try {
        const response = await fetch(API.ADD_CUSTOM_WEBSITE, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, url })
        });
        const data = await response.json();
        toastr.success(data.result);
        utils.reloadPage();
      } catch (error) {
        utils.showError('Une erreur est survenue lors de l\'ajout du site.');
      }
    },
  
    deleteCustomWebsite: async (id) => {
      try {
        const response = await fetch(API.DELETE_CUSTOM_WEBSITE(id), { method: 'DELETE' });
        const data = await response.json();
        toastr.success(data.result);
        utils.reloadPage();
      } catch (error) {
        utils.showError('Une erreur est survenue lors de la suppression du site.');
      }
    },
  
    manualScrape: async (id) => {
      try {
        const response = await fetch(API.UPDATE_WEBSITE(id));
        const data = await response.json();
        toastr.success(data.result);
        utils.reloadPage();
      } catch (error) {
        utils.showError('Une erreur est survenue lors du scan.');
      }
    },
  
    updateInterval: async (id, interval) => {
      try {
        const response = await fetch(API.UPDATE_INTERVAL(id), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ interval })
        });
        const data = await response.json();
        toastr.success(data.result);
        utils.reloadPage();
      } catch (error) {
        utils.showError('Une erreur est survenue lors de la mise à jour de l\'intervalle.');
      }
    },
    manualScrape: async (id) => {
      try {
        const response = await fetch(API.UPDATE_WEBSITE(id));
        const data = await response.json();
        toastr.success(data.result);
        
        // Update the "Dernière vérification" field in the table
        const row = document.querySelector(`tr[data-website-id="${id}"]`);
        if (row) {
          const lastCheckedCell = row.querySelector('td[data-label="Dernière Vérification"]');
          if (lastCheckedCell) {
            lastCheckedCell.textContent = data.last_checked;
          }
        }
      } catch (error) {
        utils.showError('Une erreur est survenue lors du scan.');
      }
    },
    fetchUpdatedData: async () => {
      try {
        const response = await fetch('/fetch_updated_data');
        const data = await response.json();
        return data;
      } catch (error) {
        utils.showError('Une erreur est survenue lors du chargement des données mises à jour.');
      }
    },
  };
  
  // Event Handlers
  const handlers = {
    addCustomWebsite: (event) => {
      event.preventDefault();
      const name = DOM.customWebsiteName().value;
      const url = DOM.customWebsiteUrl().value;
      api.addCustomWebsite(name, url);
    },
  
    deleteCustomWebsite: (event) => {
      const id = event.target.closest('tr').dataset.websiteId;
      api.deleteCustomWebsite(id);
    },
  
    manualScrape: (event) => {
      const id = event.target.closest('tr').dataset.websiteId;
      api.manualScrape(id);
    },
  
    updateInterval: (event) => {
      const id = event.target.closest('tr').dataset.websiteId;
      api.updateInterval(id, event.target.value);
    },
  
    filterTable: () => {
      const searchTerm = DOM.searchInput().value.toLowerCase();
      const filterValue = DOM.filterSelect().value.toLowerCase();
      const rows = DOM.jobTableBody().getElementsByTagName('tr');
  
      Array.from(rows).forEach(row => {
        const siteName = row.querySelector('td[data-label="Nom du Site"]').textContent.toLowerCase();
        const url = row.querySelector('td[data-label="URL"]').textContent.toLowerCase();
        const siteType = row.querySelector('td[data-label="ID du site"]').textContent.toLowerCase();
        const parsingMethod = row.querySelector('td[data-label="Méthode de Parsing"]').textContent.toLowerCase();
        
        const matchesSearch = [siteName, url, siteType, parsingMethod].some(text => text.includes(searchTerm));
        const matchesFilter = filterValue === '' || siteName === filterValue;
        row.style.display = (matchesSearch && matchesFilter) ? '' : 'none';
      });
    },
  
    updateDeleteButtons: () => {
      DOM.deleteWebsiteButtons().forEach(button => {
        const row = button.closest('tr');
        button.style.display = row.dataset.isPlugin === 'true' ? 'none' : 'inline-block';
      });
    },
    uploadScraper: async (event) => {
      event.preventDefault();
      const formData = new FormData(event.target);
      try {
        const response = await fetch(API.UPLOAD_SCRAPER, {
          method: 'POST',
          body: formData
        });
        const data = await response.json();
        if (response.ok) {
          toastr.success(data.message);
          utils.reloadPage();
        } else {
          toastr.error(data.message);
        }
      } catch (error) {
        utils.showError('An error occurred while uploading the scraper.');
      }
    },
    manualScrape: async (event) => {
      const id = event.target.closest('tr').dataset.websiteId;
      api.manualScrape(id).then(() => {
        api.fetchUpdatedData().then(data => {
          updateTable(data);
        });
      });
    },
  };
  
  // Initialize
  const init = () => {
    // Set up event listeners
    DOM.addCustomWebsiteForm().addEventListener('submit', handlers.addCustomWebsite);
    DOM.deleteWebsiteButtons().forEach(button => button.addEventListener('click', handlers.deleteCustomWebsite));
    DOM.manualScrapeButtons().forEach(button => button.addEventListener('click', handlers.manualScrape));
    DOM.intervalSelects().forEach(select => select.addEventListener('change', handlers.updateInterval));
    DOM.searchInput().addEventListener('input', handlers.filterTable);
    DOM.filterSelect().addEventListener('change', handlers.filterTable);
    document.getElementById('uploadScraperForm').addEventListener('submit', handlers.uploadScraper);
  
    // Initialize toastr
    toastr.options = CONFIG.TOASTR_OPTIONS;
  
    // Initial update of delete buttons
    handlers.updateDeleteButtons();
  };
  
  // Run initialization when DOM is loaded
  document.addEventListener('DOMContentLoaded', init);

// Function to set the theme
function setTheme(isDark) {
  const elementsToToggle = [
    document.documentElement,
    document.body,
    document.querySelector('header'),
    document.querySelector('table'),
    ...document.querySelectorAll('th, td, input, select, button, .type-column, .parsing-method-column')
  ];
  
  elementsToToggle.forEach(el => {
    if (el) {
      el.classList.toggle('dark-mode', isDark);
    }
  });
  
  localStorage.setItem('darkMode', isDark);
}

// Check for saved theme preference or use default (dark)
const savedTheme = localStorage.getItem('darkMode');
const defaultDark = savedTheme === null ? true : savedTheme === 'true';
setTheme(defaultDark);

// Ensure the toggle is in the correct state
const modeToggle = document.getElementById('modeToggle');
if (modeToggle) {
  modeToggle.checked = defaultDark;
  
  // Event listener for theme toggle
  modeToggle.addEventListener('change', function() {
    setTheme(this.checked);
  });
}

// Call setTheme on page load to ensure correct initial state
document.addEventListener('DOMContentLoaded', () => setTheme(defaultDark));

function updateTable(data) {
  const tableBody = DOM.jobTableBody();
  tableBody.innerHTML = '';
  
  const rows = data.map(website => {
    const intervalOptions = [
      { value: 'never', label: 'Jamais' },
      { value: '5min', label: '5 minutes' },
      { value: '30min', label: '30 minutes' },
      { value: '1hour', label: '1 heure' },
      { value: '2hours', label: '2 heures' },
      { value: '12hours', label: '12 heures' },
      { value: '1day', label: '1 jour' },
      { value: '1week', label: '1 semaine' }
    ];

    const intervalSelectOptions = intervalOptions
      .map(option => `<option value="${option.value}" ${website.scrape_interval === option.value ? 'selected' : ''}>${option.label}</option>`)
      .join('');

    return `
      <tr data-website-id="${website.id}">
        <td data-label="Nom du Site">${website.name}</td>
        <td data-label="URL">${website.url}</td>
        <td data-label="ID du site" class="type-column">
          ${website.is_ui_generated ? 'Plugin' : 'Ajouté par l\'utilisateur'}
        </td>
        <td data-label="Méthode de Parsing" class="parsing-method-column">
          ${website.is_ui_generated ? 'Parser spécifique' : 'Changement de hash'}
        </td>
        <td data-label="Nombre d'Offres">${website.last_link_count || 'Pas encore vérifié'}</td>
        <td data-label="Dernière Vérification">${website.last_checked || 'Pas encore vérifié'}</td>
        <td data-label="Intervalle de Scan">
          <select class="interval-select">
            ${intervalSelectOptions}
          </select>
        </td>
        <td data-label="Actions">
          <div class="action-buttons">
            <button class="manual-scrape-btn">Scanner Maintenant</button>
            <button class="delete-website-btn">Supprimer</button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
  
  tableBody.innerHTML = rows;
}
