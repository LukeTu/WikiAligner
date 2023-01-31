<template>
  <div id="about" class="about">
    <Header></Header>
    <el-main>
      <div class="block">
        <el-carousel height="500px">
          <el-carousel-item v-for="(item,index) in swiperList" :key="index">
            <a href="https://ctn.hkbu.edu.hk/wikiconf2021/" target="_blank"><img src="../assets/images/swiper1.png"
                                                                                 style="max-width: 100%;margin: 0 auto"></a>
          </el-carousel-item>
        </el-carousel>
      </div>

      <div class="page container">
        <h1>About Project</h1>
        <p>Wikipedia is the world's largest online encyclopaedia. It has 303 active language editions, which were
          accessed from 1.7bn unique devices during October 2020. Now over twenty years old, the encyclopaedia has been
          studied by academics working within a range of disciplines since the mid-2000s, although it is only relatively
          recently that it has started attracting the attention of translation scholars too. During a short space of
          time we have learnt a considerable amount about topics such as translation quality, translation and cultural
          remembrance, multilingual knowledge production and point of view, the prominent role played by narratives in
          articles reporting on news stories, and how translation is portrayed in multiple language versions of the
          Wikipedia article on the term itself. However, translation largely remains Wikipedia's "dark matter": not only
          is it difficult to locate, but researchers have so far struggled to map out the full extent of its
          contribution to this multilingual resource. Our aim in organising this international event is to allow the
          research community to take stock of the progress made so far and to identify new avenues for future work.</p>
      </div>

      <div class="page container">
        <h1>Our Team</h1>

        <el-row :gutter="20">
          <el-col :xs="8" :sm="6" :md="4" :lg="3" :xl="6" v-for="items in config.memberList">
            <el-card :body-style="{ padding: '0px' }">
              <img :src=items.img class="image">
              <div style="padding: 14px;">
                <h4>{{ items.name }}</h4>
                <el-popover
                    placement="bottom-start"
                    :title=items.name
                    width="30%"
                    trigger="hover"
                    :content=items.desc
                >
                  <template #reference>
                    <p class="intro_desc">{{ items.desc }}</p>
                  </template>
                </el-popover>

              </div>
            </el-card>
          </el-col>
        </el-row>

      </div>

      <div class="page container">
        <h1>Contact Us</h1>
        <el-row :gutter="20">
          <el-col :xs="8" :sm="6" :md="4" :lg="3" :xl="6" style="margin-bottom: 100px">
              <a style="text-align: center" href="mailto:wikiconf@hkbu.edu.hk">wikiconf@hkbu.edu.hk</a>
          </el-col>
        </el-row>
      </div>

    </el-main>
    <Footer></Footer>
  </div>
</template>
<script lang="ts">
import {defineComponent, onMounted, reactive} from 'vue';

import Header from '@/views/components/header.vue'
import Footer from '@/views/components/footer.vue'
import {ElMessageBox} from 'element-plus'
import markshuttleworth from "@/assets/images/markshuttleworth.jpg";
import zhilutu from "@/assets/images/zhilutu.jpg";
import wangminghao from "@/assets/images/wangminghao.jpg";
import huazhiwen from "@/assets/images/huazhiwen.jpg";

export default defineComponent({
  name: 'About',
  components: {Header, Footer, markshuttleworth},
  setup() {
    const swiperList = [
      {img: '@/swiper1.png', title: "WikiConf"}
    ]
    const config = reactive({
      memberList: [
        {
          name: 'Mark Shuttleworth',
          desc: 'Mark Shuttleworth has been involved in translation studies research and teaching since 1993, at the University of Leeds, Imperial College London, University College London and, most recently, Hong Kong Baptist University. His publications include the Dictionary of Translation Studies, as well as articles on translation technology teaching, metaphor in translation, translation and the web, and Wikipedia translation. The use of digital methodologies in translation studies research is also an interest of his. His monograph on scientific metaphor in translation, Studying Scientific Metaphor in Translation, was published in 2017 and he is currently working on a second edition of the Dictionary.',
          img: markshuttleworth
        },
        {
          name: 'Zhilu Tu',
          desc: 'Zhilu Tu holds a master\'s degree in translation and is currently a PhD Student in the Department of Translation, Interpreting and Intercultural Studies at Hong Kong Baptist University. His research interests lie primarily in Translation Studies and the area of Digital Humanities. His research aims to use digital methods to explore humanities (translation) questions. At present, he is working on visualizing translation on social media such as Twitter and Weibo. The web-scraping and parallel-sentence-mining techniques introduced in his research have also been adapted to explore the \'dark matter\' in Wikipedia translation.',
          img: zhilutu
        },
        {
          name: 'Minghao Wang',
          desc: 'Minghao Wang obtained his M.Sc. (Distinction) from Hong Kong Baptist University and his B.Eng. (Distinguished Graduate) from the Communication University of China. He focuses mainly on natural language processing, deep learning, statistic learning, and computational communication and on applications of all these techniques. He has worked on projects including fact-checking, bitext mining, topic modelling and audience research. Output from those projects has been and is being published.',
          img: wangminghao
        },
        {
          name: 'Zhiwen Hua',
          desc: 'Zhiwen Hua, a web Full-Stack Engineer, and holds a master’s degree in AI and Digital Media from Hong Kong Baptist University. With five years’ experience in front-engineering, he has firstly been engaged in the development of school related systems in the Nanjing Institute of media. Now he is working for the Intellectual Property School of Jiangsu University, responsible for the development of intellectual property in the area of big data systems.',
          img: huazhiwen
        },
      ]
    })
    const open = () => {
      ElMessageBox.alert(
          'Zhiwen Hua, a web Full-Stack Engineer, and holds a master’s degree in AI and Digital Media from Hong Kong Baptist University. With five years’ experience in front-engineering, he has firstly been engaged in the development of school related systems in the Nanjing Institute of media. Now he is working for the Intellectual Property School of Jiangsu University, responsible for the development of intellectual property in the area of big data systems.',
          'Zhiwen Hua',
          {
            dangerouslyUseHTMLString: true,
          }
      )
    }
    onMounted(() => {
      console.log('')
    })
    return {
      config,
      swiperList,
      open,
    }
  }
})

</script>
<style lang="less" scoped>
#about{color: #555}
.page{
  h1{margin-top: 40px;margin-bottom: 40px}
}
@media (min-width: 768px) {
  .container {
    width: 750px;
  }
}

@media (min-width: 992px) {
  .container {
    width: 970px;
  }
}

@media (min-width: 1200px) {
  .container {
    width: 1170px;
  }
}

.intro_desc {
  font-size: 14px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}
</style>