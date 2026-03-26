// static/push-notifications.js
// Enhanced client-side code with better user feedback

// Your VAPID public key from Firebase Console
const VAPID_PUBLIC_KEY = 'BAnweVK-efVFQelK5sixJ04X08SY2mx1ISS2dA_DABQdpXI0u2_vNzzzARxQMCtgA08VedgPSxU8oFvkKeaVbXs';

// Initialize Firebase
const firebaseConfig = {
  apiKey: "AIzaSyAwfyAKWXXdxX-YR4St08HW4BNRyMVoAq8",
  authDomain: "microclimate-health-risk.firebaseapp.com",
  databaseURL: "https://microclimate-health-risk-default-rtdb.firebaseio.com",
  projectId: "microclimate-health-risk",
  storageBucket: "microclimate-health-risk.firebasestorage.app",
  messagingSenderId: "674262753809",
  appId: "1:674262753809:web:898291d03b060b382707b0"
};

// Initialize Firebase only if not already initialized
if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}

const messaging = firebase.messaging();

// Request permission and get token - returns Promise<boolean>
window.requestNotificationPermission = async function() {
    try {
        console.log('Requesting notification permission...');
        
        // First, check if service workers are supported
        if (!('serviceWorker' in navigator)) {
            console.log('Service workers not supported');
            showStatusMessage('Your browser does not support notifications', 'error');
            return false;
        }

        // Check if already granted
        if (Notification.permission === 'granted') {
            console.log('Permission already granted');
            // Still need to check if token exists
            await getAndSaveToken();
            return true;
        }

        // Request permission 
        const permission = await Notification.requestPermission();
        console.log('Permission result:', permission);
        
        if (permission !== 'granted') {
            console.log('Notification permission denied');
            showStatusMessage('Notification permission denied', 'error');
            return false;
        }

        // Permission granted, get token
        return await getAndSaveToken();
        
    } catch (error) {
        console.error('Error setting up notifications:', error);
        showStatusMessage('Error setting up notifications', 'error');
        return false;
    }
};

// Get and save token helper
async function getAndSaveToken() {
    try {
        // Register service worker if not already registered
        const registration = await navigator.serviceWorker.register('/static/firebase-messaging-sw.js');
        console.log('Service Worker registered:', registration);

        // Get FCM token 
        const token = await messaging.getToken({
            vapidKey: VAPID_PUBLIC_KEY,
            serviceWorkerRegistration: registration
        });

        console.log('FCM Token obtained:', token.substring(0, 20) + '...');

        // Get push subscription details
        const subscription = await registration.pushManager.getSubscription();
        
        if (!subscription) {
            console.log('No push subscription found');
            return false;
        }

        // Send to server
        const response = await fetch('/notifications/register-push', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                token: token,
                endpoint: subscription.endpoint,
                keys: {
                    auth: arrayBufferToBase64(subscription.getKey('auth')),
                    p256dh: arrayBufferToBase64(subscription.getKey('p256dh'))
                },
                userAgent: navigator.userAgent
            })
        });

        if (response.ok) {
            console.log('✅ Push subscription saved to server');
            showStatusMessage('Notifications enabled successfully!', 'success');
            return true;
        } else {
            console.error('Failed to save subscription');
            return false;
        }
    } catch (error) {
        console.error('Error getting token:', error);
        return false;
    }
}

// Helper: Convert ArrayBuffer to Base64 string 
function arrayBufferToBase64(buffer) {
    if (!buffer) return null;
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
}

// Show status message helper
function showStatusMessage(message, type = 'info') {
    // You can customize this to show a toast or alert
    console.log(`[${type}] ${message}`);
    
    // Check if there's an existing status toast
    let statusToast = document.getElementById('status-toast');
    if (!statusToast) {
        statusToast = document.createElement('div');
        statusToast.id = 'status-toast';
        statusToast.className = 'position-fixed top-0 start-50 translate-middle-x mt-3';
        statusToast.style.zIndex = '10000';
        document.body.appendChild(statusToast);
    }
    
    const bgColor = type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8';
    
    statusToast.innerHTML = `
        <div class="toast show" style="background: white; border-left: 4px solid ${bgColor}; min-width: 300px;">
            <div class="toast-body d-flex align-items-center">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'} me-2" style="color: ${bgColor};"></i>
                <span class="flex-grow-1">${message}</span>
                <button type="button" class="btn-close ms-2" onclick="this.closest('.toast').remove()"></button>
            </div>
        </div>
    `;
    
    setTimeout(() => {
        if (statusToast.firstChild) {
            statusToast.firstChild.remove();
        }
    }, 5000);
}

// Handle foreground messages 
messaging.onMessage((payload) => {
    console.log('Foreground message received:', payload);
    
    // Show in-app notification
    const { title, body, risk_level } = payload.data;
    
    // Create a temporary notification toast
    const toast = document.createElement('div');
    toast.className = 'toast show position-fixed bottom-0 end-0 m-3';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '300px';
    
    const bgColor = risk_level === 'High' ? '#dc3545' : risk_level === 'Moderate' ? '#ffc107' : '#28a745';
    const icon = risk_level === 'High' ? 'fa-exclamation-triangle' : 'fa-bell';
    
    toast.innerHTML = `
        <div class="toast-header" style="background: ${bgColor}; color: white;">
            <i class="fas ${icon} me-2"></i>
            <strong class="me-auto">${title || 'Health Alert'}</strong>
            <button type="button" class="btn-close btn-close-white" onclick="this.closest('.toast').remove()"></button>
        </div>
        <div class="toast-body">
            ${body}
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => toast.remove(), 10000);
});

// Check current subscription status
window.checkSubscriptionStatus = async function() {
    try {
        const response = await fetch('/notifications/check-subscription');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error checking subscription:', error);
        return { subscribed: false };
    }
};

// Auto-check on load
document.addEventListener('DOMContentLoaded', async () => {
    // Check if we have permission and are subscribed
    if (Notification.permission === 'granted') {
        const status = await checkSubscriptionStatus();
        if (!status.subscribed) {
            console.log('Has permission but not subscribed - re-subscribing');
            await getAndSaveToken();
        }
    }
});

// Export functions for use in HTML
window.checkSubscriptionStatus = checkSubscriptionStatus;