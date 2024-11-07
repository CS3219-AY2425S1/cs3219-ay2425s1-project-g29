# Peerprep Frontend

This uses [Nuxt 3](https://nuxt.com/) as the framework for the frontend.  

## Setup
Make sure to have the following installed:
- [NodeJs](https://nodejs.org/en)
- Recommended way is to use [nvm](https://github.com/nvm-sh/nvm) or [nvm-windows](https://github.com/coreybutler/nvm-windows)


Make sure to install the dependencies:
```bash
# npm
npm install
```

## Env Variables

- Set up environment varaibles in a `.env` file
  - `FIREBASE_API_KEY` which you can get from the firebase console.
  - `HOST_ADDRESS` = localhost or the static ip (for deployment).
  - `LB_API_KEY` which you can get from the liveblocks dashboard
  - `OPENAI_API_KEY` which you can get from openai [api-keys page](https://platform.openai.com/api-keys)

## Development Server

Start the development server on `http://localhost:3000`:

```bash
# npm
npm run dev -- -o
```

## Production Build

1. Make sure you are in `frontend/Peerprep` directory.
2. Follow the steps in the env variables section above.
3. Run `docker build -t peerprep .`
4. Run `docker run --rm -it -p 3000:3000 --env-file .env --name peerprep peerprep`
