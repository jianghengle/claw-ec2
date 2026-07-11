// initial state
export const state = {
  token: localStorage.getItem('token'),
  username: localStorage.getItem('username'),
  role: localStorage.getItem('role'),
}
 
// mutations
export const mutations = {
  setUser (state, user) {
    state.username = user.username
    state.token = user.token
    state.role = user.role
  },


  reset (state) {
    state.token = null
    state.username = null
    state.role = null
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('role')
  },
}

export default {
  namespaced: true,
  state,
  mutations
}
