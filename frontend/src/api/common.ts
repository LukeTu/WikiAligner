import axiosUtil from '@/utils/axiosUtils';
import {transGet,transPost}from '@/utils/axiosUtilsTrans';



//翻译
export const getDemo= (params:any,end:string)=>{
    return transPost('/trans/vip/translate'+end,params);
}


//联想词
export const getAssociateWords= (params:any)=>{
    // return axiosUtil.postByJson('/search',params);
    return axiosUtil.postByJson('/get_keyword_options',params);
}

//可选语言列表
export const getLangList= (params:any)=>{
    // return axiosUtil.postByJson('/getLangList',params);
    return axiosUtil.postByJson('/get_wiki_title_options',params);
}
//搜索结果
export const getAnalyze= (params:any)=>{
    return axiosUtil.postByJson('/analyze',params);
}



//对比结果
export const getRes= (params:any)=>{
    return axiosUtil.postByJson('/getRes',params);
}


//对比结果
export const getExcel= (params:any)=>{
    return axiosUtil.blob('/export_to_excel',params);
}