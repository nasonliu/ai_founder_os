import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import sourceIdentifierPlugin from 'vite-plugin-source-identifier'
import path from "path"

const isProd = process.env.BUILD_MODE === 'prod'

export default defineConfig({
  plugins: [
    react(),
    sourceIdentifierPlugin({
      enabled: !isProd,
      attributePrefix: 'data-matrix',
      includeProps: true,
    })
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
