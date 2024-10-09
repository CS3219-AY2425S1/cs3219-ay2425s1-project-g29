<script setup>

const user = useCurrentUser()
const router = useRouter()

onMounted(() => {
  watch(user, (currentUser, prevUser) => {
    if (prevUser && !currentUser) {
      return router.replace('/users/login')
    }
  })
}

)

</script>

<template>
  <div>
    <Toaster />
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>