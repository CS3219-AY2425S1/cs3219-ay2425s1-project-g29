<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useCollaborationStore } from '~/stores/collaborationStore'; // Store for real-time sync
import { useFirebaseApp, useFirestore } from 'vuefire';
import { doc, onSnapshot, getDoc, setDoc, updateDoc } from 'firebase/firestore';
import CodeMirror from 'codemirror';
import 'codemirror/lib/codemirror.css';
import 'codemirror/theme/dracula.css';
import 'codemirror/mode/javascript/javascript.js';

const firebaseApp = useFirebaseApp();
const db = useFirestore(firebaseApp);
const collaborationStore = useCollaborationStore();
const session_info = collaborationStore.getCollaborationInfo;

const editor = ref(null);  // Store CodeMirror instance
const editorContainer = ref(null); // Ref for editor textarea container

onMounted(() => {
    // Initialise CodeMirror
    editor.value = CodeMirror.fromTextArea(editorContainer.value, {
        mode: 'javascript',
        lineNumbers: true,
        theme: 'dracula',
    });

    // Sync editor content with Firebase Firestore
    const docRef = doc(db, 'collaborations', session_info.uid);

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

    // Listen for changes in CodeMirror and update Firestore
    editor.value.on('change', () => {
        const currentCode = editor.value.getValue(); // Get the current code from CodeMirror
        console.log('CodeMirror content changed:', currentCode);
    
        // Update Firestore document with the new code
        updateDoc(docRef, { code: currentCode })
            .then(() => {
                console.log("Firestore document updated successfully.");
            })
            .catch((error) => {
                console.error('Error updating Firestore:', error);
            });  
    });
    
});

onBeforeUnmount(() => {
  // Clean up listeners
});
</script>

<template>
  <textarea ref="editorContainer" class="editor-container w-full h-full"></textarea>
</template>

<style scoped>
.editor-container {
  width: 90%;
  height: 100%;
  border: 1px solid #000000;
  border-radius: 4px;
  background-color: #cdcdcd;
}
</style>