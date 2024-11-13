<script setup lang="ts">
import { doc, getDoc } from 'firebase/firestore';
import { useAuthStore } from '~/stores/auth';
import { useRoute } from 'vue-router'

const authStore = useAuthStore();
const firebaseApp = useFirebaseApp();
const firestoreDb = useFirestore(firebaseApp);
const route = useRoute();
const sessionId = route.params.sessionId;


const attemptTimestamp = ref<string>("");
const codeAttempt = ref<string>("");
const isLoading = ref(true);
const matchedUserDisplayName = ref<string>("");
const questionInfo = ref();

const { user } = storeToRefs(authStore);


const getAttemptInfo = async (uid: string) => {
    try {
        const response = await fetch(`/api/users/${uid}/history/${sessionId}`);

        const data = await response.json()

        if (!response.ok) {
            throw new Error(`Error getting Attempt Info: ${response.status} ${response.statusText}`);
        }

        if (data && data.matched_user && data.question_id && data.timestamp) {
            return data;
        }
        throw new Error(`Error getting Attempt Info: Data malformed ${data}`);
    } catch (e) {
        console.error(e);
        return undefined;
    }
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

const getCodingAttempt = async () => {
    const docRef = doc(firestoreDb, 'collaborations', sessionId);

    // Check if the document exists
    const docSnap = await getDoc(docRef);
    if (!docSnap.exists()) {
        return "Attempt Not Found."
    }

    const data = docSnap.data();

    if (data && data.code !== undefined) {
        return JSON.stringify({ code: data.code });
    } else {
        return "Code field not found in the document.";
    }
}

const getInfo = async () => {
    // Get User ID
    const userId = user.value?.uid;

    // Get Attempt Info
    const attemptInfo = await getAttemptInfo(userId);
    matchedUserDisplayName.value = await getUserDisplayName(attemptInfo.matched_user);
    const questionId = attemptInfo.question_id;
    attemptTimestamp.value = convertEpochToDateTime(attemptInfo.timestamp);

    // Get Question Info
    questionInfo.value = await getQuestionInfo(questionId);

    // Get Coding Attempt
    const receivedCodingAttempt = await getCodingAttempt();
    codeAttempt.value = JSON.parse(receivedCodingAttempt).code;

    isLoading.value = false;
}

onMounted(getInfo);

</script>

<template>
  <div class="container mx-auto py-10">
    <div v-if="isLoading" class="text-gray-500">Loading Attempt Details...</div>
    <div v-else>
      <h2 class="text-2xl font-semibold mb-4">{{ questionInfo?.title || 'Question' }}</h2>
      <p><strong>Description:</strong> {{ questionInfo?.description }}</p>
      <p><strong>Category:</strong> {{ questionInfo?.category.toString() }}</p>
      <p><strong>Difficulty:</strong> {{ capitalizeFirstLetter(questionInfo?.difficulty) }}</p>

      <h3 class="text-xl font-semibold mt-6 mb-2">Your Attempt:</h3>
      <pre class="bg-gray-100 p-4 rounded-md overflow-auto">{{ codeAttempt || 'No code available' }}</pre>

      <p class="mt-4"><strong>Matched on:</strong> {{ attemptTimestamp }}</p>
      <p><strong>Matched User:</strong> {{ matchedUserDisplayName || 'N/A' }}</p>
      <p><strong>Session ID:</strong> {{ sessionId || 'N/A' }}</p>
    </div>
  </div>
</template>
