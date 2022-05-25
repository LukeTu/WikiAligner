import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import store from './store'
import * as ElIcons from '@element-plus/icons-vue'
const app = createApp(App)

for (const name in ElIcons){
	app.component(name,(ElIcons as any)[name])
}
app.use(ElementPlus)
app.use(store).use(router).mount('#app')
