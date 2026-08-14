<template>
  <div class="modal" :class="{'is-active': opened}">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Set Claude API Key</p>
        <button class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body">
        <div>
          <div class="field">
            <label class="label">API Key</label>
            <div class="control">
              <textarea class="textarea" v-model="newKey"></textarea>
            </div>
            <p class="help is-info">The API key will be set directly on EC2. We NEVER save it anywhere else.</p>
          </div>
        </div>
        <div v-if="error" class="notification is-danger is-light mt-5">
          <button class="delete" @click="error=''"></button>
          {{error}}
        </div>
      </section>
      <footer class="modal-card-foot">
        <div class="buttons">
          <a class="button is-link" :disabled="!newKeyValid" :class="{'is-loading': waiting}" @click="submit">Submit</a>
          <a class="button" @click="close">Cancel</a>
        </div>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  name: 'key-modal',
  props: ['opened', 'subscription'],
  data () {
    return {
      waiting: false,
      error: '',
      newKey: '',
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    token () {
      return this.$store.state.user.token
    },
    newKeyValid () {
      return Boolean(this.newKey.trim())
    },
  },
  methods: {
    close(){
      this.$emit('closeKeyModal')
    },
    submit () {
      if (!this.newKeyValid) {
        return
      }
      this.waiting = true
      var message = {
        subscriptionId: this.subscription.id,
        claudeKey: this.newKey.trim(),
      }
      this.$http.post(this.server + '/set-sub-claude-key', message).then(resp => {
        this.error = ''
        this.waiting = false
        this.$emit('closeKeyModal')
      }, err => {
        this.error = err.body
        this.waiting = false
      })
    },
  },
}
</script>
