export default defineEventHandler(async (event) => {
  const runtimeConfig = useRuntimeConfig(event);
  const endPoint = runtimeConfig.userService;
  const response = await $fetch(`${endPoint}/auth/verify_token`, {
    method: "POST",
    headers: {
      "Content-Type": getHeader(event, "Content-Type") || "",
      "Authorization": getHeader(event, "Authorization") || "",
    },
  });

  return response;
});
