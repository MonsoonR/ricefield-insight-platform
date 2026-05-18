import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, URL } from 'node:url';

import vue from '@vitejs/plugin-vue';
import { defineConfig, type Plugin } from 'vite';

const cesiumBuildPath = fileURLToPath(new URL('./node_modules/cesium/Build/Cesium', import.meta.url));
const cesiumPublicPath = '/cesium/';

export default defineConfig({
  define: {
    CESIUM_BASE_URL: JSON.stringify(cesiumPublicPath),
  },
  plugins: [vue(), cesiumAssetsPlugin()],
  build: {
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-antd': ['ant-design-vue'],
        },
      },
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
});

function cesiumAssetsPlugin(): Plugin {
  return {
    name: 'ricefield-cesium-assets',
    configureServer(server) {
      server.middlewares.use('/cesium', (request, response, next) => {
        const requestUrl = new URL(request.url ?? '/', 'http://cesium.local');
        const requestPath = decodeURIComponent(requestUrl.pathname);
        const filePath = path.resolve(cesiumBuildPath, `.${requestPath}`);

        if (!filePath.startsWith(cesiumBuildPath)) {
          next();
          return;
        }

        fs.stat(filePath, (statError, stat) => {
          if (statError || !stat.isFile()) {
            next();
            return;
          }

          response.setHeader('Content-Type', contentType(filePath));
          fs.createReadStream(filePath).pipe(response);
        });
      });
    },
    generateBundle() {
      for (const directory of ['Assets', 'ThirdParty', 'Widgets', 'Workers']) {
        emitCesiumDirectory(
          this,
          path.join(cesiumBuildPath, directory),
          path.posix.join('cesium', directory),
        );
      }
    },
  };
}

function emitCesiumDirectory(plugin: PluginContextLike, sourceDir: string, outputDir: string) {
  for (const item of fs.readdirSync(sourceDir, { withFileTypes: true })) {
    const sourcePath = path.join(sourceDir, item.name);
    const outputPath = path.posix.join(outputDir, item.name);

    if (item.isDirectory()) {
      emitCesiumDirectory(plugin, sourcePath, outputPath);
      continue;
    }

    plugin.emitFile({
      type: 'asset',
      fileName: outputPath,
      source: fs.readFileSync(sourcePath),
    });
  }
}

interface PluginContextLike {
  emitFile(file: {
    type: 'asset';
    fileName: string;
    source: Buffer;
  }): string;
}

function contentType(filePath: string) {
  const extension = path.extname(filePath).toLowerCase();
  const types: Record<string, string> = {
    '.css': 'text/css',
    '.gif': 'image/gif',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.js': 'text/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.svg': 'image/svg+xml',
    '.wasm': 'application/wasm',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
  };

  return types[extension] ?? 'application/octet-stream';
}
