<script setup lang="ts">
import { ref, reactive } from 'vue';
import type { Question } from '~/types/Question';
import { useToast } from '@/components/ui/toast/use-toast';

const props = defineProps<{ refreshData: () => void }>();

const { toast } = useToast();

const question = reactive<Question>({
    title: "",
    description: "",
    category: "",
    difficulty: "easy",
});

const errors = reactive({
    title: false,
    description: false,
    category: false,
});

const isDialogOpen = ref(false);

const validateForm = () => {
    let isValid = true;
    errors.title = !question.title.trim();
    errors.description = !question.description.trim();
    errors.category = !question.category.trim();
    
    if (errors.title || errors.description || errors.category) {
        isValid = false;
    }
    
    return isValid;
};

const submitQuestion = async () => {
    if (!validateForm()) {
        toast({
            title: "Validation Error",
            description: "Please fill in all required fields.",
            variant: "destructive",
        });
        return;
    }

    try {
        const category_arr = question.category.split(',').map(cat => cat.trim());
        
        const { data, error } = await useFetch('http://localhost:5000/questions', {
            method: 'POST',
            body: JSON.stringify({
                title: question.title,
                description: question.description,
                category: category_arr,
                difficulty: question.difficulty
            }),
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (error.value) {
            const errorMessage = await error.value?.data;  
            toast({
                title: "Error submitting question:",
                description: errorMessage.error,
                variant: "destructive",
            });
            console.error("Error submitting question:", errorMessage.error);
        } else {
            console.log("Submitted question successfully:", data.value);
            props.refreshData();
            isDialogOpen.value = false; // Close the dialog only on successful submission
        }
    } catch (err) {
        console.error("An error occurred while submitting the question:", err);
    }
};
</script>

<template>
    <Dialog v-model:open="isDialogOpen">
        <DialogTrigger as-child>
            <Button class="font-semibold text-md" @click="isDialogOpen = true">
                Add Question
            </Button>
        </DialogTrigger>
        <DialogContent class="sm:max-w-[525px]">
            <DialogHeader>
                <DialogTitle>Add Question</DialogTitle>
                <DialogDescription>
                    Fill in the details of the new question
                </DialogDescription>
            </DialogHeader>
            <form @submit.prevent="submitQuestion" class="grid gap-5 py-4">
                <!-- Title -->
                <div class="grid grid-cols-4 items-center gap-4">
                    <Label for="title">Title</Label>
                    <div class="col-span-3">
                        <Input id="title" v-model="question.title" placeholder="Enter question title" :class="{ 'border-red-500': errors.title }" />
                        <p v-if="errors.title" class="text-red-500 text-sm mt-1">Title is required</p>
                    </div>
                </div>

                <div class="grid grid-cols-4 items-center gap-4">
                    <Label for="description">Description</Label>
                    <div class="col-span-3">
                        <Textarea id="description" v-model="question.description" placeholder="Enter question description"
                            class="h-32" :class="{ 'border-red-500': errors.description }" />
                        <p v-if="errors.description" class="text-red-500 text-sm mt-1">Description is required</p>
                    </div>
                </div>

                <div class="grid grid-cols-4 items-center gap-4">
                    <Label for="category">Category</Label>
                    <div class="col-span-3">
                        <Input id="category" v-model="question.category" placeholder="Enter categories separated by commas"
                            :class="{ 'border-red-500': errors.category }" />
                        <p v-if="errors.category" class="text-red-500 text-sm mt-1">Category is required</p>
                    </div>
                </div>

                <div class="grid grid-cols-4 items-center gap-4">
                    <Label for="difficulty">Difficulty</Label>
                    <Select id="difficulty" v-model="question.difficulty">
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
                    Submit
                </Button>
            </form>
        </DialogContent>
    </Dialog>
</template>