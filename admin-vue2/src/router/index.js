import Vue from 'vue'
import VueRouter from 'vue-router'
import MyHome from '../views/MyHome.vue'
import Subscription from '../views/Subscription.vue'

Vue.use(VueRouter)

const router = new VueRouter({
  mode: 'history',
  base: import.meta.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'MyHome',
      component: MyHome
    },
    {
      path: '/subscription/:subscriptionId',
      name: 'Subscription',
      component: Subscription
    },
  ]
})

export default router
