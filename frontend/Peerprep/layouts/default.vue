<template>
    <main class="h-screen w-full flex flex-col overflow-hidden">
        <Navbar v-if="showNavbar" />
        <div class="flex-grow overflow-y-auto">
            <slot />
        </div>
    </main>
</template>

<script setup>
import Navbar from '~/components/navigation/Navbar.vue';
</script>

<script>
export default {
    computed: {
        showNavbar() {
            const hiddenNavbarPaths = ['/users/login', '/users/register'];

            return !hiddenNavbarPaths.includes(this.$route.path);
        }
    }
}
</script>