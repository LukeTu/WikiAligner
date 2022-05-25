import axios from 'axios';
import qs from 'qs'//这个只要安装了axios就可以直接引入
const http = axios.create({
  baseURL: '/baseApi',
  timeout: 5000
});

axios.defaults.headers.post['Content-Type']='application/x-www=-form-urlencoded'

const parseParam=(data = {},contentType = 'application/x-www-form-urlencoded')=>{
  return contentType === 'application/x-www-form-urlencoded' ? qs.stringify(data):(contentType ==='application/json'?JSON.stringify(data):data);
}
/**
 * get封装
 * @params:url
 * @params:params
*/
export function httpGet(url:any,param={}){
    return new Promise((resolve,reject)=>{
        http.get(url,{params:parseParam(param)})
        .then(response=>{
            resolve(response.data)
        })
        .catch(err=>{
            reject(err)
        })
    })
}



/**
 * post封装
 * @params:url
 * @params:param
*/
export function httpPost(url:any,param={}){
    return new Promise((resolve,reject)=>{
        http.post(url,parseParam(param))
        .then(response=>{
            resolve(response.data)
        })
        .catch(err=>{
            reject(err)
        })
    })
}
