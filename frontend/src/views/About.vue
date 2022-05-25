<template>
  <div id="about" class="about">
    <Header></Header>
       <el-main>
         <div class="block">
          <el-carousel height="500px">
            <el-carousel-item v-for="(item,index) in swiperList" :key="index">
              <a href="https://ctn.hkbu.edu.hk/wikiconf2021/" target="_blank"><img  src="../assets/images/swiper1.png" style="max-width: 100%;margin: 0 auto"></a>
<!--              <div class="carouselImg" :style="{'background-image': `url(../assets/images/swiper1.png)`}"></div>-->
            </el-carousel-item>
          </el-carousel>
         </div>

         <div class="page">
            <h1>About Project</h1>
           <p>Wikipedia is the world's largest online encyclopaedia. It has 303 active language editions, which were accessed from 1.7bn unique devices during October 2020. Now over twenty years old, the encyclopaedia has been studied by academics working within a range of disciplines since the mid-2000s, although it is only relatively recently that it has started attracting the attention of translation scholars too. During a short space of time we have learnt a considerable amount about topics such as translation quality, translation and cultural remembrance, multilingual knowledge production and point of view, the prominent role played by narratives in articles reporting on news stories, and how translation is portrayed in multiple language versions of the Wikipedia article on the term itself. However, translation largely remains Wikipedia's "dark matter": not only is it difficult to locate, but researchers have so far struggled to map out the full extent of its contribution to this multilingual resource. Our aim in organising this international event is to allow the research community to take stock of the progress made so far and to identify new avenues for future work.</p>
         </div>

          <div class="page">
            <h1>Our Team</h1>
            <el-row :gutter="20">
            <el-col :xs="8" :sm="6" :md="4" :lg="3" :xl="6">
              <el-card :body-style="{ padding: '0px' }">
                <img src="https://ctn.hkbu.edu.hk/wikiconf2021/assets/img/speakers/markshuttleworth.jpg" class="image">
                <div style="padding: 14px;">
                 <span>Mark Shuttleworth</span>
                </div>
               </el-card>
            </el-col>
                <el-col :xs="8" :sm="6" :md="4" :lg="3" :xl="6">
              <el-card :body-style="{ padding: '0px' }">
                <img src="https://ctn.hkbu.edu.hk/wikiconf2021/assets/img/speakers/zhilutu.jpg" class="image">
                <div style="padding: 14px;">
                 <span>ZHILU TU</span>
                </div>
               </el-card>
            </el-col>
                <el-col :xs="8" :sm="6" :md="4" :lg="3" :xl="6">
              <el-card :body-style="{ padding: '0px' }">
                <img src="https://ctn.hkbu.edu.hk/wikiconf2021/assets/img/speakers/markshuttleworth.jpg" class="image">
                <div style="padding: 14px;">
                 <span>Mark Shuttleworth</span>
                </div>
               </el-card>
            </el-col>
            </el-row>
          </div>

             <div class="page">
            <h1>Contact Us</h1>
            <el-row :gutter="20">
            <el-col :xs="8" :sm="6" :md="4" :lg="3" :xl="6">

            </el-col>
            </el-row>
          </div>

       </el-main>
     <Footer></Footer>
  </div>
</template>
<script lang="ts">
import {defineComponent, onMounted} from 'vue';

import Header from '@/views/components/header.vue'
import Footer from '@/views/components/footer.vue'

export default defineComponent({
  name: 'About',
  components: {Header,Footer},
  setup() {
    const swiperList=[
      {img:'@/swiper1.png',title:"WikiConf"}
    ]

    onMounted(()=>{
    console.log('')
    })
    return {
      swiperList
    }
  }
})

</script>