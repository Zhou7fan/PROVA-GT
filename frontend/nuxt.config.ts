import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
import path from 'path'



export default defineNuxtConfig({
  
  devtools: { enabled: false },

  
  modules: [
    '@nuxt/ui',
    [
      '@pinia/nuxt',
      {
        autoImports: [
          
          'defineStore',
          
          ['defineStore', 'definePiniaStore'],
        ],
      },
    ],
  ],

  
  colorMode: {
    preference: 'light',
  },

  vite: {
    plugins: [
        createSvgIconsPlugin({
            iconDirs: [path.resolve(process.cwd(), 'assets/svg')]
        })
    ],
},

  compatibilityDate: '2025-01-25'
})