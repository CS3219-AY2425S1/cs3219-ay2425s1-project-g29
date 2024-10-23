<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import type { Question } from '~/types/Question';
import { useToast } from '@/components/ui/toast/use-toast';

const props = defineProps<{
  question: Question;
  refreshData: () => void;
  isOpen: boolean;
}>();

const emit = defineEmits(['update:isOpen']);

const { toast } = useToast();

const editedQuestion = reactive({
  title: '',
  description: '',
  category: '',
  difficulty: 'easy',
});

const errors = reactive({
  title: false,
  description: false,
  category: false,
});

watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    // Reset the form when the dialog opens
    editedQuestion.title = props.question.title;
    editedQuestion.description = props.question.description;
    editedQuestion.category = Array.isArray(props.question.category) 
      ? props.question.category.join(', ') 
      : props.question.category;
    editedQuestion.difficulty = props.question.difficulty;
  }
});

const validateForm = () => {
  let isValid = true;
  errors.title = !editedQuestion.title.trim();
  errors.description = !editedQuestion.description.trim();
  errors.category = !editedQuestion.category.trim();
  
  if (errors.title || errors.description || errors.category) {
    isValid = false;
  }
  
  return isValid;
};

const updateQuestion = async () => {
  if (!validateForm()) {
    toast({
      title: "Validation Error",
      description: "Please fill in all required fields.",
      variant: "destructive",
    });
    return;
  }

  try {
    const category_arr = editedQuestion.category.split(',').map(cat => cat.trim());

    const { data, error } = await useFetch(`http://localhost:5000/questions/${props.question.id}`, {
      method: 'PUT',
      body: JSON.stringify({
        title: editedQuestion.title,
        description: editedQuestion.description,
        category: category_arr,
        difficulty: editedQuestion.difficulty
      }),
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (error.value) {
      const errorMessage = await error.value?.data;
      toast({
        title: "Error updating question:",
        description: errorMessage.error,
        variant: "destructive",
      });
      console.error("Error updating question:", error.value);
    } else {
      console.log("Updated question successfully:", data.value);
      toast({
        title: "Success",
        description: "Question updated successfully",
      });
      props.refreshData();
      emit('update:isOpen', false); // Close the dialog only on successful update
    }
  } catch (err) {
    console.error("An error occurred while updating the question:", err);
  }
};
</script>

<template>
  <DialogContent class="sm:max-w-[525px]">
    <DialogHeader>
      <DialogTitle>Edit Question</DialogTitle>
      <DialogDescription>
        Update the details of the question
      </DialogDescription>
    </DialogHeader>
    <form @submit.prevent="updateQuestion" class="grid gap-5 py-4">
      <!-- Title -->
      <div class="grid grid-cols-4 items-center gap-4">
        <Label for="title">Title</Label>
        <div class="col-span-3">
          <Input id="title" v-model="editedQuestion.title" placeholder="Enter question title" :class="{ 'border-red-500': errors.title }" />
          <p v-if="errors.title" class="text-red-500 text-sm mt-1">Title is required</p>
        </div>
      </div>

      <div class="grid grid-cols-4 items-center gap-4">
        <Label for="description">Description</Label>
        <div class="col-span-3">
          <Textarea id="description" v-model="editedQuestion.description" placeholder="Enter question description"
            class="h-32" :class="{ 'border-red-500': errors.description }" />
          <p v-if="errors.description" class="text-red-500 text-sm mt-1">Description is required</p>
        </div>
      </div>

      <div class="grid grid-cols-4 items-center gap-4">
        <Label for="category">Category</Label>
        <div class="col-span-3">
          <Input id="category" v-model="editedQuestion.category" placeholder="Enter categories separated by commas"
            :class="{ 'border-red-500': errors.category }" />
          <p v-if="errors.category" class="text-red-500 text-sm mt-1">Category is required</p>
        </div>
      </div>

      <div class="grid grid-cols-4 items-center gap-4">
        <Label for="difficulty">Difficulty</Label>
        <Select id="difficulty" v-model="editedQuestion.difficulty">
          <SelectTrigger class="col-span-3">
            <SelectValue placeholder="Select a difficulty" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectItem value="easy">Easy</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="hard">Hard</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
      <Button type="submit" class="mt-4">
        Update
      </Button>
    </form>
  </DialogContent>
</template>