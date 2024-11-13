<script setup>
import { useAuthStore } from '~/stores/auth';
import { useToast } from '~/components/ui/toast';

const open = ref(false);  // Control whether the dialog is open
const verifyPass = ref("");
const verifyPhrase = ref("");
const showInvalidCurrentPasswordError = ref(false);
const isDeletingAccount = ref(false);

const authStore = useAuthStore();
const { toast } = useToast();
const router = useRouter();

const deleteButtonDisabled = computed(() => {
    let verifyPassNotEmpty = verifyPass.value == "";
    let verifyPhraseNotMatch = verifyPhrase.value !== "delete my account";

    return verifyPassNotEmpty || verifyPhraseNotMatch;
});


const handleDeleteAccount = async () => {
    // Ensure that the function doesn't execute if the button is disabled
    if (deleteButtonDisabled.value || isDeletingAccount.value) {
        return;
    }

    isDeletingAccount.value = true;
    showInvalidCurrentPasswordError.value = false;

    if (verifyPhrase.value !== "delete my account") {
        console.log("Verify Phrase failed to validate")
        return;
    }

    // Reauthenticate User (check if current password is correct)
    try {
        await authStore.reauthenticateWithPassword(verifyPass.value);
    } catch (error) {
        let errorCode = error.code;
        if (errorCode === "auth/invalid-credential") {
            console.log("Verify Password Incorrect")
            showInvalidCurrentPasswordError.value = true;
        } else {
            console.log("Error Reauthenticating User", error);
        }
        toast({
            description: 'Failed to verify current password.',
            variant: 'destructive',
        });
        isDeletingAccount.value = false;
        return;
    }

    try {
        await authStore.deleteAccountAndSignOut();
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
    verifyPass.value = '';
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
                Enter your current password to confirm.
            </div>
            <form @keydown="handleKeyDown" @submit.prevent="handleDeleteAccount" class="space-y-2">
                <div class="grid gap-2">
                    <div>
                        <Label for="verifyPass">Confirm Your Password</Label>
                        <Input id="verifyPass" name="verifyPass" v-model="verifyPass" type="password"
                            placeholder="Enter Current Password" />
                        <p v-if="showInvalidCurrentPasswordError" class="text-red-500 text-sm">Current password is
                            incorrect.
                        </p>
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
