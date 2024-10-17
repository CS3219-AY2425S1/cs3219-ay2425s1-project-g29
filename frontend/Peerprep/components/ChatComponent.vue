<template>
    <div class="chat-container">
      <div class="messages">
        <div v-for="message in messages" :key="message.id" class="message">
          <strong>{{ message.sender_id }}:</strong> {{ message.text }}
        </div>
      </div>
      <input v-model="newMessage" @keyup.enter="sendMessage" placeholder="Type a message" />
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue';
  import { useCollection } from 'vuefire';
  import { collection, doc, addDoc, serverTimestamp } from 'firebase/firestore';
  import { useCollaborationStore } from '~/store/collaborationStore';
  import { useFirebaseAuth, useFirestore } from 'vuefire';
  
  const collaborationStore = useCollaborationStore();
  const firestore = useFirestore();
  const auth = useFirebaseAuth();
  
  const sessionId = collaborationStore.collaborationInfo?.uid;
  
  const messagesRef = collection(
    doc(firestore, 'chats', sessionId),
    'messages'
  );
  
  const messages = useCollection(messagesRef, { wait: true });
  
  const newMessage = ref('');
  
  const sendMessage = async () => {
    if (!newMessage.value.trim()) return;
  
    await addDoc(messagesRef, {
      text: newMessage.value,
      sender_id: auth.currentUser.uid,
      timestamp: serverTimestamp(),
    });
  
    newMessage.value = '';
  };
  </script>
  
  <style scoped>
  
  </style>
  