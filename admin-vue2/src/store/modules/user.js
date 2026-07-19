// initial state
const urlParams = new URLSearchParams(window.location.search)
const token = urlParams.get('token')

export const state = {
  token: token || localStorage.getItem('token'),
  email: localStorage.getItem('email'),
}
 
// mutations
export const mutations = {
  setUser (state, user) {
    state.token = user.token
    state.email = user.email
    localStorage.setItem('token', user.token)
    localStorage.setItem('email', user.email)
  },


  reset (state) {
    state.token = null
    state.email = null
    localStorage.removeItem('token')
    localStorage.removeItem('email')
  },
}

export default {
  namespaced: true,
  state,
  mutations
}
