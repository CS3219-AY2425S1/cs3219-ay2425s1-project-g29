<script setup>
    definePageMeta({
        requiresAuth: false,
    });
</script>

<template>
    <div class="unauthorized-page">
        <h1>401 - Unauthorized</h1>
        <p>You do not have permission to access this page.</p>
        <nuxt-link to="/">Go back to Home</nuxt-link>
    </div>
</template>