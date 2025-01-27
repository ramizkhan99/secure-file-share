import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import fs from "fs";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // Use for running the server with https independent of nginx
  server: {
    https: {
      key: fs.readFileSync(path.resolve(__dirname, `./localhost.key`)),
      cert: fs.readFileSync(path.resolve(__dirname, `./localhost.crt`)),
    },
  },
});
