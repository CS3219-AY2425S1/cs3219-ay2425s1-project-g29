<template>
  <div class="advice-box">
    <button @click="fetchAdvice('general')" class="advice-button">Get General Advice</button>
    <button @click="fetchAdvice('styling')" class="advice-button">Get Styling Advice</button>
    <button @click="fetchAdvice('optimization')" class="advice-button">Get Optimization Advice</button>
    
    <div class="advice-content">
      <h4 v-if="adviceType">{{ adviceType }} Advice:</h4>
      <p v-if="advice">{{ advice }}</p>
      <p v-else>No advice yet. Click a button to get advice.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watchEffect } from "vue";
import { useChatgpt } from '#imports';
import { useFirebaseApp, useFirestore, useDocument } from 'vuefire';
import { collection, doc } from "firebase/firestore";

const props = defineProps({
  description: {
    type: String,
    required: true
  },
  uid: {
    type: String,
    required: true
  }
});

const { chat } = useChatgpt();
const advice = ref('');
const adviceType = ref('');

const firebaseApp = useFirebaseApp();
const db = useFirestore(firebaseApp);
const docRef = useDocument(doc(collection(db, 'collaborations'), props.uid))

const code = ref('');
watchEffect(() => {
  if (docRef.value) {
    code.value = docRef.value.code || '';
  }
});

async function fetchAdvice(type) {
  try {
    let prompt = '';
    const problem = `${props.description}`;
    const curr_code = code.value ? `Context: ${code.value}` : '';
    adviceType.value = type.charAt(0).toUpperCase() + type.slice(1);

    switch (type) {
      case 'general':
        prompt = `Give general advice in less than 50 words on how to tackle this coding problem: ${problem} based on current code: ${curr_code}`;
        break;
      case 'styling':
        prompt = `Provide styling tips in less than 50 words specifically for the following code: ${curr_code}`;
        break;
      case 'optimization':
        prompt = `Suggest optimization strategies in less than 50 words for a coding problem about: ${problem} specifically based on current code: ${curr_code}`;
        break;
    }
    prompt += "\n Try to be specific and concise."

    const response = await chat(prompt, 
                                'gpt-3.5-turbo', //model
                                {  //options
                                  temperature: 0.5, 
                                  max_tokens: 1024, 
                                  top_p: 1,
                                  frequency_penalty: 0,
                                  presence_penalty: 0 
                                });
    advice.value = response || 'No advice available at this time.';
  } catch (error) {
    console.error('Error fetching advice:', error);
    advice.value = 'An error occurred while generating advice.';
  }
}
</script>

<style scoped>
.advice-box {
  margin-top: 1rem;
  text-align: center;
}

.advice-button {
  background-color: #4CAF50;
  color: white;
  padding: 8px 16px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  margin: 0 4px;
  border-radius: 5px;
  transition: background-color 0.3s ease;
}

.advice-button:hover {
  background-color: #45a049;
}

.advice-content {
  border: 1px solid #ccc;
  padding: 1rem;
  margin-top: 1rem;
  border-radius: 5px;
  min-height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

h4 {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

p {
  font-size: 14px;
  margin: 0;
  text-align: center;
}
</style>
