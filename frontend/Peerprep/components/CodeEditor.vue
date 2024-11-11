<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { createClient } from "@liveblocks/client";
import { LiveblocksYjsProvider } from "@liveblocks/yjs";
import * as Y from "yjs";
import { yCollab } from "y-codemirror.next";
import { EditorView, basicSetup } from "codemirror";
import { Compartment, EditorState } from "@codemirror/state";
import { javascript } from "@codemirror/lang-javascript";
import { cpp } from "@codemirror/lang-cpp";
import { python } from "@codemirror/lang-python";
import { useCollaborationStore } from '~/stores/collaborationStore'; // Store for real-time sync
import { useFirebaseApp, useFirestore } from 'vuefire';
import { doc, getDoc, setDoc, onSnapshot, updateDoc } from 'firebase/firestore';
import { oneDark } from "@codemirror/theme-one-dark";

const parent = ref(null);
const leave = ref(null);
const view = ref(null);
const language = ref("javascript");
const firebaseApp = useFirebaseApp();
const db = useFirestore(firebaseApp);
const collaborationStore = useCollaborationStore();
const session_info = collaborationStore.getCollaborationInfo;

const props = defineProps({
  isTerminated: {
    type: Boolean,
    default: false
  }
});

// Set up Liveblocks client
const client = createClient({
  publicApiKey: useRuntimeConfig().public.apiKey,
});

// Enter a multiplayer room
const info = client.enterRoom(session_info.uid);
const room = info.room;
leave.value = info.leave;

// Set up Yjs document, shared text, and Liveblocks Yjs provider
const yDoc = new Y.Doc();
const yText = yDoc.getText("codemirror");
const yProvider = new LiveblocksYjsProvider(room, yDoc);

// Set up a shared map for the language selection
const yMap = yDoc.getMap("settings");
yMap.set("language", language.value); // Initialize shared language

const editableCompartment = new Compartment();

// Function to get the current language extension
const getLanguageExtension = () => {
  switch (language.value) {
    case "python":
      return python();
    case "cpp":
      return cpp();
    default:
      return javascript();
  }
};

onMounted(async () => {
  // Create the Firestore document reference
  const docRef = doc(db, 'collaborations', session_info.uid);

  // Check if the document exists, otherwise create it with initial content
  const docSnap = await getDoc(docRef);
  if (!docSnap.exists()) {
    await setDoc(docRef, { code: '', isTerminated: props.isTerminated });
  }

  // Set up CodeMirror and extensions
  const state = EditorState.create({
    doc: yText.toString(),
    extensions: [
      basicSetup,
      getLanguageExtension(),
      yCollab(yText, yProvider.awareness),
      oneDark,
      editableCompartment.of(EditorView.editable.of(true)),
    ],
  });

  // Attach CodeMirror to element
  view.current = new EditorView({
    state,
    parent: parent.value,
  });

  // Listen to changes in the `status` field in Firestore
  onSnapshot(docRef, (snapshot) => {
    const data = snapshot.data();
    console.log(data);
    if (data && data.isTerminated) {
      view.current.dispatch({
        effects: editableCompartment.reconfigure(EditorView.editable.of(false)),
      })
      console.log("Collaboration terminated - editor set to read-only");
    }
  });

  // Watch for local collaboration termination in the store
  watch(
    () => props.isTerminated,
    async (terminated) => {
      if (terminated) {
        try {
          // Update Firestore status to "terminated"
          console.log("local termination")
          await updateDoc(docRef, { isTerminated: true });
        } catch (error) {
          console.error('Error updating collaboration status:', error);
        }
      }
    }
  );

  // Watch for language changes and update the editor
  watch(language, (newLang) => {
    yMap.set("language", newLang); // Update shared language state
    const newState = EditorState.create({
      doc: yText.toString(),
      extensions: [
        basicSetup,
        getLanguageExtension(),
        yCollab(yText, yProvider.awareness),
        oneDark,
      ],
    });
    view.current.setState(newState);
  });

  // Observe changes in the shared Yjs map for language updates from other users
  yMap.observe(() => {
    const newLanguage = yMap.get("language");
    if (language.value !== newLanguage) {
      language.value = newLanguage; // Sync local language with shared state
    }
  });

  // Save to Firestore when the document changes
  yText.observe(() => {
    const currentCode = yText.toString();
    setDoc(docRef, { code: currentCode }, { merge: true })
      .then(() => console.log("Code saved to Firestore successfully"))
      .catch(error => console.error("Error saving to Firestore:", error));
  });

});

</script>

<template>
  <select v-model="language">
    <option value="javascript">JavaScript</option>
    <option value="python">Python</option>
    <option value="cpp">C++</option>
  </select>
  <div ref="parent"></div>
</template>