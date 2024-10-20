<script setup>
import { useCollaborationStore } from '~/store/collaborationStore';
import CodeEditor from './components/CodeEditor.vue';

const collaborationStore = useCollaborationStore()
console.log(collaborationStore.getCollaborationInfo)
</script>

<template>
    <div>Collab page</div>
    <pre>{{ collaborationStore.getCollaborationInfo }}</pre>
    <CodeEditor/>
</template>