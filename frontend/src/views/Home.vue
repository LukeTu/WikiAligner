<template>
  <div id="home" class="home">
    <Header>
     <el-form :inline="true" :model="config.ruleForm" class="form-inline">
              <el-form-item>
                <el-select
                    v-model="config.ruleForm.keyword"
                    filterable
                    remote
                    reserve-keyword
                    placeholder="Please enter a keyword"
                    :remote-method="querySearchAsync"
                    :loading="config.loading"
                >
                  <el-option
                      v-for="item in config.keywordList"
                      :key="item"
                      :label="item"
                      :value="item"
                  />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-select v-model="config.ruleForm.language1" @change="changeLang1" filterable placeholder="language1" fit-input-width
                           clearable>
                  <el-option v-for="(item) in  config.languageList"  :key="item[0]" :label="item[0]+'-'+item[1]"
                           :value="item[0]"></el-option>
                </el-select>

              </el-form-item>

              <el-form-item>
                <el-select v-model="config.ruleForm.language2"  @change="changeLang2" placeholder="language2" fit-input-width clearable>
                  <el-option v-for="(item) in  config.languageList" :key="item[0]" :label="item[0]+'-'+item[1]"
                             :value="item[0]"></el-option>
                </el-select>
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="submitForm('ruleForm')" plain>Submit</el-button>
              </el-form-item>
            </el-form>
    </Header>
    <el-main>
         <div id="tool">
        <el-row :gutter="8"  style="align-items: center;">
          <el-col :span="8">
            <div  class="grid-content slider-wrapper bg-purple" style="padding-right: 15px">
              <span class="demonstration" style="padding-right: 12px">Similarity Score Threshold:</span>
              <el-slider :max=config.maxSim :min=config.minSim v-model="config.value1"  :format-tooltip="formatTooltip" :step="0.01" show-stops></el-slider>
            </div>
          </el-col>

          <el-col :span="14">
         <el-tooltip
              class="box-item"
              effect="dark"
              content="Download"
              placement="top-start"
         >
            <el-icon style="float: right;margin-right: 20px;margin-left: 10px" class="icon-self el-icon-download" @click="exportExcel">
              <download/>
            </el-icon>
         </el-tooltip>
              <el-tooltip
                class="box-item"
                effect="dark"
                content="Show All Data"
                placement="top-start"
              >
            <el-icon style="float: right" :class="{'bg-blue':config.showAllData}" class="icon-self el-icon-data-line"
                     @click="showAll">
              <data-line/>
            </el-icon>
             </el-tooltip>
            <span style="float: right;vertical-align: middle;margin-right: 20px;margin-top: 4px;"></span>
          </el-col>



        </el-row>
      </div>

      <el-row class="main">
        <el-col :span="12">
          <div class="box-title">{{ config.Text1 }} ----------{{ 'similarly: ' +   Math.round(config.simLisValue * 100) / 100   }}</div>
          <div id="text1" class="grid-content bg-purple box-text" ref="text1"
               @mouseover="changeFlag(false)">
                     <span v-for="items in config.fa_data.ST" :key="items"
                           @contextmenu.prevent="getTranlate('left',$event)">
                        <div v-if="items.content==='<br>' ">
                            <br>
                            <br>
                        </div>
                     <p v-else-if="items.content.substr(-2,2)=='=='"><b class="bg-orange">{{ items.content }}</b></p>
                     <b class="bg-orange" v-else-if="items.pair_id===-1">{{ items.content }}</b>
                     <b class="bg-orange" v-else-if="items.sim<config.value1 && items.sim>0 ">{{ items.content }}</b>
                     <b @click="doCopy($event,'left')"
                        :class="{'bg-demo':config.showAllData}"
                        :sim="items.sim"
                        :pair_id="items.pair_id"
                        v-else="items.pair_id!==-1"
                        @mouseover="wikiMouseover($event)"
                        @mouseleave="wikiMouseLeave($event)"
                     >{{ items.content }}<b class="num_tag" v-show="config.showAllData">{{ items.pair_id }}</b></b>
                    </span>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="box-title">{{ config.Text2 }}</div>
          <div id="text2" class="grid-content bg-purple-light box-text" ref="text2"
               @mouseover="changeFlag(true)">
                   <span v-for="items in config.fa_data.TT" :key="items"
                         @contextmenu.prevent="getTranlate('right',$event)">
                      <div v-if="items.content=='<br>' ">
                            <br>
                            <br>
                        </div>
                      <p v-else-if="items.content.substr(-2,2)=='=='"><b class="bg-orange">{{ items.content }}</b></p>
                     <b class="bg-orange" v-else-if="items.pair_id===-1">{{ items.content }}</b>
                     <b class="bg-orange" v-else-if="items.sim<config.value1">{{ items.content }}</b>
                     <b @click="doCopy($event,'right')" :class="{'bg-demo':config.showAllData}" :sim="items.sim"
                        :pair_id="items.pair_id"
                        v-else="items.pair_id!==-1" @mouseover="wikiMouseover($event)"
                        @mouseleave="wikiMouseLeave($event)">{{ items.content }}<b class="num_tag"
                                                                                   v-show="config.showAllData">{{
                         items.pair_id
                       }}</b></b>
                    </span>
          </div>
        </el-col>
      </el-row>
    </el-main>

  <Footer></Footer>
  </div>
