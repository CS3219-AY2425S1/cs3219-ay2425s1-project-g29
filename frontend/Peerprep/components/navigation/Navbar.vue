<script setup>
import { useAuthStore } from '~/stores/auth';
import NavLink from '~/components/navigation/NavLink.vue';

const authStore = useAuthStore();
const { user, isAdmin } = storeToRefs(authStore);

function handleSignOut() {
    authStore.authSignOut();
};

watch(user, (newUser) => {  // TODO: Check if can remove this
    if (newUser) {
        authStore.refreshUser();
    }
});
</script>

<template>
    <nav class="bg-muted/70 shadow-sm border-b border-border">
        <div class="w-full mx-auto flex items-center justify-between py-2 px-3">
            <div class="flex items-center space-x-8">
                <img src="@/assets/PeerPrep.png" alt="Logo" class="w-[52px]" />
                <div class="flex items-center space-x-6">
                    <NavLink to="/" exact>Home</NavLink>
                    <NavLink to="/questions">Questions</NavLink>
                    <NavLink to="/collaboration">Collaboration</NavLink>
                </div>
            </div>

            <div class="flex items-center space-x-4">
                <template v-if="isAdmin">
                    <NavLink to="/admin">Admin</NavLink>
                </template>
                <DropdownMenu>
                    <DropdownMenuTrigger as-child>
                        <Avatar size="xs"
                            class="hover:shadow-xl hover:bg-gray-300  transition-all duration-300 cursor-pointer">
                            <AvatarImage :src="user.photoURL" alt="User Avatar" />
                            <AvatarFallback>CN</AvatarFallback>
                        </Avatar>

                    </DropdownMenuTrigger>
                    <DropdownMenuContent class="w-fit" align="end">
                        <DropdownMenuItem>
                            <NuxtLink to="/users/settings">Settings</NuxtLink>
                        </DropdownMenuItem>
                        <DropdownMenuItem @click="handleSignOut">Sign out</DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </div>
    </nav>
</template>
