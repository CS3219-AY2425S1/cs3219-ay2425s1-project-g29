export default defineEventHandler(async (event) => {
  const questionId = getRouterParam(event, "questionId");
  const runtimeConfig = useRuntimeConfig(event);
  const endPoint = runtimeConfig.questionService;
  const response = await $fetch(`${endPoint}/questions/${questionId}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: getHeader(event, "authorization") || "",
    },
  });

  return response;
});
