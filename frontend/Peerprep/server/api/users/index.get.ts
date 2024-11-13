export default defineEventHandler(async (event) => {
  const runtimeConfig = useRuntimeConfig(event);
  const endPoint = runtimeConfig.userService;
  const response = await $fetch(`${endPoint}/users`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: getHeader(event, "authorization") || "",
    },
  });

  return response;
});
