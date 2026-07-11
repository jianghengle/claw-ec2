<template>
  <div>
    <nav class="navbar has-shadow" role="navigation" aria-label="main navigation">
      <div class="container p-3">
        <div class="navbar-brand">
          <router-link class="navbar-item is-size-4 has-text-weight-bold" :to="'/'">
            Claw EC2
          </router-link>
          

          <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false"
            :class="{'is-active': menuActive}" @click="menuActive = !menuActive">
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
          </a>
        </div>

        <div id="navbarBasicExample" class="navbar-menu"  :class="{'is-active': menuActive}">
          <div class="navbar-start">
          </div>

          <div class="navbar-end">
            <a class="navbar-item" v-if="token" @click="signout">
              <span class="icon">
                <i class="fas fa-sign-out-alt"></i>
              </span>
              <span>Sign out</span>
            </a>
          </div>
        </div>
      </div>
    </nav>
  </div>
</template>

<script>
import Vue from 'vue'

export default {
  name: 'my-header',
  data () {
    return {
      menuActive: false
    }
  },
  computed: {
    token () {
      return this.$store.state.user.token
    },
    routerPath () {
      return this.$route.path
    },
    server () {
      return this.$store.state.config.server
    },
    myUsername () {
      return this.$store.state.user.username
    },
  },
  methods: {
    signout () {
      this.$store.commit('user/reset')
    },
    getUsers () {
      var message = {
        username: this.myUsername,
        token: this.token,
      }
      this.$http.post(this.server + '/myapp/get-org-users/', message).then(resp => {
        this.$store.commit('org/setUsersMap', resp.body)
      }, err => {
        this.error = err.body
        this.$store.commit('user/reset')
        this.$store.commit('org/reset')
        if (this.routerPath != '/') {
          this.$router.push('/')
        }
      })
    },
  },
  mounted () {
    if (this.token) {
      this.getUsers()
    }
  }
}
</script>
