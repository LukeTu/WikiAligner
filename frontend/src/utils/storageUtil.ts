const storageUtil:any = {
};


/**
 * 清空LocalStorage
 */ 
storageUtil.clearLocalItem = () =>{
	window.localStorage.clear();
}
/**
 * 设置LocalStorage
 */ 
storageUtil.setLocalItem = (name:any, value:any) => {
	if (!name || (name = name.trim()) == "") return;
	if (value && typeof value == 'object') {
		value = JSON.stringify(value);
	}
	window.localStorage.setItem(name, value);
}

/**
 * 删除localStorage中的数据
 */
storageUtil.removeLocalItem = (name:any) => {
	if (!name || (name = name.trim()) == "") return;
	window.localStorage.removeItem(name);
}

/**
 * 读取localStorage中的字符串数据
 */
storageUtil.getLocalItem = (name:any) => {
	if (!name || (name = name.trim()) == "") return "";
	return window.localStorage.getItem(name);
}

/**
 * 读取localStorage中的JSON对象数据
 */
storageUtil.getLocalJsonItem = (name:any) => {
	if (!name || (name = name.trim()) == "") return null;
	const itemVal = window.localStorage.getItem(name);
	if (itemVal && itemVal != "") {
		return JSON.parse(itemVal);
	} else {
		return null;
	}
}



storageUtil.setSessionItem = (name:any, value:any) => {
	if (!name || (name = name.trim()) == "") return;
	if (value && typeof value == 'object') {
		value = JSON.stringify(value);
	}
	sessionStorage.setItem(name,value);
}



storageUtil.getSessionJsonItem = (name:any) => {
	if (!name || (name = name.trim()) == "") return null;
	const itemVal = sessionStorage.getItem(name);
	if (itemVal && itemVal != "") {
		return JSON.parse(itemVal);
	} else {
		return null;
	}
}
export default storageUtil;
