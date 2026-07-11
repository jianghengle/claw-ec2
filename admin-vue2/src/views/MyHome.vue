<template>
  <div class="container">
    <section class="section" v-if="!token">
      <h1 class="title is-5">Claw EC2 Console</h1>
      <h2 class="subtitle is-6 mt-2">
        Real cloud server with Openclaw
      </h2>
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
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    token () {
      return this.$store.state.user.token
    },
  },
  watch: {
    token: function (val) {
      
    },
  },
  methods: {
  },
  mounted () {
  },
}
</script>

<style scoped>

</style>
