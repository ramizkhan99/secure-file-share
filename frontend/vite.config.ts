import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
// import fs from "fs";
// import basicSsl from "@vitejs/plugin-basic-ssl";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // Use for running the server with https independent of nginx
  // server: {
  //   https: {
  //     key: fs.readFileSync(`/app/key.pem`),
  //     cert: fs.readFileSync(`/app/cert.pem`),
  //   },
  // },
});
