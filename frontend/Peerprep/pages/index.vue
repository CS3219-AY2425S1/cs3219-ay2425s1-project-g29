<script setup lang="ts">
import { useToast } from '@/components/ui/toast/use-toast'
import ComboBox from '@/components/ComboBox.vue'
import { useWebSocket } from '@vueuse/core';
import { useCollaborationStore, type TCollaborationInfo } from '~/stores/collaborationStore';
import { ref, onMounted } from 'vue';
const user = useCurrentUser();
const runtimeConfig = useRuntimeConfig()
const collaborationStore = useCollaborationStore()
const { toast } = useToast()
const { status, data, send, open, close } = useWebSocket(`ws://localhost:8001/ws/${user?.value?.uid}`, {
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
const isMatching = ref<boolean>(false)
const matchFound = ref(false)
const countdown = ref(30)
let countdownInterval: number | null = null

const fetchTopics = async () => {
  try {
    const { data, error } = await useFetch('http://localhost:5000/questions/categories')
    if (error.value) {
      throw new Error('Failed to fetch topics');
    }
    const categories = (data.value as { categories: string[] }).categories || [];
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


async function handleMessage(ws: WebSocket, event: MessageEvent) {

  const message = JSON.parse(event.data);
  const is_user1 = message.user1_id === user.value?.uid;
  if (isMatching.value) {
    try {
      console.log('Received message:', message);
      resetCountdown();
      isMatching.value = false;
      const status = message.status;
      console.log('status:', status);
      if (status === 'cancelled') {
        console.log('Match was cancelled by the other user');
        toast({
          description: 'The match was canceled by the other user. Please try again.',
          variant: 'destructive',
        });
        console.log('Match was cancelled by the other user');
      } else if (status === 'no_question') {
        console.log('No question found for the category:', message.status);
        toast({
          description: `No question found for the category: ${message.category}. Please try again.`,
          variant: 'destructive',
        });
      }
      else {

        const formattedStatus = message.status[0].toUpperCase() + status.slice(1);
        if (is_user1) {

          const ack = {
            status: "success",
            uid: message.uid
          }
          send(JSON.stringify(ack));
          console.log('sending ack:', ack);
          toast({
            description: `${formattedStatus} found! Matched with user ${message.user2_id}. Question ID: ${message.question_id}. Difficulty: ${message.difficulty}. Category: ${message.category}`,
          });
        } else {
          toast({
            description: `${formattedStatus} found! Matched with user ${message.user1_id}. Question ID: ${message.question_id}. Difficulty: ${message.difficulty}. Category: ${message.category}`,
          });
        }
        updateCollaborationInfo(message, status);
        // if (collaborationStore.isCollaborating) {
        //   await navigateTo(`/collaboration`);
        //   toast({
        //     description: `${status} found! Redirecting to the collaboration room...`,
        //   });
        //   matchFound.value = true;
        // }
      }
    } catch (error) {
      console.error("Failed to process received message:", error);
    }
  } else if (is_user1) {
    const ack = {
      status: "error",
      uid: message.uid
    }
    send(JSON.stringify(ack));
  }
}

async function updateCollaborationInfo(message: any, status: string) {
  const collaborationInfo: TCollaborationInfo = {
    user1_id: message.user1_id,
    user2_id: message.user2_id,
    uid: message.uid,
    question_id: message.question_id,
  };
  collaborationStore.setCollaborationInfo(collaborationInfo);


}

async function handleCancel() {

  const token = await user.value?.getIdToken();
  try {
    const response = await $fetch(`${runtimeConfig.public.matchingRequestUrl}/cancel/${user.value?.uid}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
    }
    );
    isMatching.value = false;
    matchFound.value = false;
    resetCountdown();
    toast({
      description: 'Matching canceled successfully.',
    });
  } catch (error: unknown) {
    const fetchError = error as { data?: any };
    console.error("Failed to cancel matching:", fetchError.data);
    toast({
      description: 'Failed to cancel matching.',
      variant: 'destructive',
    });
  }
}

type MatchResponse = {
  message: string;
}

async function handleSubmit() {

  const token = await user.value?.getIdToken();
  isProcessing.value = true
  isMatching.value = true
  matchFound.value = false
  const body = JSON.stringify({
    user_id: user.value?.uid,
    difficulty: difficulty.value,
    category: selectedCategory.value
  })

  try {
    const response: MatchResponse = await $fetch(`${runtimeConfig.public.matchingRequestUrl}/matching`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: body
    });
    startMatchTimeout()
    isProcessing.value = false
  } catch (error: unknown) {
    isMatching.value = false;
    matchFound.value = false
    isProcessing.value = false
    const fetchError = createError(error as Partial<Error> & { data?: { error?: string } });
    if (fetchError?.data?.error) {
      console.error("Error from server:", fetchError.data.error);
      toast({
        description: fetchError.data.error,
        variant: 'destructive',
      });
    } else if (fetchError.message) {
      console.error("An error occurred:", fetchError.message);
      toast({
        description: 'An error occurred while trying to find a match.',
        variant: 'destructive',
      });
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

function handleBeforeUnload(event: BeforeUnloadEvent) {
  console.log('Before unload event triggered');
  if (isMatching.value) {
    console.log('Cancelling matching before unloading');
    handleCancel();
    event.preventDefault();
  }
}
onMounted(() => {
  fetchTopics();
  window.addEventListener('beforeunload', handleBeforeUnload);
}
);

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload);
});

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
            <!--
            <Button v-else class="w-3/4 mt-3"
              :disabled="isProcessing || matchFound || collaborationStore.isCollaborating">
              Match
            </Button>
            -->

            <Button v-else class="w-3/4 mt-3" :disabled="isProcessing">
              Match
            </Button>
          </div>
        </form>
        <!--
        <Button @click="collaborationStore.clearCollaborationInfo" class="w-full">
          Clear
        </Button>
        -->
      </CardContent>
    </Card>
  </div>
</template>
