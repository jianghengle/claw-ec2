<template>
  <div class="modal" :class="{'is-active': opened}">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">{{title}}</p>
        <button class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body">
        <div>{{message}}</div>
      </section>
      <footer class="modal-card-foot">
        <div class="buttons">
          <a class="button is-danger" @click="confirm">{{button}}</a>
          <a class="button" @click="close">Cancel</a>
        </div>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  name: 'confirm-modal',
  computed: {
    opened () {
      return this.$store.state.modals.confirmModal.opened
    },
    title () {
      return this.$store.state.modals.confirmModal.title
    },
    message () {
      return this.$store.state.modals.confirmModal.message
    },
    button () {
      return this.$store.state.modals.confirmModal.button
    }
  },
  methods: {
    close(){
      this.$store.commit('modals/closeConfirmModal')
    },
    confirm(){
      var callback = this.$store.state.modals.confirmModal.callback
      if(callback){
        var method = callback.method
        var context = callback.context
        var args = callback.args
        method.apply(context, args)
      }
      this.close()
    }
  },
}
</script>
