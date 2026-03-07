// firebase-config.js
// ⚠️ সতর্কতা: উপরে আপলোড করা private_key এখানে ব্যবহার করবেন না!
// Firebase Console > Project Settings > General > Your Apps > Web App > SDK Setup and Configuration
// সেখান থেকে 'firebaseConfig' অংশটি কপি করে নিচে বসান।

const firebaseConfig = {
  apiKey: "AIzaSyAumnyP9OelLqNPh_CP4Eb1jqP7u7E66H0", // আপনার Web App API Key
  authDomain: "bynex-ai.firebaseapp.com", // আপনার প্রজেক্ট ID
  projectId: "bynex-ai",
  storageBucket: "bynex-ai.appspot.com",
  messagingSenderId: "1234567890",
  appId: "1:1234567890:web:abcdef123456"
};

// Firebase Initialize
if (typeof firebase !== 'undefined' && !firebase.apps.length) {
  firebase.initializeApp(firebaseConfig);
}

// Firestore ডেটাবেস রেফারেন্স
const db = firebase.firestore();
