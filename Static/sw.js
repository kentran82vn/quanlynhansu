/*
===============================================
🔧 SERVICE WORKER - EPA System PWA
===============================================
Offline support and caching for mobile experience
===============================================
*/

const CACHE_NAME = 'epa-system-v1.0.0';
const OFFLINE_URL = '/offline';

// Files to cache for offline functionality
const urlsToCache = [
  '/',
  '/dashboard',
  '/user-epa-score',
  '/static/css/modern.css',
  '/static/css/mobile-enhancements.css',
  '/static/js/app.js',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
];

// Install Service Worker
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('📦 Caching app shell files');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('✅ Service Worker installed successfully');
        return self.skipWaiting(); // Force activation
      })
      .catch((error) => {
        console.error('❌ Failed to cache files:', error);
      })
  );
});

// Activate Service Worker
self.addEventListener('activate', (event) => {
  console.log('🚀 Service Worker activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            // Delete old caches
            if (cacheName !== CACHE_NAME) {
              console.log('🗑️ Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('✅ Service Worker activated');
        return self.clients.claim(); // Take control immediately
      })
  );
});

// Fetch Strategy: Network First with Cache Fallback
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip external requests (except fonts and icons)
  if (url.origin !== location.origin && 
      !url.hostname.includes('googleapis.com') && 
      !url.hostname.includes('cdnjs.cloudflare.com')) {
    return;
  }
  
  event.respondWith(
    networkFirstWithFallback(request)
  );
});

/**
 * Network First strategy with cache fallback
 * Good for dynamic content that changes frequently
 */
async function networkFirstWithFallback(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    // If successful, update cache and return response
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    
    // If network fails, try cache
    throw new Error('Network response not ok');
    
  } catch (error) {
    console.log('🌐 Network failed, trying cache for:', request.url);
    
    // Try to get from cache
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // If both network and cache fail, return offline page for navigation requests
    if (request.mode === 'navigate') {
      return caches.match(OFFLINE_URL) || 
             new Response('Offline - Không có kết nối mạng', {
               status: 200,
               headers: { 'Content-Type': 'text/html; charset=utf-8' }
             });
    }
    
    // For other requests, return a generic offline response
    return new Response('Offline', {
      status: 503,
      statusText: 'Service Unavailable',
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

// Background Sync for form submissions
self.addEventListener('sync', (event) => {
  console.log('🔄 Background sync triggered:', event.tag);
  
  if (event.tag === 'epa-form-sync') {
    event.waitUntil(syncEPAForms());
  }
});

/**
 * Sync EPA forms when connection is restored
 */
async function syncEPAForms() {
  try {
    // Get pending EPA submissions from IndexedDB
    const pendingForms = await getPendingEPAForms();
    
    for (const form of pendingForms) {
      try {
        const response = await fetch('/api/submit-epa', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(form.data)
        });
        
        if (response.ok) {
          // Remove from pending list
          await removePendingEPAForm(form.id);
          console.log('✅ EPA form synced successfully:', form.id);
        }
      } catch (error) {
        console.error('❌ Failed to sync EPA form:', form.id, error);
      }
    }
  } catch (error) {
    console.error('❌ Background sync failed:', error);
  }
}

// Push Notifications (for future EPA deadline reminders)
self.addEventListener('push', (event) => {
  console.log('📱 Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'Nhắc nhở đánh giá EPA',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/badge-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      url: '/user-epa-score'
    },
    actions: [
      {
        action: 'open-epa',
        title: 'Làm đánh giá',
        icon: '/static/icons/action-epa.png'
      },
      {
        action: 'dismiss',
        title: 'Bỏ qua',
        icon: '/static/icons/action-dismiss.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('EPA System', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('📱 Notification clicked:', event.action);
  
  event.notification.close();
  
  const urlToOpen = event.action === 'open-epa' 
    ? '/user-epa-score' 
    : '/dashboard';
  
  event.waitUntil(
    clients.matchAll({ type: 'window' })
      .then((clientList) => {
        // If already open, focus the window
        for (const client of clientList) {
          if (client.url.includes(urlToOpen) && 'focus' in client) {
            return client.focus();
          }
        }
        
        // Otherwise, open new window
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
  );
});

// Message handling for communication with main thread
self.addEventListener('message', (event) => {
  console.log('💬 Message received in SW:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
});

// Helper functions for IndexedDB operations
async function getPendingEPAForms() {
  // TODO: Implement IndexedDB operations for offline form storage
  return [];
}

async function removePendingEPAForm(id) {
  // TODO: Implement IndexedDB remove operation
  return true;
}

console.log('🎯 Service Worker script loaded successfully');