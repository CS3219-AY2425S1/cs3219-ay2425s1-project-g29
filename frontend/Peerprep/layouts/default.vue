<template>
    <main class="h-screen w-full flex flex-col overflow-hidden">
        <div class="flex-grow overflow-y-auto">
            <slot />
        </div>
    </main>
</template>

<script setup>
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