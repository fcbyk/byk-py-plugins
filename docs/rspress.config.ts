import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig } from '@rspress/core';
import { pluginLlms } from '@rspress/plugin-llms';
import pluginFileTree from 'rspress-plugin-file-tree';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  root: 'content',
  lang: 'zh',
  title: 'BYK 插件',
  globalStyles: path.join(__dirname, 'styles', 'custom.css'),
  plugins: [pluginLlms(), pluginFileTree()],
  markdown: {
    link: {
      checkDeadLinks: {
        excludes: ['/llms-full.txt', '/basics/'],
      },
    },
  },
  route: {
    cleanUrls: true,
  },
  themeConfig: {
    llmsUI: true,
    editLink: {
      docRepoBaseUrl: 'https://github.com/fcbyk/bykpy/tree/main/docs/content',
    },
    socialLinks: [
      {
        icon: 'github',
        mode: 'link',
        content: 'https://github.com/fcbyk/bykpy',
      },
    ],
  },
});
