import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import router from "./router";
import "./assets/tailwind.css"; // if Tailwind is configured, else skip this line

createApp(App).use(router).mount("#app");
