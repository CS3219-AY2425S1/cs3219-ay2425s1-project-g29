export default defineNuxtConfig({
  nitro: {
    experimental: {
      websocket: true,
    },
  },
  compatibilityDate: "2024-04-03",
  devtools: { enabled: true },
  ssr: false,
  modules: ["nuxt-vuefire", "@nuxtjs/tailwindcss", "shadcn-nuxt", "@pinia/nuxt"],
  runtimeConfig: {
    public: {
      matchingRequestUrl: "http://localhost:8000",
      webSocketUrl: "ws://localhost:8010",
      FIREBASE_API_KEY: process.env.FIREBASE_API_KEY,
      FIREBASE_AUTH_DOMAIN: process.env.FIREBASE_AUTH_DOMAIN,
      FIREBASE_PROJECT_ID: process.env.FIREBASE_PROJECT_ID,
      FIREBASE_STORAGE_BUCKET: process.env.FIREBASE_STORAGE_BUCKET,
      FIREBASE_MESSAGING_SENDER_ID: process.env.FIREBASE_MESSAGING_SENDER_ID,
      FIREBASE_APP_ID: process.env.FIREBASE_APP_ID,
    },
  },
  shadcn: {
    /**
     * Prefix for all the imported components
     */
    prefix: "",
    /**
     * Directory where the components live.
     * @default "./components/ui"
     */
    componentDir: "./components/ui",
  },
  
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
  router: {
    middleware: ['collaboration'],
  },
});
