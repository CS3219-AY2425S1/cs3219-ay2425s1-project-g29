<script setup lang="ts">
import { ref, onMounted, onUnmounted, defineExpose } from 'vue';
import Toaster from '@/components/ui/toast/Toaster.vue';
import { io } from "socket.io-client";
import axios from 'axios';
import { useCollaborationStore } from '~/stores/collaborationStore';

// Define the Message interface
interface Message {
  id: string;
  username: string;
  message: string;
  timestamp: string;
  avatar?: string;
}

const user = useCurrentUser();
const runtimeConfig = useRuntimeConfig();
const collaborationStore = useCollaborationStore();

// Connect to Socket.IO server
const socket = io(runtimeConfig.public.chatService); // Server address

// Define response status
const messages = ref<Message[]>([]);
const message = ref('');
const selectedConversation = ref<string | null>(null); // Track selected conversation
const collaborationActive = ref(true); // Track collaboration status

// Function for sending message
const sendMessage = () => {
  if (!collaborationActive.value) return; // Prevent sending if collaboration is inactive
  
  if (message.value.trim() && selectedConversation.value) {
    const messageData = {
      conversation: selectedConversation.value,
      message: message.value,
      username: user?.value?.email,
    };
    socket.emit('chat message', messageData);
    message.value = ''; // Clear input text box
  }
};

// Function for sending "stop" message
const sendStopMessage = () => {
  if (selectedConversation.value) {
    socket.emit('chat message', { 
      conversation: selectedConversation.value, 
      message: "user has exited collaboration", 
      username: user?.value?.email 
    });
    collaborationActive.value = false; // Disable send box immediately
  }
};

// Function to receive messages
const receiveMessage = (msg: { conversation: string; message: Message }) => {
  if (msg.conversation === selectedConversation.value) {
    messages.value.push(msg.message);
    // Sort messages by timestamp after adding the new message
    messages.value.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
    
    // Check if the received message indicates termination
    if (msg.message.message === "user has exited collaboration") {
      collaborationActive.value = false;
    }
  }
};

