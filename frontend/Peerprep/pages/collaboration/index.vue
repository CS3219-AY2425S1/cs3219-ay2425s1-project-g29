<template>
    <div>
      <!-- Other collaboration content e.g. the coding editor -->
      <ChatComponent />
    </div>
  </template>
  
  <script setup>
  import { useCollaborationStore } from '~/store/collaborationStore';
  import ChatComponent from '~/components/ChatComponent.vue';
  
  const collaborationStore = useCollaborationStore();
  </script>
  