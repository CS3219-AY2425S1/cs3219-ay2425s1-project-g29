export default defineEventHandler(async (event) => {
  const runtimeConfig = useRuntimeConfig(event);
  const endPoint = runtimeConfig.questionService;
  const response = await $fetch(`${endPoint}/questions/categories`, {
    method: "GET",
    headers: {
      Authorization: getHeader(event, "authorization") || "",
    },
  });

  return response;
});
