import axios from 'axios';
import qs from 'qs'//这个只要安装了axios就可以直接引入
const fttp = axios.create({
  baseURL: '/trans',
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
export function transGet(url:any,param={}){
    return new Promise((resolve,reject)=>{
        fttp.get(url,{params:parseParam(param)})
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
export function transPost(url:any,param={}){
    return new Promise((resolve,reject)=>{
        fttp.post(url,parseParam(param))
        .then(response=>{
            resolve(response.data)
        })
        .catch(err=>{
            reject(err)
        })
    })
}
