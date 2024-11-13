export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const runtimeConfig = useRuntimeConfig(event);
  const matchingService = runtimeConfig.matchingService;
  try {
    const response = await $fetch(`${matchingService}/matching`, {
      method: "POST",
      body: body,
      headers: {
        Authorization: getHeader(event, "authorization") || "",
      },
    });

    return response;
  } catch (error) {
    let errorMessage = "Unknown error occurred";

    if (error && typeof error === "object" && "response" in error) {
      errorMessage = (error as any).response._data.error;
    }
    return {
      error: errorMessage,
    };
  }
});
