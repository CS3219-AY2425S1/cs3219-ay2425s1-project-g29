<script setup lang="ts">
import { useAuthStore } from '~/stores/auth';
import { ref } from 'vue';
import type { UserProfile } from '~/types/UserProfile';
import type { QuestionAttempt, QuestionAttemptNet } from '~/types/QuestionAttempt';
import AvatarFallback from '~/components/ui/avatar/AvatarFallback.vue';

const attemptList = ref<QuestionAttempt[]>([]);
const isLoading = ref(true);

const authStore = useAuthStore();
const { user } = storeToRefs(authStore);

const userProfile = ref<UserProfile>({
    displayName: '',
    email: '',
    photoURL: '',
})

const getInitials = () => {
    const name = user.value?.displayName || '';
    const words = name.split(' ');
    const initials = words[0][0].toUpperCase() + (words[1] ? words[1][0].toUpperCase() : '');
    return initials;
}

const getQuestionInfo = async (question_id: string) => {
    const { data, error } = await useFetch(`http://localhost:5000/questions/${question_id}`)

    if (error.value) {
        throw new Error(error.value.message);
    }

    if (data.value !== undefined) {
        return data.value;
    }

    throw new Error("Received undefined value from Question Service");
}

const getUserDisplayName = async (user_id: string) => {  // This function might be a security risk, consider moving it to user service
    const { data, error } = await useFetch(`http://localhost:5001/users/${user_id}`);

    if (error.value) {
        throw new Error(error.value.message);
    }

    if (data.value !== undefined) {
        return data.value.user.displayName;
    }

    throw new Error("Received undefined value from User Service")
}

const convertEpochToDateTime = (epochTime: number) => {
    let date = new Date(epochTime * 1000);
    let dateString = date.toLocaleString();
    return dateString;
}

const capitalizeFirstLetter = (inputString: string) => {
    return inputString.charAt(0).toUpperCase() + inputString.slice(1);
};

const fetchAttemptList = async () => {
    try {
        isLoading.value = true;

        // TODO: SEND AUTHORIZATION TOKEN HERE TO VERIFY
        const { data, error: fetchError } = await useFetch(`http://localhost:5001/users/${user.value.uid}/history`);

        if (fetchError.value) {
            throw new Error(fetchError.value.message);
        }

        if (data.value) {
            const listOfAttempts = data.value;

            const attemptsWithQuestionInfo = await Promise.all(
                listOfAttempts.map(async (attempt: QuestionAttemptNet, index: number) => {
                    const questionInfo = await getQuestionInfo(attempt.question_id);
                    const questionTitle = questionInfo.title;
                    const questionDifficulty = capitalizeFirstLetter(questionInfo.difficulty);
                    const questionCategory = questionInfo.category.toString();

                    const matchedUser = await getUserDisplayName(attempt.matched_user);

                    return {
                        index: index + 1,
                        sessionId: attempt.session_id,
                        dateTime: convertEpochToDateTime(attempt.timestamp),
                        matchedUser: matchedUser,  // Request from User Service User Display Name
                        questionTitle: questionTitle,  // For now
                        questionDifficulty: questionDifficulty,
                        questionCategory: questionCategory,
                    }
                })
            )

            attemptList.value = attemptsWithQuestionInfo;
        }
    } catch (e) {
        console.error("Error while fetching attempt history:", e);
    } finally {
        isLoading.value = false;
    }
}

onMounted(() => {
    if (user.value) {
        userProfile.value.displayName = user.value.displayName;
        userProfile.value.photoURL = user.value.photoURL;
        userProfile.value.email = user.value.email;
    }
    isLoading.value = false;
    
    fetchAttemptList();
});
</script>

<template>
    <div class="container mx-auto py-10">
        <!-- User Info Section -->
        <div class="flex items-center space-x-6">
            <!-- Profile Picture -->
            <div class="w-20 h-20 rounded-full bg-gray-200 flex items-center justify-center">
                <Avatar size="s" class="flex items-center justify-center">
                    <AvatarImage :src="userProfile.photoURL || ''" alt="{{ getInitials() }}" />
                    <AvatarFallback class="bg-gray-200 text-2xl font-bold">{{ getInitials() }}</AvatarFallback>
                </Avatar>
            </div>

            <!-- User Info -->
            <div>
                <h2 class="text-2xl font-semibold">
                    {{ userProfile.displayName || 'Anonymous' }}
                </h2>
                <p class="text-gray-500">{{ userProfile.email }}</p>
            </div>

            <!-- Edit Profile Button -->
            <div>
                <router-link to="/profile/settings">
                    <Button class="btn bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">
                        Account Settings
                    </Button>
                </router-link>
            </div>
        </div>

        <h2 class="text-2xl font-semibold mt-10">Attempt History:</h2>

        <!-- Match History Section -->
        <div class="mt-4">
            <div v-if="isLoading" class="text-gray-500">Loading History...</div>
            <AttemptHistoryListTable
                v-else
                :data="attemptList"
                :key="attemptList.length"
            />
        </div>
    </div>
</template>
