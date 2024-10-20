<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useCollaborationStore } from '~/store/collaborationStore'; // Store for real-time sync
import { initializeApp } from 'firebase/app';
import { getFirestore, doc, onSnapshot, updateDoc } from 'firebase/firestore';
import CodeMirror from 'codemirror';
import 'codemirror/lib/codemirror.css';

// Firebase config
const firebaseConfig = {
  apiKey: "AIzaSyDuExsKWkNaXvpZhATNLNeWInqRyAeuSq8",
  authDomain: "peerprep-g29.firebaseapp.com",
  projectId: "peerprep-g29",
  storageBucket: "peerprep-g29.appspot.com",
  messagingSenderId: "1075086955666",
  appId: "1:1075086955666:web:8929f9277a3a982847c24b"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const collaborationStore = useCollaborationStore();
const editor = ref(null);
const session_id = collaborationStore.getCollaborationInfo.uid;

onMounted(() => {
  // Initialize CodeMirror
  editor.value = CodeMirror(this.$refs.editorContainer, {
    mode: 'javascript',
    lineNumbers: true,
    theme: 'default',
  });

  // Sync editor content with Firebase Firestore
  const docRef = doc(db, 'collaborations', session_id);

  // Check if the document exists in Firestore
  getDoc(docRef)
    .then((docSnap) => {
      if (docSnap.exists()) {
        // Document exists, load the content into CodeMirror
        const data = docSnap.data();
        if (data && data.code) {
          editor.value.setValue(data.code);
        }
      } else {
        // Document doesn't exist, create a new one with default content
        setDoc(docRef, { code: '' })
          .then(() => {
            console.log('New document created successfully!');
          })
          .catch((error) => {
            console.error('Error creating document:', error);
          });
      }
    })
    .catch((error) => {
      console.error('Error getting document:', error);
    });

  // Listen for real-time updates from Firestore
  onSnapshot(docRef, (snapshot) => {
    const data = snapshot.data();
    if (data && data.code) {
      // Update CodeMirror content when changes are received from Firestore
      if (editor.value.getValue() !== data.code) {
        editor.value.setValue(data.code);
      }
    }
  });

  // Detect changes in CodeMirror and update Firestore
  editor.value.on('change', () => {
    updateDoc(docRef, { code: editor.value.getValue() });
  });
});

onBeforeUnmount(() => {
  // Clean up listeners
});
</script>

<template>
  <div ref="editor" class="editor-container w-full h-full"></div>
</template>

<style scoped>
.editor-container {
  width: 100%;
  height: 100%;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f8f8f8;
}
</style>