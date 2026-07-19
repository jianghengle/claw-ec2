<template>
  <div class="container">
    <section class="section" v-if="!token">
      <h1 class="title is-5">Claw EC2 Console</h1>
      <h2 class="subtitle is-6 mt-2">
        Real cloud server with Openclaw
      </h2>

      <div class="field">
        <label class="label">Email</label>
        <div class="control has-icons-left has-icons-right">
          <input class="input" type="email" placeholder="Email" v-model="email">
          <span class="icon is-small is-left">
            <i class="fas fa-envelope"></i>
          </span>
        </div>
      </div>

      <div class="field is-grouped">
        <div class="control">
          <button class="button is-link" :class="{'is-loading': sending}" :disabled="!emailValid" @click="sendLink">Send secure login link to my email</button>
        </div>
      </div>

      <div v-if="error" class="notification is-danger is-light">
        <button class="delete" @click="error=''"></button>
        {{error}}
      </div>

      <div v-if="sent" class="notification is-success is-light">
        The login link has been sent to your email. Please login from there.
      </div>
    </section>
    <div v-if="token">
      

    </div>
  </div>
</template>

<script>
export default {
  name: 'my-home',
  components: {
  },
  data () {
    return {
      error: '',
      waiting: false,
      email: '',
      sending: false,
      sent: false,
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    token () {
      return this.$store.state.user.token
    },
    emailValid () {
      var re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
      return re.test(this.email.trim().toLowerCase())
    },
  },
  watch: {
    token: function (val) {
      
    },
  },
  methods: {
    sendLink () {
      var message = {
        email: this.email.trim().toLowerCase(),
        origin: window.location.origin
      }
      this.sending = true
      this.$http.post(this.server + '/send-login-link', message).then(resp => {
        console.log(resp)
        this.sent = true
      }).catch(err => {
        console.log(err)
        this.error = err.body
      }).finally(() => {
        this.sending = false
      })
    },
  },
  mounted () {
  },
}
</script>

<style scoped>

</style>
