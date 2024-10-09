<script setup>
import {
  signInWithPopup,
  GoogleAuthProvider,
  signInWithEmailAndPassword,
} from "firebase/auth";
import { useAuthStore } from '~/stores/auth';

definePageMeta({
  requiresAuth: false,
})

const authStore = useAuthStore();
const auth = useFirebaseAuth();
const router = useRouter();

function signInWithFirebase() {
  signInWithPopup(auth, new GoogleAuthProvider())
  .then(() => {
    authStore.refreshUser();
    router.replace("/");
  })
  .catch((error) => {
    console.error("Sign-in failed", error);
  });
}

const email = ref("");
const password = ref("");
const isLoggingIn = ref(false);
const firebaseErrorMessage = ref("");

const handleSubmit = () => {
  isLoggingIn.value = true;
  firebaseErrorMessage.value = "";
  login()
    .then(() => {
      authStore.refreshUser();
      router.replace("/");
    })
    .catch(handleFirebaseLoginErrors)
    .finally(() => {
      isLoggingIn.value = false;
    });
};

const login = async () => {
  await signInWithEmailAndPassword(auth, email.value, password.value);
};

const handleFirebaseLoginErrors = (error) => {
  var errorCode = error.code;
  if (
    errorCode == "auth/invalid-email" ||
    errorCode == "auth/user-not-found" ||
    errorCode == "auth/wrong-password" ||
    errorCode == "auth/invalid-credential"
  ) {
    firebaseErrorMessage.value = "Incorrect email or password.";
  } else {
    firebaseErrorMessage.value = "Login error. Contact administrator.";
  }
}
</script>

<template>
  <div class="min-h-full w-full flex items-center justify-center">
    <Card class="w-[380px]">
      <CardHeader>
        <div class="flex justify-center">
          <img src="@/assets/PeerPrep.png" alt="Logo" class="w-24" />
        </div>
      </CardHeader>
      <CardContent class="space-y-5">
        <form @submit.prevent="handleSubmit" class="space-y-5">
          <div class="grid gap-2">
            <Label for="email">Email</Label>
            <Input
              id="email"
              name="email"
              v-model="email"
              type="email"
              placeholder="m@example.com"
              required
              autocomplete="email"
            />
          </div>
          <div class="grid gap-2">
            <div class="flex items-center">
              <Label for="password">Password</Label>
              <NuxtLink to="#" class="ml-auto inline-block text-sm underline">
                Forgot your password?
              </NuxtLink>
            </div>
            <Input
              id="password"
              name="password"
              v-model="password"
              type="password"
              required
              autocomplete="current-password"
            />
          </div>
          <!-- Error Message -->
          <p v-if="firebaseErrorMessage" class="text-red-500">
            {{ firebaseErrorMessage }}
          </p>
          <Button type="submit" class="w-full" :disabled="isLoggingIn">
            {{ isLoggingIn ? "Logging In..." : "Login" }}
          </Button>
        </form>
        <Button
          variant="outline"
          @click="signInWithFirebase"
          class="w-full flex items-center justify-center gap-x-5"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 48 48"
          >
            <path
              fill="#fbc02d"
              d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12	s5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24s8.955,20,20,20	s20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"
            ></path>
            <path
              fill="#e53935"
              d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039	l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"
            ></path>
            <path
              fill="#4caf50"
              d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36	c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"
            ></path>
            <path
              fill="#1565c0"
              d="M43.611,20.083L43.595,20L42,20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571	c0.001-0.001,0.002-0.001,0.003-0.002l6.19,5.238C36.971,39.205,44,34,44,24C44,22.659,43.862,21.35,43.611,20.083z"
            ></path>
          </svg>
          Sign in with Google
        </Button>
        <div class="mt-4 text-center text-sm">
          Don't have an account?
          <NuxtLink to="/users/register" class="underline"> Sign up </NuxtLink>
        </div>
      </CardContent>
    </Card>
  </div>
</template>
