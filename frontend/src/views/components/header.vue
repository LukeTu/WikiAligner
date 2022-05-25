<template>
<nav class="navbar navbar-expand-lg navbar-light bg-light">
  <div class="container-fluid">
    <a class="navbar-brand Logo" href="#"><img src="../../assets/images/logo3.png" style="max-height: 50px"  class="img-fluid" alt=""></a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav me-auto mb-2 mb-lg-0">
        <li class="nav-item">
          <a class="nav-link active" @click="go('/')" aria-current="page" href="#">Home</a>
        </li>

        <li class="nav-item">
          <a class="nav-link" @click="go('/history')">History</a>
        </li>
          <li class="nav-item">
          <a class="nav-link" href="#">Help</a>
        </li>
          <li class="nav-item dropdown">
              <a class="nav-link" @click="go('/about')">About us</a>
        </li>
      </ul>
       <slot class="d-flex"></slot>
    </div>
  </div>
</nav>



<!--  <header class="navbar  has-sidebar" style="background-color: #fff">-->
<!--     <div class="navbar-wrapper">-->
<!--        <div class="header-container">-->
<!--          <div class="logo-container">-->
<!--            <span class="Logo"><img src="../../assets/images/logo3.png"  alt=""></span>-->
<!--          </div>-->
<!--          <div class="content">-->
<!--             <el-menu-->
<!--              :default-active="activeIndex"-->
<!--              class="el-menu-home"-->
<!--              mode="horizontal"-->
<!--              :router=true-->
<!--              :collapse-transition=true-->
<!--              :ellipsis=false-->
<!--          >-->
<!--            <slot class="pt-14"></slot>-->
<!--            <el-menu-item index="/">Home</el-menu-item>-->
<!--&lt;!&ndash;            <el-sub-menu index="/history">&ndash;&gt;-->
<!--&lt;!&ndash;              <template #title>History</template>&ndash;&gt;-->
<!--&lt;!&ndash;              <el-menu-item index="/history">item one</el-menu-item>&ndash;&gt;-->
<!--&lt;!&ndash;              <el-menu-item index="/history">item two</el-menu-item>&ndash;&gt;-->
<!--&lt;!&ndash;              <el-menu-item index="/history">item three</el-menu-item>&ndash;&gt;-->
<!--&lt;!&ndash;            </el-sub-menu>&ndash;&gt;-->
<!--            <el-menu-item index="/history">history</el-menu-item>-->
<!--            <el-menu-item index="/about">About Us</el-menu-item>-->
<!--          </el-menu>-->
<!--             <div class="gitWrapper">-->
<!--              <a class="githubIcon" title="GitHub" href="https://github.com/LukeTu/WikiAligner" target="_blank">-->
<!--                <i class="el-icon" style="font-size:24px;">-->
<!--                   <svg preserveAspectRatio="xMidYMid meet" viewBox="0 0 24 24" width="1.2em" height="1.2em" data-v-6c8d2bba=""><path fill="currentColor" d="M12 2C6.475 2 2 6.475 2 12a9.994 9.994 0 0 0 6.838 9.488c.5.087.687-.213.687-.476c0-.237-.013-1.024-.013-1.862c-2.512.463-3.162-.612-3.362-1.175c-.113-.288-.6-1.175-1.025-1.413c-.35-.187-.85-.65-.013-.662c.788-.013 1.35.725 1.538 1.025c.9 1.512 2.338 1.087 2.912.825c.088-.65.35-1.087.638-1.337c-2.225-.25-4.55-1.113-4.55-4.938c0-1.088.387-1.987 1.025-2.688c-.1-.25-.45-1.275.1-2.65c0 0 .837-.262 2.75 1.026a9.28 9.28 0 0 1 2.5-.338c.85 0 1.7.112 2.5.337c1.912-1.3 2.75-1.024 2.75-1.024c.55 1.375.2 2.4.1 2.65c.637.7 1.025 1.587 1.025 2.687c0 3.838-2.337 4.688-4.562 4.938c.362.312.675.912.675 1.85c0 1.337-.013 2.412-.013 2.75c0 .262.188.574.688.474A10.016 10.016 0 0 0 22 12c0-5.525-4.475-10-10-10z"></path></svg>-->
<!--                </i>-->
<!--               </a>-->
<!--            </div>-->
<!--          </div>-->
<!--        </div>-->

<!--      </div>-->

</template>



<script lang="ts">
import {defineComponent, onMounted, reactive, toRefs, ref, watch, computed} from 'vue';
import md5 from 'md5'
import {getDemo, getAssociateWords, getRes, getLangList, getAnalyze} from '@/api/common'
import {ElNotification} from 'element-plus'
import router from "@/router";
import { useStore } from 'vuex'
import "bootstrap/dist/css/bootstrap.min.css"
import "bootstrap"
export default defineComponent({
  name: 'Header',
  components: {},
  setup() {
    const config = reactive({
      temp: 0,
      drawer: false,
      flag: true,
      simLisValue: 0,
      showAllData: false,
      fa_data: [],
      keywordList: []
    });
    const getPath=()=>{
      console.log()
    }
    const activeIndex=router.currentRoute.value.path?router.currentRoute.value.path:'/';
    const go = (e: any) => {
      router.push(e)
    }
    const handleSelect=(e:any)=>{
       router.push(e)
    }
  onMounted(()=>{
    getPath()
  })
  return{
    config,
    getPath,
    go,
    handleSelect,
    activeIndex,
       }
  }
  })
</script>

<style lang="less" scoped>
.el-menu--horizontal{
  border-bottom: none!important;
}
.navbar-wrapper{
    position: relative;
    padding: 0 12px 0 24px;
    top: 0;
    border-bottom: 1px solid #dcdfe6;
    .pt-14{padding-top: 14px}
    .header-container{
      max-width: 100vw;
      display: flex;
      margin: 0 auto;
      justify-content: flex-end;
      align-items: center;
      flex-grow: 1;
      .logo-container{
        display: flex;
        align-items: center;
        img{max-height: 50px}
      }
      .Logo{
        text-decoration: none;
        font-size: 32px;
        font-weight: bold;
        font-style: italic;
      }
      .gitWrapper{
        height: 24px;
        padding: 0 12px;
       .githubIcon{
        color: #000;
      }
      }
      .content{
        display: flex;
        justify-content: flex-end;
        align-items: center;
        flex-grow: 1;
      }
    }
  }
</style>