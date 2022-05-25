import { createStore } from 'vuex'
import storageUtil from '@/utils/storageUtil'
export default createStore({
  state: {
    HistList:[],
    UnSolveList:[],
  },
  mutations: {
    setHistList(state, v) {
       state.HistList = v;
      if (state.HistList.length>10){
        storageUtil.setLocalItem("HistList", state.HistList.slice(-10));
      }else {
        storageUtil.setLocalItem("HistList", state.HistList);
      }
    },


  },
  actions: {
      delHistList(state, v) {
      const His=storageUtil.getLocalJsonItem("HistList");
      let res=false
      for(const index in His){
          if (His[index]['id'] === v){
            const temp=His.splice(index,1);
            res=true
            storageUtil.setLocalItem("HistList", His);
            break;
          }
      }
    return res
    },
  },
  modules: {
  },
  getters:{
   getHistList() {
    return  storageUtil.getLocalJsonItem("HistList")?storageUtil.getLocalJsonItem("HistList").reverse():[];
    },
  },
})
