<template>
  <div id="History">
    <Header></Header>
    <el-main>
        <el-container>
        <el-table :data="tableData" stripe style="width: 100%">
      <el-table-column type="index"/>
      <el-table-column prop="keyword" label="keyword"/>
      <el-table-column prop="language_code1" label="language code1"/>
      <el-table-column prop="wiki_title1" label="language1"/>
      <el-table-column prop="language_code2" label="language code2"/>
      <el-table-column prop="wiki_title2" label="language2"/>
      <el-table-column prop="date" label="date time"/>
      <el-table-column label="Operations">
        <template #default="scope">
          <el-button
              size="small"
              type="success"
              @click="showInfo(scope.$index, scope.row)"
          >Info
          </el-button
          >

          <el-button
              size="small"
              type="danger"
              @click="delHisLog(scope.$index, scope.row)"
          >Delete
          </el-button
          >
        </template>
      </el-table-column>
    </el-table>
    <el-pagination background layout="prev, pager, next"  @current-change=getData :hide-on-single-page="true" v-model:currentPage="currentPage"
                   :page-size="pageSize" :total="total"/>
  </el-container>
    </el-main>
    <Footer></Footer>
  </div>
</template>
<script lang="ts">
import {defineComponent, onMounted, reactive, toRefs, ref, watch, computed} from 'vue';
import {useStore} from "vuex";
import Header from '@/views/components/header.vue'
import Footer from '@/views/components/footer.vue'
import { ElMessage } from 'element-plus'
import { useRouter } from "vue-router";
export default defineComponent({
  name: 'History',
  components: {Header,Footer},
  setup() {
    const store = useStore();
    const router = useRouter();
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
    const showInfo=(index: number, row: any)=>{
       router.push({name: 'Home',params:{info:JSON.stringify(row)}})
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
      showInfo,
    }
  }
})
</script>