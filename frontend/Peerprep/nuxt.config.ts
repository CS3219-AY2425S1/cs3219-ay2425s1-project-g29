// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  nitro: {
    experimental: {
      websocket: true,
    },
  },
  compatibilityDate: "2024-04-03",
  devtools: { enabled: true },
  ssr: false,
  modules: [
    "nuxt-vuefire",
    "@nuxtjs/tailwindcss",
    "shadcn-nuxt",
    "@pinia/nuxt",
  ],
  runtimeConfig: {
    public: {
      matchingRequestUrl: "http://localhost:8000",
      webSocketUrl: "ws://localhost:8010",
    },
  },
  shadcn: {
    /**
     * Prefix for all the imported component
     */
    prefix: "",
    /**
     * Directory that the component lives in.
     * @default "./components/ui"
     */
    componentDir: "./components/ui",
  },
  // app: {
  //   head: {
  //     htmlAttrs: {
  //       'data-bs-theme': 'dark'
  //     },
  //     link: [
  //       { rel: 'stylesheet', href: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css'}
  //     ],
  //     script: [
  //       { src: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js'}
  //     ],
  //   }
  // },
  vuefire: {
    auth: {
      enabled: true,
      sessionCookies: false,
    },
    config: {
      apiKey: process.env.FIREBASE_API_KEY,
      authDomain: "peerprep-g29.firebaseapp.com",
      projectId: "peerprep-g29",
      storageBucket: "peerprep-g29.appspot.com",
      messagingSenderId: "1075086955666",
      appId: "1:1075086955666:web:8929f9277a3a982847c24b",
    },
  },
});