</template>

<script lang="ts">
import {defineComponent, onMounted, reactive, toRefs, ref, watch, computed} from 'vue';
import md5 from 'md5'
import {getDemo, getAssociateWords, getRes, getLangList, getAnalyze, getExcel} from '@/api/common'
import {ElNotification} from 'element-plus'
import router from "@/router";
import { useRoute } from "vue-router";
import { useStore } from 'vuex'
import Header from '@/views/components/header.vue'
import Footer from '@/views/components/footer.vue'
import { ElMessage } from 'element-plus'
export default defineComponent({
  name: 'Home',
  components: {Footer,Header},
  setup() {
    const config = reactive({
      routeData:[],
      temp: 0,
      drawer: false,
      Text1: 'ST',
      Text2: 'TT',
      maxSim: 10,
      minSim: 0,
      flag: true,
      simLisValue: 0,
      value1: 0,
      showAllData: false,
      fa_data: [],
      simListOn: {},
      simListOff: {},
      languageList: [['en','Steve Jobs']],
      language1List: [['en','Steve Jobs']],
      language2List: [['zh','史蒂夫·乔布斯l']],
      translatedLanguage: '',
      ruleForm: {
        keyword: 'steve jobs',
        language1: 'en',
        language2: 'zh',
        languageText1: 'Steve Jobs',
        languageText2: '史蒂夫·乔布斯',
      },
      rules: {
        keyword: [
          {required: true, message: 'please input keywords', trigger: 'blur'},
        ],
        language1: [
          {required: true, message: 'please select', trigger: 'blur'},
        ],
        language2: [
          {required: true, message: 'please select', trigger: 'blur'},
        ],
      },
      keywordList: []
    });
    const store = useStore();
    const route = useRoute();
    const showAll = () => {
      config.showAllData = !config.showAllData;
    };

    const formatTooltip=(val:any)=>{
          return val.toFixed(2);
    }
    const submitForm = () => {
      let param={
        keyword:config.ruleForm.keyword,
        language_code1: config.ruleForm.language1,
        wiki_title1: config.ruleForm.languageText1,
        language_code2: config.ruleForm.language2,
        wiki_title2: config.ruleForm.languageText2,
      }
      if(param.keyword!=='steve jobs'){
        let tempList= store.getters.getHistList?store.getters.getHistList:[]
        let tempREs=param;
        tempREs['res']={};
        tempREs['date']=new Date().toLocaleString();
        tempREs['id']=Date.now()+Math.ceil(Math.random()*1000).toString();
        tempList.push(tempREs)
        store.commit('setHistList', tempList);
      }

      getAnalyze(param).then((response: any) => {
        if(response.success){
          let keys = Object.keys(response.result)
        config.fa_data = response.result;
        config.Text1 = keys[0];
        config.Text2 = keys[1];
        config.maxSim = response.result.maxSim;
        config.minSim = response.result.minSim;
        }else{
           ElMessage.error(response.message)
        }

      })
    };
    const getTranlate = (type: string, event: any) => {
      let salt = 'demo'
      let q = event.target.firstChild.textContent
      let from = type === 'left' ? config.ruleForm.language1 : config.ruleForm.language2
      let to = type === 'left' ? config.ruleForm.language2 : config.ruleForm.language1
      let sign = md5(`20210620000867906${q}${salt}0NNfT6b27iPaMVw9hAgp`)
      let appid = `20210620000867906`
      let data = {"q": q, "from": from, "to": to, "appid": '20210620000867906', "salt": salt, "sign": sign};
      let end = `?q=${q}&from=${from}&to=${to}&appid=${appid}&salt=${salt}&sign=${sign}`
      getDemo(data, end).then((res: any) => {
        config.translatedLanguage = res.trans_result[0].dst
        ElNotification({
          title: 'Translation',
          message: config.translatedLanguage,
          duration: 6000
        })
      })
    };
    const go = (e: any) => {
      router.push(e)
    }

    const links = ref<string[]>([])
    const loadAll = () => {
      return []
    }

    const querySearchAsync = (queryString: string, cb: (arg: any) => void) => {
      const param = {query: queryString};
      getAssociateWords(param).then((res: any) => {
        config.keywordList = res.result.keyword_options
      })
    }

    const createFilter = (queryString: string) => {
      return (restaurant: string) => {
        return (
            restaurant.toLowerCase().indexOf(queryString.toLowerCase()) === 0
        )
      }
    }


    const wikiMouseover = (e: any) => {
      let pair_id = e.target.getAttribute('pair_id').toString();
      config.simLisValue = e.target.getAttribute('sim').toString();
      document.querySelectorAll('[pair_id="' + pair_id + '"]').forEach(function (item) {
        item.classList.add("bg_blue")
      })
    }
    const wikiMouseLeave = (e: any) => {
      document.querySelectorAll('b').forEach(function (item) {
        item.classList.remove("bg_blue");
      })
      config.simLisValue = 0
    }

    const changeFlag = (flag: any) => {
      config.flag = flag
    }
    const sysHandleScroll = () => {
      console.log(1)
    }
    const exterHandleScroll = () => {
      console.log(1)
    }

    const updateLangList = (keyword: string) => {
      getLangList({keyword: keyword}).then((res: any) => {
        config.ruleForm.language1 = ''
        config.ruleForm.language2 = ''
        config.languageList = res.result.wiki_title_options
      })
    }

    const doCopy = (e: any, type: any) => {
      if (type === 'left') {
        let pair_id = e.target.getAttribute('pair_id').toString()
        let cc: any = document.querySelectorAll('[pair_id="' + pair_id + '"]')
        const ccTop = cc[1] ? cc[1].offsetTop : 0;
        const text2 = document.getElementById('text2')
        if (text2 && ccTop)
          text2.scrollTop = ccTop - 60;

      } else {
        let pair_id = e.target.getAttribute('pair_id').toString()
        let cc: any = document.querySelectorAll('[pair_id="' + pair_id + '"]')
        const ccTop = cc[0] ? cc[0].offsetTop : 0;
        const text1 = document.getElementById('text1')
        if (text1 && ccTop)
          text1.scrollTop = ccTop - 60;
      }
    }
    const changeLang1=(val:any)=>{
      const temp=config.languageList;
      for (let i of temp){
        if(i[0]===val){
          config.ruleForm.languageText1=i[1]
          break
        }
      }
    }
      const exportExcel=()=>{
      getExcel({keyword:config.ruleForm.keyword,language1:config.ruleForm.language1,language2:config.ruleForm.language2}).then((res:any)=>{
         let url = window.URL.createObjectURL(
            new Blob([res.data], { type: 'application/vnd.ms-excel' })
          );
          let link = document.createElement('a');
          link.download = 'export.xlsx';
          link.href = url;
          link.click();
      })
      }
     const changeLang2=(val:any)=>{
     const temp=config.languageList;
          for (let i of temp){
            if(i[0]===val){
             config.ruleForm.languageText2=i[1]
              break
            }
          }
        }
    watch(
        () => config.ruleForm.keyword,
        (e) => {
          updateLangList(e)
        }
    );


    onMounted(() => {

      submitForm()
    });

    return {
      //导航
      showAll,
      submitForm,
      getTranlate,
      changeFlag,
      sysHandleScroll,
      exterHandleScroll,
      //鼠标浮动事件
      wikiMouseover,
      wikiMouseLeave,
      //联想
      querySearchAsync,
      config,
      go,
      doCopy,
      changeLang1,
      changeLang2,
      exportExcel,
      formatTooltip,

    }
  }
});
</script>
<style lang="less" scoped>
#home{
  .el-menu-home{
    display: flex;
    justify-content: flex-end;
    align-items: center;
    flex-grow: 1;

  }
  .icon-self{width: 2em;height: 2em;margin: 8px}
  #tool{
    padding: 5px 15px;
    min-height: 45px;
    background: #f2f2f2;
    color: #555;
    opacity: .9;
    border-radius: 6px;
   .slider-wrapper{
    display: flex;
    align-items: center;
    .demonstration {
        font-size: 14px;
        line-height: 44px;
        flex: 1;
        //overflow: hidden;
        //text-overflow: ellipsis;
        white-space: nowrap;
        margin-bottom: 0;
      }
     .el-slider {
      flex: 0 0 70%;
    }
  }

  }
  .form-inline{
    padding-top: 14px;
  .el-form-item{
    margin-bottom: 0;
  }
  }
}

</style>
