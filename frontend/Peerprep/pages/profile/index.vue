<script setup lang="ts">
import { useAuthStore } from '~/stores/auth';
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
    try {
        const response = await fetch(`/api/questions/${question_id}`);

        if (!response.ok) {
            console.error(`Error fetching question info: ${response.status} ${response.statusText}`);
            return undefined;
        }

        const data = await response.json();

        if (data) {
            return data;
        }
    } catch (error) {
        console.error("Error fetching question info:", error);
        return undefined;
    }
    return undefined;
}

const getUserDisplayName = async (user_id: string) => {  // This function might be a security risk, consider moving it to user service
    try {
        const response = await fetch(`/api/users/${user_id}`);

        if (!response.ok) {
            console.error(`Error fetching user data: ${response.status} ${response.statusText}`)
            return "Deleted User";
        }
        const data = await response.json();

        if (data && data.user && data.user.displayName) {
            return data.user.displayName;
        }
    } catch (e) {
        console.error("Error fetching user data:", e);
        return "Unknown User";
    }
    return "Unknown User";
}

const convertEpochToDateTime = (epochTime: number) => {
    let date = new Date(epochTime * 1000);
    let dateString = date.toLocaleString();
    return dateString;
}

const capitalizeFirstLetter = (inputString: string) => {
    if (!inputString) {
        return '';
    }
    return inputString.charAt(0).toUpperCase() + inputString.slice(1);
};

const fetchAttemptList = async () => {
    try {
        isLoading.value = true;

        const token = await authStore.getToken();
        const response = await fetch(`/api/users/${user.value.uid}/history`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(`Error getting attempt list: ${response.status} ${response.statusText}`);
        }

        if (data) {
            await updateAttemptList(data);
        }
    } catch (e) {
        console.error("Error while fetching attempt history:", e);
    } finally {
        isLoading.value = false;
    }
}

const updateAttemptList = async (listOfAttempts: QuestionAttemptNet[]) => {
    const attemptsWithQuestionInfo = await Promise.all(
        listOfAttempts.sort((a: QuestionAttemptNet, b: QuestionAttemptNet) => b.timestamp - a.timestamp)
            .map(async (attempt: QuestionAttemptNet, index: number) => {
                const questionInfo = await getQuestionInfo(attempt.question_id);
                let questionTitle = "";
                let questionDifficulty = "";
                let questionCategory = "";
                if (questionInfo) {
                    questionTitle = questionInfo.title;
                    questionDifficulty = capitalizeFirstLetter(questionInfo.difficulty);
                    questionCategory = questionInfo.category.toString();
                } else {
                    questionTitle = "Unknown Question";
                    questionDifficulty = "Unknown Question";
                    questionCategory = "Unknown Question";
                }

                const matchedUser = await getUserDisplayName(attempt.matched_user);
                return {
                    index: index + 1,
                    sessionId: attempt.session_id,
                    dateTime: convertEpochToDateTime(attempt.timestamp),
                    matchedUser: matchedUser,
                    questionTitle: questionTitle,
                    questionDifficulty: questionDifficulty,
                    questionCategory: questionCategory,
                }
            })
    )

    attemptList.value = attemptsWithQuestionInfo;
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
            <AttemptHistoryListTable v-else :data="attemptList" :key="attemptList.length" />
        </div>
    </div>
</template>
