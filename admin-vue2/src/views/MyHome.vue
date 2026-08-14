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
    <div v-if="token" class="p-3">
      <nav class="breadcrumb" aria-label="breadcrumbs">
        <ul>
          <li class="is-active"><a href="#" aria-current="page">Subscriptions</a></li>
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

        <div v-if="!waiting">
          <div v-if="subscriptions">
            <div v-if="subscriptions.length">
              <div class="columns is-multiline">
                <div class="column is-half" v-for="sub in subscriptions" :key="'sub-' + sub.id">
                  <div class="card">
                    <header class="card-header" :class="{'is-clickable': sub.status != 'Not started'}" @click="openSubscription(sub)">
                      <p class="card-header-title">{{ sub.name }}</p>
                      <button class="card-header-icon" v-if="sub.status != 'Not started'">
                        <span class="icon">
                          <i class="fas fa-angle-right" aria-hidden="true"></i>
                        </span>
                      </button>
                      <button class="card-header-icon" v-if="sub.status == 'Not started'" @click="deleteSubscription(sub)">
                        <span class="icon">
                          <i class="fas fa-trash" aria-hidden="true"></i>
                        </span>
                      </button>
                    </header>
                    <div class="card-content">
                      <div class="content">
                        <div class="field is-horizontal">
                          <div class="field-label is-normal">
                            <label class="label">Status</label>
                          </div>
                          <div class="field-body">
                            <div class="field is-narrow">
                              <div class="control">
                                <span class="tag is-medium status-tag" :class="{'is-success': sub.status == 'Active'}">
                                  {{ sub.status }}
                                </span>
                              </div>
                              <p class="help is-info" v-if="sub.status == 'Not started'">
                                Please refresh page later after making payment.
                              </p>
                            </div>
                          </div>
                        </div>

                        <form :action="server + '/stripe/create-checkout-session'" method="POST">
                          <input type="hidden" name="subscriptionId" :value="sub.id">
                          <input type="hidden" name="token" :value="token">
                          <div class="field is-horizontal" v-if="sub.status == 'Not started'">
                            <div class="field-label is-normal">
                              <label class="label">Start</label>
                            </div>
                            <div class="field-body">
                              <div class="field has-addons">
                                <p class="control">
                                  <span class="select">
                                    <select name="months" v-model="sub.months" @change="computePrice(sub)">
                                      <option :value="1">1 month</option>
                                      <option :value="2">2 month</option>
                                      <option :value="3">3 month</option>
                                    </select>
                                  </span>
                                </p>
                                <p class="control">
                                  <a class="button is-static">
                                    {{ sub.priceLabel }}
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

                        <div class="field is-horizontal" v-if="sub.status != 'Not started'">
                          <div class="field-label is-normal">
                            <label class="label">Period</label>
                          </div>
                          <div class="field-body">
                            <div class="field is-narrow">
                              <div class="control static-field-value">
                                <input class="input is-static" type="text" :value="sub.periodLabel" readonly />
                              </div>
                            </div>
                          </div>
                        </div>

                        <div class="field is-horizontal" v-if="sub.status == 'Active' && !sub.instanceId && !subInstanceMap[sub.id]">
                          <div class="field-label is-normal">
                            <label class="label">EC2</label>
                          </div>
                          <div class="field-body">
                            <div class="field is-narrow">
                              <div class="control">
                                <button class="button is-link" :class="{'is-loading': launching}" @click="launchEc2(sub)">
                                  Launch EC2
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>

                        <hr v-if="subInstanceMap[sub.id]" />

                        <div class="field is-horizontal" v-if="subInstanceMap[sub.id]">
                          <div class="field-label is-normal">
                            <label class="label">EC2</label>
                          </div>
                          <div class="field-body">
                            <div class="field is-narrow">
                              <div class="control">
                                <span class="tag is-medium status-tag" :class="{'is-success': subInstanceMap[sub.id].status == 'Active'}" v-if="!refreshing">
                                  {{ subInstanceMap[sub.id].status }}
                                </span>
                                <span class="icon status-spinner" v-else>
                                  <i class="fas fa-spinner fa-pulse"></i>
                                </span>
                              </div>
                              <p class="help is-info" v-if="subInstanceMap[sub.id].status != 'Active'">
                                It might take up to 10 minutes to launch EC2 ...
                              </p>
                            </div>
                          </div>
                        </div>

                        <div class="field is-horizontal" v-if="subInstanceMap[sub.id] && subInstanceMap[sub.id].status == 'Active'">
                          <div class="field-label is-normal">
                            <label class="label claw-label">Claw</label>
                          </div>
                          <div class="field-body">
                            <div class="field is-narrow">
                              <div class="control">
                                <a class="button is-ghost claw-url" target="_blank" :href="'https://' + subInstanceMap[sub.id].domain + ':' + subInstanceMap[sub.id].clawPort + '/?token=' + subInstanceMap[sub.id].clawToken">
                                  <span>Secure Claw URL</span>
                                  <span class="icon is-small">
                                    <i class="fas fa-external-link-alt"></i>
                                  </span>
                                </a>
                                <button class="button ml-3" @click="openKeyModal(sub)">
                                  <span class="icon is-small">
                                    <i class="fas fa-key"></i>
                                  </span>
                                  <span>API Key</span>
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>

                      </div>
                    </div>
                  </div>
                </div>
              </div>

            </div>
            <div v-else>
              No subscriptions found. Please add subscription and make payment to activate subscription.
            </div>
          </div>

          <div class="buttons mt-6 mb-6">
            <a class="button" :class="{'is-loading': creating}" @click="createSubscription">
              <span class="icon">
                <i class="fas fa-plus"></i>
              </span>
              <span>New subscription</span>
            </a>
          </div>

          <hr/>

          <div class="mt-6">
            <div class="field">
              <label class="label">Demo EC2</label>
              <div class="control">
                <a class="button" target="_blank" href="https://mailapp.myworkflowhub.com:18789/?token=kEd_rF5vcUJM15E0">
                  <span>Demo Claw URL</span>
                  <span class="icon is-small">
                    <i class="fas fa-external-link-alt"></i>
                  </span>
                </a>
              </div>
              <p class="help is-info">Shared demo claw EC2. Please try it out respectfully.</p>
            </div>

          </div>
        </div>
      </div>

      <key-modal :opened="keyModal.opened" :subscription="keyModal.subscription" @closeKeyModal="closeKeyModal"></key-modal>

    </div>
  </div>
