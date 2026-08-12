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

                        <div class="field is-horizontal" v-if="sub.status == 'Active' && !sub.instanceId">
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

          <div class="buttons mt-6">
            <a class="button" :class="{'is-loading': creating}" @click="createSubscription">
              <span class="icon">
                <i class="fas fa-plus"></i>
              </span>
              <span>New subscription</span>
            </a>
          </div>

          <hr/>

          <div>
            demo
          </div>
        </div>
      </div>

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
      subscriptions: null,
      creating: false,
      instances: {},
      launching: false,
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
        var instances = {...this.instances, [subId]: resp.body}
        this.instances = instances
        sub.instanceId = resp.body.id
        this.launching = false
      }).catch(err => {
        this.error = err.body
        this.launching = false
      })
    },
  },
  mounted () {
    this.$nextTick(() => {
      if (this.token) {
        this.waiting = true
        this.$http.get(this.server + '/get-user-subscriptions').then(resp => {
          this.subscriptions = resp.body.map(this.makeSubscription)
        }).catch(err => {
          this.error = err.body
        }).finally(() => {
          this.waiting = false
        })
      }
    })
  },
}
</script>

<style scoped>
.status-tag {
  position: relative;
  top: 3px;
}

.static-field-value {
  position: relative;
  top: -2px;
}
</style>
