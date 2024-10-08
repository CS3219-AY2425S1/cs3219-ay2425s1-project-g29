<script setup lang="ts">
import { useToast } from '@/components/ui/toast/use-toast'
import ComboBox from '@/components/ComboBox.vue'
import { useWebSocket } from '@vueuse/core';
import { useCollaborationStore, type TCollaborationInfo } from '~/store/collaborationStore';
import { ref, onMounted } from 'vue';
const auth = useFirebaseAuth();
const user = useCurrentUser();
const runtimeConfig = useRuntimeConfig()
const collaborationStore = useCollaborationStore()
const { toast } = useToast()
const { status, data, send, open, close } = useWebSocket(`ws://localhost:8010/ws/${user?.value?.uid}`, {
  autoReconnect: true,
  onConnected: () => {
    console.log('Connected to WebSocket server')
  },
  onDisconnected: () => {
    console.log('Disconnected from WebSocket server')
  },
  onMessage: handleMessage,
});

const leetcodeTopics = ref<{ value: string; label: string }[]>([]);  // Set topics as a reactive ref
const difficulty = ref('easy')
const selectedCategory = ref('')
const isProcessing = ref(false)
const isMatching = ref(false)
const matchFound = ref(false)
const countdown = ref(30)
let countdownInterval: number | null = null

const fetchTopics = async () => {
  try {
    const { data, error } = await useFetch('http://localhost:5000/questions/categories')
    if (error.value) {
      throw new Error('Failed to fetch topics');
    }
    const categories = data.value.categories || [];
    // console.log('Categories', categories);
    leetcodeTopics.value = categories.map((category: string) => ({
      value: category,
      label: category
    }));
    selectedCategory.value = leetcodeTopics.value.length > 0 ? leetcodeTopics.value[0].value : '';
  } catch (err) {
    console.error('Error fetching topics:', err);
    toast({
      description: 'Failed to fetch topics.',
      variant: 'destructive',
    });
  }
};

onMounted(() => {
  fetchTopics();  // Fetch topics when the component mounts
});

async function handleMessage(ws: WebSocket, event: MessageEvent) {
  if (isMatching.value) {
    try {
      const message = JSON.parse(event.data);
      console.log('Received message:', message);
      resetCountdown();
      isMatching.value = false;
      updateCollaborationInfo(message);
    } catch (error) {
      console.error("Failed to parse message:", error);
    }
  }
}

async function updateCollaborationInfo(message: any) {
  const collaborationInfo: TCollaborationInfo = {
    user1_id: message.user1_id,
    user2_id: message.user2_id,
    uid: message.uid,
  };
  collaborationStore.setCollaborationInfo(collaborationInfo);

  if (collaborationStore.isCollaborating) {
    await navigateTo(`/collaboration`);
    toast({
      description: 'Match found! Redirecting to the collaboration room...',
    });
    matchFound.value = true;
  }
}

async function handleCancel() {
  try {
    const response = await $fetch(`${runtimeConfig.public.matchingRequestUrl}/matching/cancel`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: user.value?.uid
      })
    });

    isMatching.value = false;
  } catch (error: unknown) {
    isMatching.value = false;
    console.error("Failed to cancel matching:", error);
  }
}

async function handleSubmit() {
  isProcessing.value = true
  isMatching.value = true
  matchFound.value = false
  const body = JSON.stringify({
    user_id: user.value?.uid,
    difficulty: difficulty.value,
    category: selectedCategory.value
  })

  try {
    const response = await $fetch(`${runtimeConfig.public.matchingRequestUrl}/matching`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: body
    });
    startMatchTimeout()
    isProcessing.value = false
  } catch (error: unknown) {
    isMatching.value = false;
    matchFound.value = false
    const fetchError = createError(error as Partial<Error> & { data?: { error?: string } });
    if (fetchError?.data?.error) {
      console.error("Error from server:", fetchError.data.error);
    } else if (fetchError.message) {
      console.error("An error occurred:", fetchError.message);
    } else {
      console.error("An unknown error occurred:", error);
    }
  }
}

function startMatchTimeout() {
  countdown.value = 30
  countdownInterval = window.setInterval(() => {
    if (countdown.value > 0) {
      countdown.value -= 1
    } else {
      isMatching.value = false
      matchFound.value = false
      toast({
        description: 'Failed to find a match within the given time.',
        variant: 'destructive',
      });
      resetCountdown()
    }
  }, 1000)
}

function resetCountdown() {
  if (countdownInterval) {
    clearInterval(countdownInterval);
    countdownInterval = null;
  }
}

onUnmounted(() => {
  resetCountdown()
});
</script>

<template>
  <div class="min-h-full w-full flex flex-col justify-center items-center">
    <Card class="w-[420px]">
      <CardHeader>
        <div class="flex justify-center font-bold text-xl">
          Matching
        </div>
      </CardHeader>
      <CardContent class="space-y-5">
        <form @submit.prevent="handleSubmit" class="space-y-6 px-4">
          <div class="flex items-center justify-between">
            <Label for="difficulty" class="text-lg">Difficulty</Label>
            <Select id="difficulty" v-model="difficulty">
              <SelectTrigger class="w-[200px] font-medium px-4">
                <SelectValue placeholder="Select a difficulty level" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="easy">
                  Easy
                </SelectItem>
                <SelectItem value="medium">
                  Medium
                </SelectItem>
                <SelectItem value="hard">
                  Hard
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="flex items-center justify-between">
            <Label class="text-lg">Category</Label>
            <ComboBox :data="leetcodeTopics" v-model="selectedCategory" />
          </div>

          <div class="flex justify-center w-full">
            <div v-if="isMatching" class="text-center ">
              Matching... Time left: {{ countdown }} seconds
              <Button type="button" @click="handleCancel" class="w-3/4 mt-3">
                Cancel Matching
              </Button>
            </div>

            <Button v-else class="w-3/4 mt-3"
              :disabled="isProcessing || matchFound || collaborationStore.isCollaborating">
              Match
            </Button>
          </div>
        </form>
        <Button @click="collaborationStore.clearCollaborationInfo" class="w-full">
          Clear
        </Button>
      </CardContent>
    </Card>
  </div>
</template>
