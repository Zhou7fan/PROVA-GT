export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.directive('b-tooltip', {
    getSSRProps() {
      return {}
    },
    mounted() {},
    updated() {},
  })
})