</template>

<script>
import KeyModal from '../components/modals/KeyModal.vue'

export default {
  name: 'my-home',
  components: {
    KeyModal
  },
  data () {
    return {
      error: '',
      waiting: false,
      email: '',
      sending: false,
      sent: false,
      subscriptions: null,
      creating: false,
      subInstanceMap: {},
      launching: false,
      keyModal: {
        opened: false,
        subscription: null,
      },
      interval: null,
      refreshing: false,
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    token () {
      return this.$store.state.user.token
    },
    unitPrice () {
      return this.$store.state.config.unitPrice
    },
    emailValid () {
      var re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
      return re.test(this.email.trim().toLowerCase())
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
        this.sent = true
      }).catch(err => {
        this.error = err.body
      }).finally(() => {
        this.sending = false
      })
    },
    createSubscription () {
      this.creating = true
      this.$http.post(this.server + '/create-subscription', {}).then(resp => {
        this.subscriptions.push(this.makeSubscription(resp.body))
      }).catch(err => {
        this.error = err.body
      }).finally(() => {
        this.creating = false
      })
    },
    makeSubscription (data) {
      var sub = {...data}
      sub.months = 1
      sub.price = this.unitPrice
      sub.priceLabel = '$' + sub.price.toFixed(2)
      if (sub.startTime) {
        var startDate = new Date(sub.startTime * 1000)
        var endDate = new Date(sub.endTime * 1000)
        sub.periodLabel = startDate.toLocaleDateString('en-US') + ' ~ ' + endDate.toLocaleDateString('en-US')
      }
      if (data.instanceId === undefined) {
        sub.instanceId = null
      }
      return sub
    },
    computePrice (sub) {
      this.$nextTick(() => {
        sub.price = sub.months * this.unitPrice
        sub.priceLabel = '$' + sub.price.toFixed(2)
      })
    },
    deleteSubscription (sub) {
      var confirm = {
        title: 'Delete subscription',
        message: 'Are you sure to remove this subscription "' + sub.name + '"?',
        button: 'Yes, I am sure.',
        callback: {
          context: this,
          method: this.deleteSubscriptionConfirmed,
          args: [sub]
        }
      }
      this.$store.commit('modals/openConfirmModal', confirm)
    },
    deleteSubscriptionConfirmed (sub) {
      var message = {subscriptionId: sub.id}
      this.$http.post(this.server + '/delete-subscription', message).then(resp => {
        var idx = this.subscriptions.indexOf(sub)
        this.subscriptions.splice(idx, 1)
      }).catch(err => {
        this.error = err.body
      }).finally(() => {
        this.creating = false
      })
    },
    openSubscription (sub) {
      this.$router.push('/subscription/' + sub.id)
    },
    launchEc2 (sub) {
      var message = {subscriptionId: sub.id}
      this.launching = true
      this.$http.post(this.server + '/create-subscription-instance', message).then(resp => {
        this.subInstanceMap[sub.id] = resp.body
        sub.instanceId = resp.body.id
        this.refreshInstance(sub.id)
        this.launching = false
      }).catch(err => {
        this.error = err.body
        this.launching = false
      })
    },
    refreshInstance (subId) {
      if (this.interval) {
        return
      }
      this.interval = setInterval(() => {
        var instance = this.subInstanceMap[subId]
        if (instance.status == 'Active') {
          clearInterval(this.interval)
        }
        this.getSubscriptionInstance(subId)
      }, 5000);
    },
    getSubscriptionInstance (subId) {
      this.refreshing = true
      this.$http.get(this.server + '/get-sub-instance/' + subId).then(resp => {
        this.subInstanceMap[subId] = resp.body
        this.refreshing = false
      }).catch(err => {
        this.error = err.body
        this.refreshing = false
      })
    },
    openKeyModal (subscription) {
      this.keyModal.subscription = subscription
      this.keyModal.opened = true
    },
    closeKeyModal () {
      this.keyModal.subscription = null
      this.keyModal.opened = false
    },
  },
  mounted () {
    this.$nextTick(() => {
      if (this.token) {
        this.waiting = true
        this.$http.get(this.server + '/get-user-subscriptions').then(resp => {
          var subscriptions = resp.body.map(this.makeSubscription)
          var subInstanceMap = {}
          for (var sub of subscriptions) {
            subInstanceMap[sub.id] = null
          }
          this.subInstanceMap = subInstanceMap
          this.subscriptions = subscriptions
          for (var sub of subscriptions) {
            if (sub.instanceId) {
              let subId = sub.id
              this.getSubscriptionInstance(subId)
            }
          }
        }).catch(err => {
          this.error = err.body
        }).finally(() => {
          this.waiting = false
        })
      }
    })
  },
  unmounted () {
    if (this.interval) {
      clearInterval(this.interval)
    }
  },
}
</script>

<style scoped>
.status-tag {
  position: relative;
  top: 3px;
}

.status-spinner {
  position: relative;
  top: 4px;
}

.static-field-value {
  position: relative;
  top: -2px;
}

.claw-label {
  position: relative;
  top: 2px;
}

.claw-url {
  padding-left: 0px !important;
}
</style>
