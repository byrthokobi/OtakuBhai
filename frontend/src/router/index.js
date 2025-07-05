import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/LoginView.vue";
import Chat from "../views/ChatView.vue";

const routes = [
  {
    path: "/",
    name: "Login",
    component: Login,
  },
  {
    path: "/chat",
    name: "Chat",
    component: Chat,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 🚧 Route Guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem("token");

  if (to.meta.requiresAuth && !isAuthenticated) {
    // Trying to access protected route while not logged in
    return next({ name: "Login" });
  }

  if (to.name === "Login" && isAuthenticated) {
    // Logged in user going to root/login should go to chat
    return next({ name: "Chat" });
  }

  next();
});

export default router;
