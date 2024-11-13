export default defineEventHandler(async (event) => {
  const userId = getRouterParam(event, "userId");
  const runtimeConfig = useRuntimeConfig(event);
  const endPoint = runtimeConfig.userService;
  const response = await $fetch(`${endPoint}/admin/users/${userId}/is_admin`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: getHeader(event, "authorization") || "",
    },
  });

  return response;
});
