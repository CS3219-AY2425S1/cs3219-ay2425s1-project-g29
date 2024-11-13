<script setup>
import { useCollaborationStore } from '~/stores/collaborationStore';
import CodeEditor from '~/components/CodeEditor.vue';
import AdviceBox from '~/components/collab/AdviceBox.vue';
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Chat from '~/components/chat/chat.vue';

const collaborationStore = useCollaborationStore();
const session_info = collaborationStore.getCollaborationInfo;
const router = useRouter();

const chatRef = ref(null); // Reference to the Chat component

const question = ref(null); // Store the fetched question
const isLoading = ref(false);
const error = ref(null);

const isTerminated = ref(false);

const fetchQuestion = async (id) => {
  try {
    isLoading.value = true;
    error.value = null;
    const { data, error: fetchError } = await useFetch(`/api/questions/${id}`);

    if (fetchError.value) {
      throw new Error(fetchError.value.message);
    }

    if (data.value) {
      question.value = {
        id: data.value.id,
        title: data.value.title,
        description: data.value.description,
        category: Array.isArray(data.value.category) ? data.value.category.join(', ') : data.value.category,
        difficulty: data.value.difficulty,
      };
    }
  } catch (err) {
    console.error('Error fetching question:', err);
    error.value = err instanceof Error ? err.message : 'An unknown error occurred';
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchQuestion(collaborationStore.getCollaborationInfo.question_id);
});

const terminateCollaboration = () => {
  try {
    isTerminated.value = true;
    collaborationStore.clearCollaborationInfo();
    chatRef.value?.sendStopMessage(); // Trigger the stop message in Chat component
    navigateTo('/');
  } catch (error) {
    console.error('Error in terminateCollaboration:', error);
  }
};
</script>

<template>
  <div class="page-container">
    <div class="question-box">
      <h3 class="question-title">{{ question?.title || "" }}</h3>
      <p>{{ question?.description || "" }}</p>
    </div>
    <AdviceBox style="padding-bottom: 20px;" v-if="question" :description="question.description" :uid="session_info.uid"/>
    <div style="display:flex; width:100%;">
      <div style="flex:2;">
        <Chat ref="chatRef" />
      </div>
      <div style="flex:3; overflow-y:auto; max-height: 500px; background-color: #282c34;">
        <CodeEditor :isTerminated="isTerminated" />
      </div>
    </div>
    <div style="margin-top: 8px; text-align: right; padding-bottom: 10px;">
      <button class="red-button" @click="terminateCollaboration">
        Terminate Collaboration
      </button>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  padding: 0 2rem;
}

.question-box {
  border: 1px solid #ccc;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 4px;
}

.question-title {
  font-weight: bold;
  margin-bottom: 0.5rem;
  text-align: center;
}

.red-button {
  background-color: rgb(254, 254, 254);
  border: 2px solid black;
  padding: 10px 20px;
  cursor: pointer;
  font-size: 16px;
  border-radius: 5px;
}

.red-button:hover {
  background-color: rgb(223, 223, 223);
}
</style>
