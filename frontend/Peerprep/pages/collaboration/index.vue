<script setup>
import { useCollaborationStore } from '~/stores/collaborationStore';
const collaborationStore = useCollaborationStore()
console.log(collaborationStore.getCollaborationInfo)
</script>

<template>
    <div>Collab page</div>
    <pre>{{ collaborationStore.getCollaborationInfo }}</pre>
</template>