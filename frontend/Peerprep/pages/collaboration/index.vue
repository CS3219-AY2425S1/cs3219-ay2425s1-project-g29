<script setup>
import { useCollaborationStore } from '~/store/collaborationStore';
const collaborationStore = useCollaborationStore()
console.log(collaborationStore.getCollaborationInfo)
</script>


<template>
    <div>Collab page_</div>
    <pre>{{ collaborationStore.getCollaborationInfo }}</pre>
</template>