import axios from "axios";
import { ElMessage } from 'element-plus'
const baseUrl = "";
axios.defaults.timeout = 500000;
axios.defaults.baseURL = '/baseApi';

// 添加响应拦截器
axios.interceptors.response.use(response => {
	console.log(response)
	const data = response.data;
	let msg = data.message;
			console.log(response)
	  if ( response.request.responseType == 'blob') {
      return response;
    }

	switch (data.code) {
		case 401: //需要登录或Token无效
			// securityUtil.logout();
			if (!msg) {
				msg = "登录信息已失效，请重新登录！";
			}
			ElMessage.error(msg);
			break;
		case 403: // 没有操作权限
			if (!msg) {
				msg = "没有操作权限！";
			}
			ElMessage.error(msg);
			break;
		case 500: // 服务器错误
			if (!msg) {
				msg = "服务器发生未知错误！";
			}
			ElMessage.error(msg);
			break;
		default:
			break;
	}
	return data;
}, (error) => {
	if (error.response) {
		ElMessage.error(error.response.status + "：" + error.response.statusText);
	} else {
		ElMessage.error(error.message);
	}
	return Promise.reject(error);
});


function formDataUrlEncoder(data:any) {
	let transformData = "";
	if (data) {
		for (const key in data) {
			transformData +=
				"&" + encodeURIComponent(key) + "=" + encodeURIComponent(data[key]);
		}
		if (transformData.length > 0) {
			transformData = transformData.substring(1);
		}
	}
	return transformData;
}

const axiosUtil:any = {
};
// get请求
axiosUtil.get = (url:string, params:any) => {

	return axios({
		method: "get",
		url: `${baseUrl}${url}`,
		params: params,
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded',
			
		},
	});
};
// get请求
axiosUtil.blob = (url:string, params:any) => {

	return axios({
		method: "post",
		url: `${baseUrl}${url}`,
		params: params,
		headers: {
			'Content-Type':'application/json;charset=utf-8',

		},
		 responseType: 'blob'
	});
};
//

// post请求
axiosUtil.post = (url:string, data:any) => {
	return axios({
		method: "post",
		url: `${baseUrl}${url}`,
		data: data,
		//去除transformRequest
		transformRequest: [formDataUrlEncoder],
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded',
		},
	});
};
//
axiosUtil.put = (url:string, data:any)=> {
	return axios({
		method: "put",
		url: `${baseUrl}${url}`,
		data: data,
		transformRequest: [formDataUrlEncoder],
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded',
		},
	});
};

axiosUtil.delete = (url:string, data:any)=> {
	return axios({
		method: 'delete',
		url: `${baseUrl}${url}`,
		data: data,
		headers: {
			
		},
	});
};

axiosUtil.postByJson = (url:string, data:any)=> {
	return axios({
		method: 'post',
		url: `${baseUrl}${url}`,
		data: data,
		headers: {
			'Content-Type':'application/json;charset=utf-8',
		},
	});
};

axiosUtil.putByJson = (url:string, data:any)=> {
	return axios({
		method: 'put',
		url: `${baseUrl}${url}`,
		data: data,
		headers: {
			'Content-Type': 'application/json',
		},
	});
};

// 无需身份认定的get请求
axiosUtil.getWithoutAuth = (url:string, data:any)=> {
	return axios({
		method: "get",
		url: `${baseUrl}${url}`,
		data: data,
	});
};
// 无需身份认定的post请求
axiosUtil.postWithoutAuth = (url:string, data:any)=> {
	return axios({
		method: "post",
		url: `${baseUrl}${url}`,
		data: data,
		transformRequest: [formDataUrlEncoder],
		headers: {
			"Content-Type": "application/json",
		},
	});
};

export default axiosUtil;