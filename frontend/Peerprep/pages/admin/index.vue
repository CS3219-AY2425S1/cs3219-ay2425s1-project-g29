<script setup lang="ts">
import { ref } from 'vue';
import type { User } from '~/types/User'
import UserTable from '@/components/user_list/UserTable.vue';

definePageMeta({
    requiresAuth: true,
    requiresAdmin: true,
})

const users = ref<User[]>([])
const isLoading = ref(true);
const error = ref<string | null>(null);

const checkIfUidAdmin = async (uid: string) => {
    const { data, error } = await useFetch<boolean>(`http://localhost:5001/admin/users/${uid}/is_admin`)

    if (error.value) {  // If there is an error in the fetch
        throw new Error(error.value.message);
    }

    if (data.value !== undefined) {
        return data.value;
    }

    throw new Error("Received undefined value from User Service")
}

const fetchUsers = async () => {
    try {
        isLoading.value = true;
        error.value = null;

        // Get a list of users
        const { data, error: fetchError } = await useFetch('http://localhost:5001/users')

        if (fetchError.value) {
            throw new Error(fetchError.value.message);
        }

        if (data.value && data.value.users) {
            const listOfUsers = data.value.users;

            // Map through each user and add the admin status
            const usersWithAdminStatus = await Promise.all(
                listOfUsers.map(async (user) => {
                    const isAdmin = await checkIfUidAdmin(user.uid ?? '');
                    return {
                        displayName: user.display_name,
                        email: user.email,
                        uid: user.uid,
                        admin: isAdmin,
                    };
                })
            )

            users.value = usersWithAdminStatus;
        }
    } catch (e) {
        console.error("Error while fetching users:", e);
        error.value = e instanceof Error ? e.message : "An unknown error occurred";
    } finally {
        isLoading.value = false;
    }
};

onMounted(() => {
    fetchUsers();
})

</script>

<template>
    <div class="container py-10">
        <div v-if="isLoading">Loading...</div>
        <div v-else-if="error">An error occurred: {{ error }}</div>
        <UserTable
            v-else
            :data="users"
            :key="users.length"
        />
        <div class="flex flex-col items-center py-10">
            <router-link to="/admin/token_test">
                <Button>Admin Token Test Page</Button>
            </router-link>
        </div>

    </div>
</template>
