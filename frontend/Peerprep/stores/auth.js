import { defineStore } from "pinia";
import { EmailAuthProvider, reauthenticateWithCredential, signOut, onAuthStateChanged, updateProfile, updatePassword } from "firebase/auth";

export const useAuthStore = defineStore('auth', () => {
    const auth = useFirebaseAuth();
    const user = ref(null);
    const isAdmin = ref(false);  // Assume User is not admin by default
    const isGoogleLogin = ref(false);

    async function refreshUser() {
        const currentUser = await getCurrentUser();

        if (currentUser) {
            user.value = currentUser;

            // Check If Admin
            const tokenResult = await currentUser.getIdTokenResult();
            const adminResult = tokenResult.claims.admin === true;
            isAdmin.value = adminResult;

            // Check If Login with Google
            const googleProvider = user.value?.providerData[0].providerId === 'google.com';
            isGoogleLogin.value = googleProvider;
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

    async function updateDisplayName(newDisplayName) {
        refreshUser();

        if (user.value) {
            try {
                await updateProfile(user.value, {
                    displayName: newDisplayName
                });
                return true;
            } catch (error) {
                console.error("Error updating profile:", error);
                return false;
            }
        } else {
            console.log('No user is logged in');
            return false;
        }
    }

    async function reauthenticateWithPassword(password) {
        // Sanity check to make sure Account is not signed in with Google
        if (isGoogleLogin.value === true) {
            console.log('Cannot re-authenticate with Google account using password');
            return false;
        }

        try {
            await refreshUser();
            if (user.value && password) {
                const credential = EmailAuthProvider.credential(
                    user.value.email,
                    password
                );

                await reauthenticateWithCredential(user.value, credential);
                console.log("User reauthenticated successfully");
            }
        } catch (error) {
            console.error("Error reauthenticating user in store:", error.message);
            throw error;
        }
    }

    async function changePassword(newPassword) {
        // Sanity check to make sure Account is not signed in with Google
        if (isGoogleLogin.value === true) {
            console.log('Cannot change password with account signed in with Google');
            return false;
        }

        try {
            if (user.value && newPassword) {
                await updatePassword(user.value, newPassword);
                console.log("Password change successful");
            }
        } catch (error) {
            console.error("Error updating password in store:", error.message);
            throw(error);
        }
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
        isGoogleLogin,
        authSignOut,
        changePassword,
        updateDisplayName,
        reauthenticateWithPassword,
        refreshUser
    };
})
