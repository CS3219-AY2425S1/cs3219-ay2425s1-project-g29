<script setup>
import { ref } from 'vue';

definePageMeta({
    requiresAuth: true,
    requiresAdmin: true,
})

const token = ref('');
const isAdmin = ref('');
const user = await getCurrentUser();
const userDetails = ref('');

const getUserToken = async () => {
    const tokenResult = await user.getIdTokenResult();
    token.value = tokenResult
    isAdmin.value = tokenResult.claims.admin || "false"
    userDetails.value = user;
};

</script>


<template>
    <div>
        <Button @click="getUserToken">Get User Token</Button>
        <p v-if="token" class="text-red-500">{{ token }}</p>
        <p v-if="isAdmin">isAdmin: {{ isAdmin }}</p>
        <p v-if="userDetails">userDetails: {{ userDetails }}</p>
    </div>
</template>