import { defineStore } from "pinia";
import { signOut, onAuthStateChanged } from "firebase/auth";

export const useAuthStore = defineStore('auth', () => {
    const auth = useFirebaseAuth();
    const user = ref(null);
    const isAdmin = ref(false);  // Assume User is not admin by default

    async function refreshUser() {
        const currentUser = await getCurrentUser();

        if (currentUser) {
            user.value = currentUser;

            // Check If Admin
            const tokenResult = await currentUser.getIdTokenResult();
            const adminResult = tokenResult.claims.admin === true;
            isAdmin.value = adminResult;
        } else {
            user.value = null;
            isAdmin.value = false;
        }
    }

    // Handle sign out
    async function authSignOut() {
        await signOut(auth);
        user.value = null;
        isAdmin.value = false;
    }

    // Update user when auth changes
    onAuthStateChanged(auth, async (currentUser) => {
        if (currentUser) {
            await refreshUser();
        }
    })

    return {
        user,
        isAdmin,
        refreshUser,
        authSignOut
    };
})
