<script setup>
import { useCollaborationStore } from '~/stores/collaborationStore';
import CodeEditor from '~/components/CodeEditor.vue';
const collaborationStore = useCollaborationStore()
console.log(collaborationStore.getCollaborationInfo)
</script>

<template>
    <div>
        <h2>Collab Page</h2>
        <pre>{{ collaborationStore.getCollaborationInfo }}</pre>
        <CodeEditor/>
    </div>
</template>