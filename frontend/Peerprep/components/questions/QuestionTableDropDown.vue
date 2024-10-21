<script setup lang="ts">
import type { Question } from '~/types/Question';
import { MoreHorizontal } from 'lucide-vue-next'
import EditQuestionDialog from './EditQuestionDialog.vue';
import { useToast } from '@/components/ui/toast/use-toast';

const props = defineProps<{
    question: Question
}>()

const { toast } = useToast();

const emit = defineEmits(['refresh']);

const deleteQuestion = async () => {
  try {
    const { error } = await useFetch(`http://localhost:5000/questions/${props.question.id}`, {
      method: 'DELETE',
    });
    
    if (error.value) {
      console.error('Error deleting question:', error.value);
    } else {
      console.log('Deleted question successfully');
      emit('refresh');
    }
  } catch (err) {
    console.error('An error occurred while deleting the question:', err);
  }
};

const isEditDialogOpen = ref(false);

const openEditDialog = () => {
  isEditDialogOpen.value = true;
};

const closeEditDialog = () => {
  isEditDialogOpen.value = false;
};

const refreshData = () => {
  emit('refresh');
  closeEditDialog();
};
</script>

<template>
    <DropdownMenu>
        <DropdownMenuTrigger as-child>
            <Button variant="ghost" class="w-8 h-8 p-0">
                <span class="sr-only">Open menu</span>
                <MoreHorizontal class="w-4 h-4" />
            </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <DropdownMenuItem @click="openEditDialog">Edit</DropdownMenuItem>
            <DropdownMenuItem @click="deleteQuestion">Delete</DropdownMenuItem>
        </DropdownMenuContent>
    </DropdownMenu>

    <Dialog :open="isEditDialogOpen" @update:open="closeEditDialog">
        <EditQuestionDialog 
            :question="question"
            :refreshData="refreshData"
            :isOpen="isEditDialogOpen"
            @update:isOpen="isEditDialogOpen = $event"
        />
    </Dialog>
</template>