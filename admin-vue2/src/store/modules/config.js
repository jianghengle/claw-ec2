const dev = process.env.NODE_ENV == 'development'

// initial state
export const state = {
  server: dev ? 'http://localhost:3000' : 'https://k2iucs3uo1.execute-api.us-west-2.amazonaws.com/Prod',
}

// mutations
export const mutations = {
}

export default {
  namespaced: true,
  state,
  mutations
}
