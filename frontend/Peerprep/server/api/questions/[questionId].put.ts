export default defineEventHandler(async (event) => {
  const questionId = getRouterParam(event, "questionId");
  const body = await readBody(event);
  const runtimeConfig = useRuntimeConfig(event);
  const endPoint = runtimeConfig.questionService;
  const response = await $fetch(`${endPoint}/questions/${questionId}`, {
    method: "PUT",
    body: body,
    headers: {
      "Content-Type": "application/json",
      Authorization: getHeader(event, "authorization") || "",
    },
  });

  return response;
});
