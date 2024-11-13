export default defineEventHandler(async (event) => {
    const userId = getRouterParam(event, "userId");
    const attemptId = getRouterParam(event, "attemptId");
    const runtimeConfig = useRuntimeConfig(event);
    const endPoint = runtimeConfig.userService;
    const response = await $fetch(`${endPoint}/users/${userId}/history/${attemptId}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: getHeader(event, "authorization") || "",
      },
    });
  
    return response;
  });
