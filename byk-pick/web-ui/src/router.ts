import { createRouter, createWebHistory } from 'vue-router'
import ItemPick from './components/ItemPick.vue'
import FilePick from './components/FilePick.vue'
import Admin from './components/Admin.vue'

const router = createRouter({
  history: createWebHistory('/'),
  routes: [
    {
      path: '/item-pick',
      name: 'item-pick',
      component: ItemPick
    },
    {
      path: '/f',
      name: 'file-pick',
      component: FilePick
    },
    {
      path: '/admin',
      name: 'admin',
      component: Admin
    }
  ]
})

// 路由守卫：管理后台登录检查
router.beforeEach(async (to, _from, next) => {
  if (to.path === '/admin' && sessionStorage.getItem('admin_authed') !== '1') {
    next('/')
    return
  }
  next()
})

export default router
