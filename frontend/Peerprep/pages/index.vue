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
const { status, data, send, open, close } = useWebSocket(`${runtimeConfig.public.webSocketUrl}/ws/${user?.value?.uid}`, {
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
    const { data, error } = await useFetch(`/api/questions/categories`)
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
      } else if (status === 'no_question') {
        console.log('No question found for the category:', message.status);
        toast({
          description: `No question found for the category: ${message.category}. Please try again.`,
          variant: 'destructive',
        });
      } else {
        await updateCollaborationInfo(message, status);

        const collaborationInfo = collaborationStore.getCollaborationInfo;

        if (!collaborationInfo) {
          throw new Error('Collaboration information is missing.');
        }

        const sessionId = collaborationInfo.uid; // Use the uid as session ID
        console.log('Using session ID from collaborationStore:', sessionId);
        const formattedStatus = message.status[0].toUpperCase() + status.slice(1);
        if (is_user1) {
          const ack = {
            status: "success",
            uid: message.uid
          };
          send(JSON.stringify(ack));
          console.log('sending ack:', ack);
          toast({
            description: `${formattedStatus} found! Matched with user ${message.user2_id}. Question ID: ${message.question_id}. Difficulty: ${message.actual_difficulty}. Category: ${message.category}`,
          });
          createSession(sessionId, message.user1_id); // Use sessionId from store
        } else {
          createSession(sessionId, message.user2_id); // Use sessionId from store
          toast({
            description: `${formattedStatus} found! Matched with user ${message.user1_id}. Question ID: ${message.question_id}. Difficulty: ${message.actual_difficulty}. Category: ${message.category}`,
          });
        }

        if (collaborationStore.isCollaborating) {
          await navigateTo(`/collaboration`);
          matchFound.value = true;
        }
      }
    } catch (error) {
      console.error("Failed to process received message:", error);
    }
  } else if (is_user1) {
    const ack = {
      status: "error",
      uid: message.uid
    };
    send(JSON.stringify(ack));
  }
}




function createSession(sessionId: string, username: string) {
  fetch(`${runtimeConfig.public.chatService}/api/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ sessionname: sessionId, username }) // Pass sessionId as sessionname
  })
    .then(response => {
      if (response.ok) {
        return response.json();
      }
      throw new Error('Failed to create session');
    })
    .then(data => {
      console.log('Session created:', data);
    })
    .catch(error => {
      console.error('Error:', error);
    });
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
    const response = await $fetch(`/api/matching/cancel/${user.value?.uid}`, {
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

  const response = await $fetch(`/api/matching`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: body
  });
  startMatchTimeout()
  isProcessing.value = false
  console.log('Match response:', response);
  if (response && typeof response === "object" && 'error' in response && response.error) {
    isMatching.value = false;
    matchFound.value = false
    isProcessing.value = false
    resetCountdown()
    console.error("An error occurred:", response.error);
    toast({
      description: String(response.error),
      variant: 'destructive',
    });
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
