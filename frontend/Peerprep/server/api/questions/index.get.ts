export default defineEventHandler(async (event) => {
  const runtimeConfig = useRuntimeConfig(event);
  const endPoint = runtimeConfig.questionService;
  const response = await $fetch(`${endPoint}/questions`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: getHeader(event, "authorization") || "",
    },
  });

  return response;
});
