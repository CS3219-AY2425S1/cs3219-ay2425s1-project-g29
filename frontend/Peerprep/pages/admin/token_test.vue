<script setup>
import { ref } from 'vue';

definePageMeta({
    requiresAuth: true,
    requiresAdmin: true,
})

const token = ref('');
var actualToken = "";
const isAdmin = ref('');
const user = await getCurrentUser();
const userDetails = ref('');
const userServiceResponse = ref('')

const getUserToken = async () => {
    const tokenResult = await user.getIdTokenResult();
    token.value = tokenResult;
    actualToken = tokenResult.token;
    isAdmin.value = tokenResult.claims.admin || "false";
    userDetails.value = user;
};

const sendTokenToUserService = async () => {
    const response = await fetch('http://localhost:5001/auth/verify_token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${actualToken}`,
        }
    });
    const result = await response.json();
    userServiceResponse.value = result;
}

</script>


<template>
    <div>
        <Button @click="getUserToken">Get User Token</Button>
        <p v-if="token" class="text-red-500">{{ token }}</p>
        <p v-if="isAdmin">isAdmin: {{ isAdmin }}</p>
        <p v-if="userDetails">userDetails: {{ userDetails }}</p>
    </div>
    <div>
        <Button v-if="token" @click="sendTokenToUserService">Test Token with User Service</Button>
        <p v-if="userServiceResponse">Response: {{ userServiceResponse }}</p>
    </div>
</template>