// Function to format timestamp
const formatTimestamp = (timestamp: string | number | Date) => {
  let date: Date;

  if (typeof timestamp === 'number') {
    if (timestamp.toString().length === 10) {
      date = new Date(timestamp * 1000); // Convert seconds to milliseconds
    } else {
      date = new Date(timestamp);
    }
  } else if (typeof timestamp === 'string') {
    const isoRegex = /^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(\.\d{1,3})?\d*$/;
    const match = timestamp.match(isoRegex);
    let processedTimestamp = timestamp;

    if (match) {
      const [_, main, fraction] = match;
      if (fraction) {
        let milliseconds = fraction.substring(0, 4);
        while (milliseconds.length < 4) {
          milliseconds += '0';
        }
        processedTimestamp = `${main}${milliseconds}Z`;
      } else {
        processedTimestamp = `${main}.000Z`;
      }
    } else {
      processedTimestamp = `${timestamp}Z`;
    }

    date = new Date(processedTimestamp);
  } else {
    date = new Date(timestamp);
  }

  if (isNaN(date.getTime())) {
    console.error("Invalid date format:", timestamp);
    return "Invalid date";
  }

  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

// Function to load the active conversation
const loadActiveConversation = async () => {
  try {
    const response = await axios.get(`${runtimeConfig.public.chatService}/api/conversations/${user?.value?.uid}`);
    const activeConversation = response.data.conversations.find((conv: any) => conv.flag === 'active');
    if (activeConversation) {
      selectedConversation.value = activeConversation.sessionName;
      loadHistory(activeConversation.sessionName);
    } else {
      console.warn('No active conversation found.');
      handleInactiveSession();
    }
  } catch (error) {
    console.error('Error loading active conversation:', error);
    handleInactiveSession();
  }
};

// Function to handle inactive session scenarios
const handleInactiveSession = () => {
  collaborationActive.value = false;
  // Optionally, you can clear the collaboration info from the store
  // collaborationStore.clearCollaborationInfo();
};

// Function to load chat history
const loadHistory = async (conversation: string) => {
  try {
    const response = await axios.get(`${runtimeConfig.public.chatService}/api/history/${conversation}`);
    messages.value = response.data.messages;
    selectedConversation.value = conversation;

    // Sort messages by timestamp after loading history
    messages.value.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

    // Check if any message indicates termination
    const terminationMessage = messages.value.find(msg => msg.message === "user has exited collaboration");
    if (terminationMessage) {
      collaborationActive.value = false;
    }
  } catch (error) {
    console.error('Error loading history:', error);
    handleInactiveSession();
  }
};

// When component is mounted, set up Socket.IO events
onMounted(() => {
  socket.on('chat message', receiveMessage);
  
  // Load the active conversation on mount
  loadActiveConversation();

  // Make sure the users do not get redirected faster than socket 
  setTimeout(async () => {
    if (!selectedConversation.value) {
      await loadActiveConversation();
    }
  }, 500);
});

// When component is unmounted, remove Socket.IO events
onUnmounted(() => {
  socket.off('chat message', receiveMessage);
});

// Expose necessary functions
defineExpose({
  sendStopMessage
});
</script>

<template>
  <div class="container py-10 mx-auto flex">
    <!-- Chat Window -->
    <div class="chat-window">
      <div id="messages" class="messages">
        <div v-for="msg in messages" :key="msg.id" class="message-item">
          <div class="avatar">
            <img :src="msg.avatar" :alt="msg.username" />
          </div>
          <div class="message-content">
            <div class="username">{{ msg.username }}</div>
            <div class="text">{{ msg.message }}</div>
            <div class="timestamp">{{ formatTimestamp(msg.timestamp) }}</div>
          </div>
        </div>
      </div>
      <input
        v-model="message"
        @keyup.enter="sendMessage"
        placeholder="Message..."
        class="input-message"
        :disabled="!collaborationActive"
      />
      <button 
        @click="sendMessage" 
        :disabled="!collaborationActive" 
        :class="{'disabled-button': !collaborationActive}" 
        class="send-button">
        Send
      </button>
      <button @click="sendStopMessage" class="stop-button">Stop</button>
    </div>
  </div>
  <Toaster />
  <div v-if="!collaborationActive" class="notification">
    Session ended. Click "Terminate Collaboration" to return to the main page.
  </div>
</template>

<style scoped>
.container {
  display: flex;
  justify-content: center; /* Center the chat window */
}

.chat-window {
  width: 100%; /* Take full width since conversation list is removed */
  padding: 20px;
}

.messages {
  border: 1px solid #ccc;
  padding: 10px;
  height: 400px;
  overflow-y: auto;
}

.message-item {
  display: flex;
  margin-bottom: 10px;
}

.avatar img {
  display: none;
}

.message-content {
  flex-grow: 1;
}

.username {
  font-weight: bold;
}

.timestamp {
  font-size: 12px;
  color: #888;
}

.input-group {
  display: flex;
  align-items: center;
  margin-top: auto; /* Push input group to bottom */
}

.input-message {
  width: 80%;
  flex-grow: 1; /* Msg box occupying left space */
  padding: 10px; /* Adding inner margin */
  margin-right: 10px; /* Inner margin with send btn */
  border: 1px solid #ccc;
  border-radius: 4px;
}

.send-button {
  padding: 10px 20px; /* Inner padding */
  background-color: #007bff; /* Send btn color */
  color: white; /* Text color */
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.disabled-button {
  background-color: #cccccc;
  cursor: not-allowed;
}

.stop-button {
  display: none;
}

.send-button:hover {
  background-color: #0056b3;
}

.notification {
  background-color: #ffdddd;
  border-left: 6px solid #f44336;
  padding: 10px;
  margin-top: 10px;
  border-radius: 4px;
  text-align: center;
}
</style>
