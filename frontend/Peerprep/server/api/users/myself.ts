export default defineEventHandler(async (event) => {
  const runtimeConfig = useRuntimeConfig(event);
  const endPoint = runtimeConfig.userService;
  const response = await $fetch(`${endPoint}/users/myself`, {
    method: "DELETE",
    headers: {
      Authorization: getHeader(event, "authorization") || "",
    },
  });

  return response;
});
