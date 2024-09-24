<script setup lang="ts">
import { ref } from 'vue';
import QuestionTable from '@/components/questions/QuestionTable.vue';
import type { Question } from '~/types/Question';
import Toaster from '@/components/ui/toast/Toaster.vue';

const questions = ref<Question[]>([]);

const fetchQuestions = async () => {
  const { data, error } = await useFetch('http://localhost:5000/questions')
  if (error.value) {
    console.error('Error fetching questions:', error.value);
  } else if (data.value) {
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
};

// Fetch questions initially
fetchQuestions();

const refreshData = () => {
  fetchQuestions();
};
</script>

<template>
  <div class="container py-10 mx-auto">
    <QuestionTable :data="questions" :refresh-data="refreshData" :key="questions"/>
  </div>
  <Toaster />
</template>