<template>
  <div id="about" class="about">
      <Header></Header>
    <el-main>

    </el-main>
    <Footer></Footer>
  </div>
</template>
<script lang="ts">
import {defineComponent, onMounted, reactive, toRefs, ref, watch, computed} from 'vue';

import router from "@/router";
import {useStore} from "vuex";
import Header from '@/views/components/header.vue'
import Footer from '@/views/components/footer.vue'
import { ElMessage } from 'element-plus'
export default defineComponent({
  name: 'About',
  components: {Header,Footer},
  setup() {
    const store = useStore();
    const currentPage = ref(1)
    const pageSize = ref(5)
    const HistList = ref([])
    const tableData = ref([]);
    const total = ref(0)
    const delHisLog = (index: number, row: any) => {
     let res=store.dispatch('delHistList', row.id)
     if(res){
       ElMessage({
          message: 'delete success',
          type: 'success',
        })
     }else{
       ElMessage({
          message: 'delete error',
          type: 'error',
        })
     }

     getData()
    }
    const getData=()=>{
       HistList.value=store.getters.getHistList ? store.getters.getHistList : []
       total.value=HistList.value.length
       tableData.value=HistList.value.slice((currentPage.value - 1) * pageSize.value, (currentPage.value - 1) * pageSize.value + pageSize.value)
    }
    onMounted(()=>{
      getData()
    })
    return {
      tableData,
      total,
      currentPage,
      pageSize,
      HistList,
      delHisLog,
      getData,
    }
  }
})

</script>