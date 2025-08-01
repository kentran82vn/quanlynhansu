/*
===============================================
📱 PWA INITIALIZATION
===============================================
Service Worker registration and PWA features
===============================================
*/

// Service Worker Registration
if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {
      const registration = await navigator.serviceWorker.register('/static/sw.js');
      console.log('✅ Service Worker registered successfully:', registration.scope);
      
      // Listen for updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        console.log('🔄 New Service Worker installing...');
        
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            // New version available
            showUpdateNotification();
          }
        });
      });
      
    } catch (error) {
      console.error('❌ Service Worker registration failed:', error);
    }
  });
  
  // Listen for Service Worker messages
  navigator.serviceWorker.addEventListener('message', (event) => {
    console.log('💬 Message from Service Worker:', event.data);
  });
}

// PWA Install Prompt
let deferredPrompt;
let installButton;

window.addEventListener('beforeinstallprompt', (e) => {
  console.log('📱 PWA install prompt available');
  
  // Prevent the mini-infobar from appearing on mobile
  e.preventDefault();
  
  // Save the event so it can be triggered later
  deferredPrompt = e;
  
  // Show custom install button
  showInstallButton();
});

window.addEventListener('appinstalled', (event) => {
  console.log('🎉 PWA installed successfully');
  hideInstallButton();
  
  // Track installation
  if (typeof gtag !== 'undefined') {
    gtag('event', 'pwa_install', {
      event_category: 'PWA',
      event_label: 'App Installed'
    });
  }
});

// Show custom install button
function showInstallButton() {
  // Create install button if it doesn't exist
  if (!installButton) {
    installButton = document.createElement('button');
    installButton.className = 'btn btn-primary pwa-install-btn';
    installButton.innerHTML = '📱 Cài đặt ứng dụng';
    installButton.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      z-index: 1000;
      border-radius: 25px;
      padding: 12px 20px;
      font-size: 14px;
      font-weight: 600;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
      animation: slideInUp 0.3s ease-out;
    `;
    
    installButton.addEventListener('click', installPWA);
    document.body.appendChild(installButton);
  }
  
  installButton.style.display = 'block';
}

// Hide install button
function hideInstallButton() {
  if (installButton) {
    installButton.style.display = 'none';
  }
}

// Install PWA
async function installPWA() {
  if (!deferredPrompt) {
    console.log('❌ No install prompt available');
    return;
  }
  
  // Show the install prompt
  deferredPrompt.prompt();
  
  // Wait for the user's response
  const choiceResult = await deferredPrompt.userChoice;
  
  if (choiceResult.outcome === 'accepted') {
    console.log('✅ User accepted PWA install');
  } else {
    console.log('❌ User dismissed PWA install');
  }
  
  // Clear the prompt
  deferredPrompt = null;
  hideInstallButton();
}

// Update notification
function showUpdateNotification() {
  // Create update notification
  const updateBanner = document.createElement('div');
  updateBanner.className = 'update-notification';
  updateBanner.innerHTML = `
    <div class="update-content">
      <i class="fas fa-sync-alt"></i>
      <span>Có phiên bản mới! Tải lại để cập nhật?</span>
      <button class="btn btn-sm btn-light" onclick="reloadApp()">Tải lại</button>
      <button class="btn btn-sm btn-outline-light" onclick="dismissUpdate()">Bỏ qua</button>
    </div>
  `;
  
  updateBanner.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: var(--primary-color);
    color: white;
    z-index: 10000;
    animation: slideInDown 0.3s ease-out;
  `;
  
  document.body.prepend(updateBanner);
}

// Reload app with new version
function reloadApp() {
  if (navigator.serviceWorker.controller) {
    navigator.serviceWorker.controller.postMessage({ type: 'SKIP_WAITING' });
  }
  window.location.reload();
}

// Dismiss update notification
function dismissUpdate() {
  const notification = document.querySelector('.update-notification');
  if (notification) {
    notification.remove();
  }
}

// Network Status Detection
function handleOnlineStatus() {
  const status = navigator.onLine ? 'online' : 'offline';
  console.log(`🌐 Network status: ${status}`);
  
  // Show/hide offline indicator
  updateOfflineIndicator(status);
  
  // Trigger background sync if back online
  if (status === 'online' && 'serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
    navigator.serviceWorker.ready.then(registration => {
      return registration.sync.register('epa-form-sync');
    }).catch(error => {
      console.error('❌ Background sync registration failed:', error);
    });
  }
}

// Update offline indicator
function updateOfflineIndicator(status) {
  let indicator = document.getElementById('offline-indicator');
  
  if (status === 'offline') {
    if (!indicator) {
      indicator = document.createElement('div');
      indicator.id = 'offline-indicator';
      indicator.innerHTML = `
        <i class="fas fa-wifi"></i>
        <span>Không có kết nối mạng</span>
      `;
      indicator.style.cssText = `
        position: fixed;
        top: 60px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--warning-color);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        z-index: 9999;
        animation: slideInDown 0.3s ease-out;
      `;
      document.body.appendChild(indicator);
    }
  } else {
    if (indicator) {
      indicator.remove();
    }
  }
}

// Listen for network status changes
window.addEventListener('online', handleOnlineStatus);
window.addEventListener('offline', handleOnlineStatus);

// Initialize network status
handleOnlineStatus();

// Performance Monitoring
if ('performance' in window) {
  window.addEventListener('load', () => {
    // Get performance metrics
    const perfData = performance.getEntriesByType('navigation')[0];
    
    if (perfData) {
      const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
      const domContentLoaded = perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart;
      
      console.log(`⚡ Page load time: ${loadTime}ms`);
      console.log(`⚡ DOM ready time: ${domContentLoaded}ms`);
      
      // Track performance metrics
      if (typeof gtag !== 'undefined') {
        gtag('event', 'page_load_time', {
          event_category: 'Performance',
          value: Math.round(loadTime)
        });
      }
    }
  });
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideInUp {
    from {
      transform: translateY(100%);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }
  
  @keyframes slideInDown {
    from {
      transform: translateY(-100%);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }
  
  .update-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 12px;
    text-align: center;
  }
  
  .update-content i {
    animation: spin 2s linear infinite;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  @media (max-width: 768px) {
    .pwa-install-btn {
      bottom: 80px !important;
      font-size: 12px !important;
      padding: 8px 16px !important;
    }
    
    .update-content {
      flex-direction: column;
      gap: 8px;
    }
    
    .update-content span {
      font-size: 14px;
    }
  }
`;
document.head.appendChild(style);

console.log('📱 PWA initialization script loaded');