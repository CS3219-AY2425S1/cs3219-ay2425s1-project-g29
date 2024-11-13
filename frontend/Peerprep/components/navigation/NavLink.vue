<template>
    <NuxtLink :to="to" v-slot="{ isActive, isExactActive, href }" v-bind="$attrs">
        <a :href="href" :class="[
            isExactActive || isActive ? activeClasses : baseClasses
        ]">
            <slot />
        </a>
    </NuxtLink>
</template>

<script setup>
const props = defineProps({
    to: {
        type: [String, Object],
        required: true,
    },
    exact: {
        type: Boolean,
        default: false,
    },
});

const baseClasses = 'text-muted-foreground hover:text-foreground font-medium';
const activeClasses = 'text-foreground font-semibold';
</script>
