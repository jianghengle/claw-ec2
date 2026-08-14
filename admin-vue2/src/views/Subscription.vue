<template>
  <div class="container">
    <div v-if="token" class="p-3">
      <nav class="breadcrumb" aria-label="breadcrumbs">
        <ul>
          <li>
            <router-link :to="'/'" aria-current="page">Subscriptions</router-link>
          </li>
          <li class="is-active">
            <a href="#" aria-current="page">{{ this.subscription ? this.subscription.name :  this.subscriptionId }}</a>
          </li>
        </ul>
      </nav>

      <div class="mt-5">
        <div v-if="waiting">
          <span class="icon is-medium is-size-4">
            <i class="fas fa-spinner fa-pulse"></i>
          </span>
        </div>

        <div v-if="error" class="notification is-danger is-light">
          <button class="delete" @click="error=''"></button>
          {{error}}
        </div>

        <div v-if="!waiting && subscription">
          <div class="mb-6">
            <h5 class="title is-5">Subscription info</h5>

            <div class="field">
              <label class="label">Name</label>
              <div class="control">
                <div class="field has-addons">
                  <div class="control">
                    <input class="input" type="text" v-model="newName">
                  </div>
                  <div class="control">
                    <button class="button" :class="{'is-loading': updating}" :disabled="!newNameValid" @click="updateName">
                      <span class="icon is-small">
                        <i class="fas fa-share"></i>
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="field">
              <label class="label">Status</label>
              <div class="control">
                <span class="tag is-medium" :class="{'is-success': subscription.status == 'Active'}">
                  {{ subscription.status }}
                </span>
              </div>
            </div>

            <div class="field">
              <label class="label">Period</label>
              <div class="control">
                <input class="input is-static" type="text" :value="subscription.periodLabel" readonly />
              </div>
            </div>

          </div>

          <hr />

          <div class="mb-6">
            <h5 class="title is-5">EC2 instance</h5>

            <div class="field">
              <label class="label">Status</label>
              <div class="control">
                <span class="tag is-medium" :class="{'is-success': instance && (instance.status == 'Active')}">
                  {{ instance ? instance.status : 'None' }}
                </span>
                <span class="icon status-spinner" v-if="refreshing">
                  <i class="fas fa-spinner fa-pulse"></i>
                </span>
              </div>
              <p class="help is-info" v-if="instance && (instance.status == 'Creating' || instance.status == 'Initializing')">
                It might take up to 10 minutes to launch EC2 ...
              </p>
            </div>

            <div class="field" v-if="!instance && subscription.status == 'Active' && !subscription.instanceId">
              <label class="label">EC2</label>
              <div class="control">
                <button class="button is-link" :class="{'is-loading': launching}" @click="launchEc2">
                  Launch EC2
                </button>
              </div>
            </div>

            <div class="field" v-if="instance && instance.status == 'Active'">
              <label class="label">Claw</label>
              <div class="control">
                <a class="button" target="_blank" :href="'https://' + instance.domain + ':' + instance.clawPort + '/?token=' + instance.clawToken">
                  <span>Secure Claw URL</span>
                  <span class="icon is-small">
                    <i class="fas fa-external-link-alt"></i>
                  </span>
                </a>
              </div>
            </div>

            <div class="field" v-if="instance && instance.status == 'Active'">
              <label class="label">Claude API Key</label>
              <div class="control">
                <button class="button" @click="openKeyModal">
                  <span>Set</span>
                  <span class="icon is-small">
                    <i class="fas fa-key"></i>
                  </span>
                </button>
              </div>
            </div>

            <article class="message is-info mt-5">
              <div class="message-body">
                Contact <a href="mailto:support@bee-archi.com">support@bee-archi.com</a> for more info or operations like public DNS, opening ports etc.
              </div>
            </article>

          </div>

          <hr />

          <div>
            <h5 class="title is-5">Payments</h5>

            <form :action="server + '/stripe/create-checkout-session'" method="POST">
              <input type="hidden" name="subscriptionId" :value="subscription.id">
              <input type="hidden" name="token" :value="token">
              <div class="field">
                <label class="label">Add months</label>
                <div class="control">
                  <div class="field has-addons">
                    <p class="control">
                      <span class="select">
                        <select name="months" v-model="months">
                          <option :value="1">1 month</option>
                          <option :value="2">2 month</option>
                          <option :value="3">3 month</option>
                        </select>
                      </span>
                    </p>
                    <p class="control">
                      <a class="button is-static">
                        {{ priceLabel }}
                      </a>
                    </p>
                    <p class="control">
                      <button class="button is-link" type="submit">
                        Pay
                      </button>
                    </p>
                  </div>
                </div>
              </div>
            </form>

            <div class="mt-5" v-if="payments">
              <label class="label">Payments history</label>
              <div class="control">
                <table class="table is-hoverable is-striped">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th class="has-text-centered">Date</th>
                      <th class="has-text-right">Paid amount</th>
                      <th class="has-text-right">Months</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(payment, index) in payments" :key="'p-' + index">
                      <td>{{ index + 1 }}</td>
                      <td class="has-text-centered">{{ new Date(payment.updatedAt * 1000).toLocaleDateString('en-US') }}</td>
                      <td class="has-text-right">{{ '$' + payment.paymentAmount.toFixed(2) }}</td>
                      <td class="has-text-right">{{ payment.months }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

          </div>
          
        </div>
      </div>

      <key-modal :opened="keyModal.opened" :subscription="subscription" @closeKeyModal="closeKeyModal"></key-modal>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import KeyModal from '../components/modals/KeyModal.vue'

export default {
  name: 'subscription',
  components: {
    KeyModal
  },
  data () {
    return {
      waiting: false,
      error: '',
      subscription: null,
      newName: '',
      updating: false,
      months: 1,
      payments: null,
      instance: null,
      launching: false,
      keyModal: {
        opened: false,
      },
      interval: null,
      refreshing: false,
    }
  },
  computed: {
    token () {
      return this.$store.state.user.token
    },
    subscriptionId () {
      return this.$route.params.subscriptionId
    },
    server () {
      return this.$store.state.config.server
    },
    unitPrice () {
      return this.$store.state.config.unitPrice
    },
    newNameValid () {
      if (!this.subscription) {
        return false
      }
      return (this.newName != this.subscription.name) && this.newName.trim()
    },
    priceLabel () {
      if (!this.subscription) {
        return ''
      }
      var total = this.unitPrice * this.months
      return '$' + total.toFixed(2)
    }
  },
  methods: {
    getSunscription () {
      this.waiting = true
      this.error = ''
      this.$http.get(this.server + '/get-subscription/' + this.subscriptionId).then(resp => {
        this.buildSubscription(resp.body)
        if (this.subscription.instanceId) {
          this.getInstance()
        }
        this.waiting = false
      }, (err) => {
        this.error = err.body
        this.waiting = false
      })
    },
    buildSubscription (data) {
      var sub = {...data}
      sub.months = 1
      sub.price = this.unitPrice
      sub.priceLabel = '$' + sub.price.toFixed(2)
      if (sub.startTime) {
        var startDate = new Date(sub.startTime * 1000)
        var endDate = new Date(sub.endTime * 1000)
        sub.periodLabel = startDate.toLocaleDateString('en-US') + ' ~ ' + endDate.toLocaleDateString('en-US')
      }
      this.subscription = sub
      this.newName = sub.name
    },
    updateName () {
      if (!this.newNameValid) {
        return
      }
      this.updating = true
      this.$http.post(this.server + '/update-sub-name/' + this.subscriptionId, {name: this.newName.trim()}).then(resp => {
        this.subscription.name = this.newName.trim()
      }).catch(err => {
        this.error = err.body
      }).finally(() => {
        this.updating = false
      })
    },
    getPayments() {
      this.$http.get(this.server + '/get-sub-payments/' + this.subscriptionId).then(resp => {
        this.payments = resp.body.map(this.buildPayment).sort((a, b) => b.createTime - a.createTime)
      })
    },
    buildPayment (data) {
      var payment = {...data}
      return payment
    },
    getInstance () {
      this.refreshing = true
      this.$http.get(this.server + '/get-sub-instance/' + this.subscriptionId).then(resp => {
        this.instance = resp.body
        this.refreshing = false
      }, (err) => {
        this.error = err.body
        this.refreshing = false
      })
    },
    launchEc2 () {
      var message = {subscriptionId: this.subscriptionId}
      this.launching = true
      this.$http.post(this.server + '/create-subscription-instance', message).then(resp => {
        this.instance = resp.body
        this.subscription.instanceId = resp.body.id
        this.refreshInstance()
        this.launching = false
      }).catch(err => {
        this.error = err.body
        this.launching = false
      })
    },
    refreshInstance () {
      if (this.interval) {
        return
      }
      this.interval = setInterval(() => {
        if (this.instance.status == 'Active') {
          clearInterval(this.interval)
        }
        this.getInstance()
      }, 5000);
    },
    openKeyModal () {
      this.keyModal.opened = true
    },
    closeKeyModal () {
      this.keyModal.opened = false
    },
  },
  mounted () {
    if (this.token) {
      Vue.http.headers.common['Authorization'] = this.token
      this.getSunscription()
      this.getPayments()
    } else {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.name-input {
  max-width: 300px;
}
</style>
