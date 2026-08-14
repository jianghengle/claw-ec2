<template>
  <div id="app">
    <my-header />
    <router-view />
    <confirm-modal />

    <footer class="footer mt-6">
      <div class="content has-text-centered">
        <p>
          <strong>Claw EC2</strong> by <a href="https://bee-archi.com">Bee-Archi.com</a>.
          Contact support at <a href="mailto:support@bee-archi.com">support@bee-archi.com</a>
        </p>
      </div>
    </footer>
  </div>
</template>

<script>
import MyHeader from './views/MyHeader.vue'
import ConfirmModal from './components/modals/ConfirmModal.vue'

export default {
  components: {
    MyHeader,
    ConfirmModal
  }
}
</script>

<style>
.button.is-link.my-disabled-button {
  opacity: 0.5;
  background-color: #485fc7;
  border-color: #485fc7;
  box-shadow: none;
}

.my-disbaled-field {
  -webkit-text-fill-color: #7a7a7a;
  opacity: 1; /* required on iOS */
}
</style>
