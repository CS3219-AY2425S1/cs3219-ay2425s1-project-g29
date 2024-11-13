<script setup>
import { useAuthStore } from '~/stores/auth';
import { useToast } from '~/components/ui/toast';

const open = ref(false);  // Control whether the dialog is open
const verifyPhrase = ref("");
const showInvalidCurrentPasswordError = ref(false);
const isDeletingAccount = ref(false);
const isGoogleReauthSuccess = ref(true);  // Having issues with reauthing Google, for now set true

const authStore = useAuthStore();
const { toast } = useToast();
const router = useRouter();

const deleteButtonDisabled = computed(() => {
    let verifyPhraseNotMatch = verifyPhrase.value !== "delete my account";

    return verifyPhraseNotMatch || !isGoogleReauthSuccess.value;
});

const reauthenticateGoogle = async () => {
    try {
        await authStore.reauthenticateWithGoogle();
        console.log("Successfully reauthenticated with Google!");
        isGoogleReauthSuccess.value = true;
    } catch (error) {
        console.log("Error while reauthenticating with Google:", error.message);
    }
}

const handleDeleteAccount = async () => {
    // Ensure that the function doesn't execute if the button is disabled
    if (deleteButtonDisabled.value || isDeletingAccount.value || !isGoogleReauthSuccess.value) {
        return;
    }

    isDeletingAccount.value = true;
    showInvalidCurrentPasswordError.value = false;

    if (verifyPhrase.value !== "delete my account") {
        console.log("Verify Phrase failed to validate")
        return;
    }

    try {
        await authStore.deleteUsingUserService();
        toast({
            description: 'Successfully deleted account.',
        });
        router.replace('/users/login');
    } catch (error) {
        console.log("Error Deleting Account:", error);
        toast({
            description: 'Failed to delete account.',
            variant: 'destructive',
        });
        isDeletingAccount.value = false;
        return;
    }
};

const handleKeyDown = (event) => {
    if (event.key === "Enter") {
        handleDeleteAccount();
        event.preventDefault();  // Prevent default form behaviour like closing the dialog
    }
}

const cancel = () => {
    open.value = false;
    isGoogleReauthSuccess.value = false;
    verifyPhrase.value = '';
};

</script>

<template>
    <Dialog v-model:open="open">
        <DialogTrigger>
            <Button class="bg-red-500 hover:bg-red-600 text-white">Delete My Account</Button>
        </DialogTrigger>
        <DialogContent>
            <DialogHeader>
                <DialogTitle>Are you absolutely sure?</DialogTitle>
                <DialogDescription>
                    This action cannot be undone. This will permanently delete your account.
                </DialogDescription>
            </DialogHeader>
            <div>
                Reauthenticate with Google to continue.
            </div>
            <form @keydown="handleKeyDown" @submit.prevent="handleDeleteAccount" class="space-y-2">
                <div class="grid gap-2">
                    <div>
                        <Label>Verify Google Login</Label>
                        <Button variant="outline" :disabled="isGoogleReauthSuccess" @click="reauthenticateGoogle"
                            class="w-full flex items-center justify-center gap-x-3">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 48 48">
                                <path fill="#fbc02d"
                                    d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12	s5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24s8.955,20,20,20	s20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z">
                                </path>
                                <path fill="#e53935"
                                    d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039	l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z">
                                </path>
                                <path fill="#4caf50"
                                    d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36	c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z">
                                </path>
                                <path fill="#1565c0"
                                    d="M43.611,20.083L43.595,20L42,20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571	c0.001-0.001,0.002-0.001,0.003-0.002l6.19,5.238C36.971,39.205,44,34,44,24C44,22.659,43.862,21.35,43.611,20.083z">
                                </path>
                            </svg>
                            Sign in with Google
                            <svg v-show="isGoogleReauthSuccess" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="green">
                                <path d="M9 16.2l-4.2-4.2-1.4 1.4L9 19 20.6 7.4l-1.4-1.4L9 16.2z" />
                            </svg>
                        </Button>
                    </div>
                    <div>
                        <Label for="verifyPhrase">To verify, type "delete my account" below:</Label>
                        <Input id="verifyPhrase" name="verifyPhrase" v-model="verifyPhrase"
                            placeholder="Enter the Phrase" />
                    </div>
                </div>
                <DialogFooter>
                    <Button @click="cancel" class="bg-gray-200 hover:bg-gray-400 text-gray-700">Cancel</Button>
                    <Button @click="handleDeleteAccount" :disabled="deleteButtonDisabled || isDeletingAccount"
                        type="submit" class="bg-red-500 hover:bg-red-600 text-white">
                        {{ isDeletingAccount ? "Deleting..." : "DELETE MY ACCOUNT" }}
                    </Button>
                </DialogFooter>
            </form>
        </DialogContent>
    </Dialog>
</template>
