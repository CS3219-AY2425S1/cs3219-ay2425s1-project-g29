<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import QuestionTable from '@/components/questions/QuestionTable.vue';
import type { Question } from '~/types/Question';
import Toaster from '@/components/ui/toast/Toaster.vue';

const questions = ref<Question[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

const fetchQuestions = async () => {
  try {
    isLoading.value = true;
    error.value = null;
    const { data, error: fetchError } = await useFetch('http://localhost:5000/questions')
    if (fetchError.value) {
      throw new Error(fetchError.value.message);
    }
    if (data.value) {
      questions.value = data.value
        .sort((a, b) => a.title.localeCompare(b.title))
        .map((question, index) => ({
          id: question.id,
          title: question.title,
          description: question.description,
          category: Array.isArray(question.category) ? question.category.join(', ') : question.category,
          difficulty: question.difficulty,
          index: index + 1
        }));
    }
  } catch (err) {
    console.error('Error fetching questions:', err);
    error.value = err instanceof Error ? err.message : 'An unknown error occurred';
  } finally {
    isLoading.value = false;
  }
};

let intervalId: number | null = null;

onMounted(() => {
  fetchQuestions(); // Fetch immediately on mount
  intervalId = setInterval(fetchQuestions, 5000); // Then every 5 seconds
});

onUnmounted(() => {
  if (intervalId !== null) {
    clearInterval(intervalId); // Clean up the interval when the component is unmounted
  }
});

const refreshData = () => {
  fetchQuestions(); // Manually refresh data
};
</script>

<template>
  <div class="container py-10 mx-auto">
    <div v-if="isLoading && questions.length === 0">Loading...</div>
    <div v-else-if="error">An error occurred: {{ error }}</div>
    <QuestionTable 
      v-else 
      :data="questions" 
      :refresh-data="refreshData" 
      :key="questions.length"
    />
  </div>
  <Toaster />
</template>