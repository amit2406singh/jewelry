import { renderDashboard } from './components/dashboard.js';
import { renderSearch } from './components/search.js';
import { renderRegister } from './components/register.js';
import { renderManage } from './components/manage.js';
import { renderLogin } from './components/login.js';
import { renderPortfolio } from './components/portfolio.js';

// Global live gold rates config (₹ per gram for 24K pure gold)
const LIVE_GOLD_RATES = {
  '24K': 7560
};

// Application State
let currentUser = null;

// DOM Elements
const contentMount = document.getElementById('content-mount');
const viewTitle = document.getElementById('view-title');
const viewSubtitle = document.getElementById('view-subtitle');
const navItems = document.querySelectorAll('.nav-item');

const navDashboard = document.getElementById('nav-dashboard');
const navSearch = document.getElementById('nav-search');
const navRegister = document.getElementById('nav-register');
const navManage = document.getElementById('nav-manage');
const navPortfolio = document.getElementById('nav-portfolio');
const navLogout = document.getElementById('nav-logout');

const sidebarFooter = document.querySelector('.sidebar-footer');

// Page Header Titles & Subtitles mapping
const viewMetaData = {
  login: {
    title: 'Secure Access Portal',
    subtitle: 'Authenticate credentials to register gold assets or manage portfolio indices.'
  },
  dashboard: {
    title: 'Dashboard Overview',
    subtitle: 'Real-time status of registered jewelry and active HUIDs.'
  },
  search: {
    title: 'HUID Verification Portal',
    subtitle: 'Search and authenticate jewelry ownership status using the laser-etched HUID.'
  },
  register: {
    title: 'HUID Registration Portal',
    subtitle: 'Register newly purchased hallmarked jewelry into the secure ownership network.'
  },
  manage: {
    title: 'Registry Status Manager',
    subtitle: 'Update ownership status, file theft logs, or recover flagged jewelry records.'
  },
  portfolio: {
    title: 'Gold Owner Portfolio',
    subtitle: 'Track your registered asset specs, current market values, and investment returns.'
  }
};

/**
 * Updates the navigation sidebar tabs according to the active role session
 */
function updateSidebarUI() {
  if (!currentUser) {
    // Hidden mode during Login
    navDashboard.style.display = 'none';
    navSearch.style.display = 'none';
    navRegister.style.display = 'none';
    navManage.style.display = 'none';
    navPortfolio.style.display = 'none';
    navLogout.style.display = 'none';
    sidebarFooter.style.display = 'none';
    return;
  }

  sidebarFooter.style.display = 'block';
  navLogout.style.display = 'flex';

  if (currentUser.role === 'shop') {
    // Shop Dashboard View
    navDashboard.style.display = 'flex';
    navSearch.style.display = 'flex';
    navRegister.style.display = 'flex';
    navManage.style.display = 'flex';
    navPortfolio.style.display = 'none';

    // Footer
    sidebarFooter.innerHTML = `
      <div class="user-profile">
        <div class="avatar">JS</div>
        <div class="user-details">
          <p class="user-name">Jeweller Station</p>
          <p class="user-role">Authorized Node</p>
        </div>
      </div>
    `;
  } else if (currentUser.role === 'owner') {
    // Owner Portfolio View
    navDashboard.style.display = 'none';
    navSearch.style.display = 'none';
    navRegister.style.display = 'none';
    navManage.style.display = 'none';
    navPortfolio.style.display = 'flex';

    // Footer
    const initials = currentUser.name.split(' ').map(x => x[0]).join('').slice(0, 2).toUpperCase();
    sidebarFooter.innerHTML = `
      <div class="user-profile">
        <div class="avatar">${initials}</div>
        <div class="user-details">
          <p class="user-name">${currentUser.name}</p>
          <p class="user-role" style="font-family: monospace;">HUID: ${currentUser.record.huid}</p>
        </div>
      </div>
    `;
  }
}

/**
 * Modern Toast Notification System
 * @param {string} message 
 * @param {'success' | 'error' | 'info'} type 
 */
export function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  let iconSvg = '';
  if (type === 'success') {
    iconSvg = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20 6L9 17l-5-5"/>
      </svg>
    `;
  } else if (type === 'error') {
    iconSvg = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
    `;
  } else {
    iconSvg = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="16" x2="12" y2="12"/>
        <line x1="12" y1="8" x2="12.01" y2="8"/>
      </svg>
    `;
  }

  toast.innerHTML = `
    ${iconSvg}
    <span>${message}</span>
  `;

  container.appendChild(toast);

  // Auto remove after 4 seconds
  setTimeout(() => {
    toast.style.animation = 'slideInRight 0.3s cubic-bezier(0.16, 1, 0.3, 1) reverse forwards';
    toast.addEventListener('animationend', () => {
      toast.remove();
      if (container.children.length === 0) {
        container.remove();
      }
    });
  }, 4000);
}

/**
 * Handle view navigation transitions
 * @param {string} view 
 * @param {any} params 
 */
function navigateTo(view, params = '') {
  // If not logged in, force redirect to login
  if (!currentUser && view !== 'login') {
    view = 'login';
  }

  if (!viewMetaData[view]) return;

  // Update header text
  viewTitle.textContent = viewMetaData[view].title;
  viewSubtitle.textContent = viewMetaData[view].subtitle;

  // Sync Sidebar Active Item
  navItems.forEach(item => {
    if (item.getAttribute('data-view') === view) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Render Page Content
  switch (view) {
    case 'login':
      renderLogin(contentMount, onLoginSuccess, showToast);
      break;
    case 'dashboard':
      renderDashboard(contentMount, navigateTo);
      break;
    case 'search':
      renderSearch(contentMount, navigateTo, params);
      break;
    case 'register':
      renderRegister(contentMount, navigateTo, showToast);
      if (params) {
        const huidInput = document.getElementById('reg-huid');
        if (huidInput) {
          huidInput.value = params.toUpperCase().trim();
          huidInput.dispatchEvent(new Event('input'));
        }
      }
      break;
    case 'manage':
      renderManage(contentMount, navigateTo, showToast, params);
      break;
    case 'portfolio':
      renderPortfolio(contentMount, currentUser, navigateTo, showToast, LIVE_GOLD_RATES);
      break;
  }
}

/**
 * Handle successful login events
 * @param {object} sessionUser 
 */
function onLoginSuccess(sessionUser) {
  currentUser = sessionUser;
  updateSidebarUI();
  
  if (currentUser.role === 'shop') {
    navigateTo('dashboard');
  } else {
    navigateTo('portfolio');
  }
}

// Attach event listeners to navigation buttons
navItems.forEach(item => {
  item.addEventListener('click', () => {
    const view = item.getAttribute('data-view');
    navigateTo(view);
  });
});

// Logout handler
navLogout.addEventListener('click', () => {
  currentUser = null;
  updateSidebarUI();
  showToast('Logged out successfully.', 'info');
  navigateTo('login');
});

// Initial App Startup
updateSidebarUI();
navigateTo('login');
