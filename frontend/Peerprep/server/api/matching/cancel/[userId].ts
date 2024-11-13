export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const runtimeConfig = useRuntimeConfig(event);
  const userId = getRouterParam(event, "userId");
  const matchingService = runtimeConfig.matchingService;
  const response = await $fetch(`${matchingService}/cancel/${userId}`, {
    method: "POST",
    body: body,
    headers: {
      Authorization: getHeader(event, "authorization") || "",
    },
  });

  return response;
});
