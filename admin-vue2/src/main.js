import Vue from 'vue'

import App from './App.vue'
import router from './router'
import store from './store'

import 'bulma/css/bulma.css'

import VueResource from 'vue-resource'
Vue.use(VueResource)

new Vue({
  router,
  store,
  render: (h) => h(App)
}).$mount('#app')
