(function(e){function t(t){for(var o,r,l=t[0],i=t[1],u=t[2],s=0,d=[];s<l.length;s++)r=l[s],Object.prototype.hasOwnProperty.call(a,r)&&a[r]&&d.push(a[r][0]),a[r]=0;for(o in i)Object.prototype.hasOwnProperty.call(i,o)&&(e[o]=i[o]);f&&f(t);while(d.length)d.shift()();return c.push.apply(c,u||[]),n()}function n(){for(var e,t=0;t<c.length;t++){for(var n=c[t],o=!0,r=1;r<n.length;r++){var l=n[r];0!==a[l]&&(o=!1)}o&&(c.splice(t--,1),e=i(i.s=n[0]))}return e}var o={},r={app:0},a={app:0},c=[];function l(e){return i.p+"js/"+({}[e]||e)+"."+{"chunk-2d216dc7":"20a94af9","chunk-2d2259e5":"7921901e","chunk-4baa741f":"fcfd89fe"}[e]+".js"}function i(t){if(o[t])return o[t].exports;var n=o[t]={i:t,l:!1,exports:{}};return e[t].call(n.exports,n,n.exports,i),n.l=!0,n.exports}i.e=function(e){var t=[],n={"chunk-4baa741f":1};r[e]?t.push(r[e]):0!==r[e]&&n[e]&&t.push(r[e]=new Promise((function(t,n){for(var o="css/"+({}[e]||e)+"."+{"chunk-2d216dc7":"31d6cfe0","chunk-2d2259e5":"31d6cfe0","chunk-4baa741f":"1d0df4c4"}[e]+".css",a=i.p+o,c=document.getElementsByTagName("link"),l=0;l<c.length;l++){var u=c[l],s=u.getAttribute("data-href")||u.getAttribute("href");if("stylesheet"===u.rel&&(s===o||s===a))return t()}var d=document.getElementsByTagName("style");for(l=0;l<d.length;l++){u=d[l],s=u.getAttribute("data-href");if(s===o||s===a)return t()}var f=document.createElement("link");f.rel="stylesheet",f.type="text/css",f.onload=t,f.onerror=function(t){var o=t&&t.target&&t.target.src||a,c=new Error("Loading CSS chunk "+e+" failed.\n("+o+")");c.code="CSS_CHUNK_LOAD_FAILED",c.request=o,delete r[e],f.parentNode.removeChild(f),n(c)},f.href=a;var b=document.getElementsByTagName("head")[0];b.appendChild(f)})).then((function(){r[e]=0})));var o=a[e];if(0!==o)if(o)t.push(o[2]);else{var c=new Promise((function(t,n){o=a[e]=[t,n]}));t.push(o[2]=c);var u,s=document.createElement("script");s.charset="utf-8",s.timeout=120,i.nc&&s.setAttribute("nonce",i.nc),s.src=l(e);var d=new Error;u=function(t){s.onerror=s.onload=null,clearTimeout(f);var n=a[e];if(0!==n){if(n){var o=t&&("load"===t.type?"missing":t.type),r=t&&t.target&&t.target.src;d.message="Loading chunk "+e+" failed.\n("+o+": "+r+")",d.name="ChunkLoadError",d.type=o,d.request=r,n[1](d)}a[e]=void 0}};var f=setTimeout((function(){u({type:"timeout",target:s})}),12e4);s.onerror=s.onload=u,document.head.appendChild(s)}return Promise.all(t)},i.m=e,i.c=o,i.d=function(e,t,n){i.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:n})},i.r=function(e){"undefined"!==typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},i.t=function(e,t){if(1&t&&(e=i(e)),8&t)return e;if(4&t&&"object"===typeof e&&e&&e.__esModule)return e;var n=Object.create(null);if(i.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var o in e)i.d(n,o,function(t){return e[t]}.bind(null,o));return n},i.n=function(e){var t=e&&e.__esModule?function(){return e["default"]}:function(){return e};return i.d(t,"a",t),t},i.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},i.p="/",i.oe=function(e){throw console.error(e),e};var u=window["webpackJsonp"]=window["webpackJsonp"]||[],s=u.push.bind(u);u.push=t,u=u.slice();for(var d=0;d<u.length;d++)t(u[d]);var f=s;c.push([0,"chunk-vendors"]),n()})({0:function(e,t,n){e.exports=n("cd49")},"09bc":function(e,t,n){"use strict";n("1f34")},1:function(e,t){},"15ee":function(e,t,n){"use strict";n("5b1d")},"1f34":function(e,t,n){},"5b1d":function(e,t,n){},"8ba5":function(e,t,n){"use strict";var o=n("7a23"),r=n("bdf3"),a=n.n(r),c=function(e){return Object(o["pushScopeId"])("data-v-ee0c3588"),e=e(),Object(o["popScopeId"])(),e},l={class:"navbar navbar-expand-lg navbar-light bg-light"},i={class:"container-fluid"},u=c((function(){return Object(o["createElementVNode"])("a",{class:"navbar-brand Logo",href:"#"},[Object(o["createElementVNode"])("img",{src:a.a,style:{"max-height":"50px"},class:"img-fluid",alt:""})],-1)})),s=c((function(){return Object(o["createElementVNode"])("button",{class:"navbar-toggler",type:"button","data-bs-toggle":"collapse","data-bs-target":"#navbarSupportedContent","aria-controls":"navbarSupportedContent","aria-expanded":"false","aria-label":"Toggle navigation"},[Object(o["createElementVNode"])("span",{class:"navbar-toggler-icon"})],-1)})),d={class:"collapse navbar-collapse",id:"navbarSupportedContent"},f={class:"navbar-nav me-auto mb-2 mb-lg-0"},b={class:"nav-item"},m={class:"nav-item"},p=c((function(){return Object(o["createElementVNode"])("li",{class:"nav-item"},[Object(o["createElementVNode"])("a",{class:"nav-link",href:"#"},"Help")],-1)})),g={class:"nav-item dropdown"};function j(e,t,n,r,a,c){return Object(o["openBlock"])(),Object(o["createElementBlock"])("nav",l,[Object(o["createElementVNode"])("div",i,[u,s,Object(o["createElementVNode"])("div",d,[Object(o["createElementVNode"])("ul",f,[Object(o["createElementVNode"])("li",b,[Object(o["createElementVNode"])("a",{class:"nav-link active",onClick:t[0]||(t[0]=function(t){return e.go("/")}),"aria-current":"page",href:"#"},"Home")]),Object(o["createElementVNode"])("li",m,[Object(o["createElementVNode"])("a",{class:"nav-link",onClick:t[1]||(t[1]=function(t){return e.go("/history")})},"History")]),p,Object(o["createElementVNode"])("li",g,[Object(o["createElementVNode"])("a",{class:"nav-link",onClick:t[2]||(t[2]=function(t){return e.go("/about")})},"About us")])]),Object(o["renderSlot"])(e.$slots,"default",{class:"d-flex"},void 0,!0)])])])}var O=n("afbc"),h=(n("ab8b"),n("7b17"),Object(o["defineComponent"])({name:"Header",components:{},setup:function(){var e=Object(o["reactive"])({temp:0,drawer:!1,flag:!0,simLisValue:0,showAllData:!1,fa_data:[],keywordList:[]}),t=function(){console.log()},n=O["a"].currentRoute.value.path?O["a"].currentRoute.value.path:"/",r=function(e){O["a"].push(e)},a=function(e){O["a"].push(e)};return Object(o["onMounted"])((function(){t()})),{config:e,getPath:t,go:r,handleSelect:a,activeIndex:n}}})),v=(n("c1ca"),n("6b0d")),k=n.n(v);const y=k()(h,[["render",j],["__scopeId","data-v-ee0c3588"]]);t["a"]=y},afbc:function(e,t,n){"use strict";n("d3b7"),n("3ca3"),n("ddb0");var o=n("6c02"),r=n("7a23"),a=function(e){return Object(r["pushScopeId"])("data-v-64675157"),e=e(),Object(r["popScopeId"])(),e},c={id:"home",class:"home"},l=Object(r["createTextVNode"])("Submit"),i={id:"tool"},u={class:"grid-content slider-wrapper bg-purple",style:{"padding-right":"15px"}},s=a((function(){return Object(r["createElementVNode"])("span",{class:"demonstration",style:{"padding-right":"12px"}},"Similarity Score Threshold:",-1)})),d=a((function(){return Object(r["createElementVNode"])("span",{style:{float:"right","vertical-align":"middle","margin-right":"20px","margin-top":"4px"}},null,-1)})),f={class:"box-title"},b={key:0},m=a((function(){return Object(r["createElementVNode"])("br",null,null,-1)})),p=a((function(){return Object(r["createElementVNode"])("br",null,null,-1)})),g=[m,p],j={key:1},O={class:"bg-orange"},h={key:2,class:"bg-orange"},v={key:3,class:"bg-orange"},k=["sim","pair_id"],y={class:"box-title"},w={key:0},x=a((function(){return Object(r["createElementVNode"])("br",null,null,-1)})),C=a((function(){return Object(r["createElementVNode"])("br",null,null,-1)})),S=[x,C],V={key:1},_={class:"bg-orange"},L={key:2,class:"bg-orange"},N={key:3,class:"bg-orange"},E=["sim","pair_id"];function B(e,t,n,o,a,m){var p=Object(r["resolveComponent"])("el-option"),x=Object(r["resolveComponent"])("el-select"),C=Object(r["resolveComponent"])("el-form-item"),B=Object(r["resolveComponent"])("el-button"),T=Object(r["resolveComponent"])("el-form"),F=Object(r["resolveComponent"])("Header"),A=Object(r["resolveComponent"])("el-slider"),I=Object(r["resolveComponent"])("el-col"),D=Object(r["resolveComponent"])("download"),H=Object(r["resolveComponent"])("el-icon"),M=Object(r["resolveComponent"])("el-tooltip"),J=Object(r["resolveComponent"])("data-line"),q=Object(r["resolveComponent"])("el-row"),P=Object(r["resolveComponent"])("el-main"),U=Object(r["resolveComponent"])("Footer");return Object(r["openBlock"])(),Object(r["createElementBlock"])("div",c,[Object(r["createVNode"])(F,null,{default:Object(r["withCtx"])((function(){return[Object(r["createVNode"])(T,{inline:!0,model:e.config.ruleForm,class:"form-inline"},{default:Object(r["withCtx"])((function(){return[Object(r["createVNode"])(C,null,{default:Object(r["withCtx"])((function(){return[Object(r["createVNode"])(x,{modelValue:e.config.ruleForm.keyword,"onUpdate:modelValue":t[0]||(t[0]=function(t){return e.config.ruleForm.keyword=t}),filterable:"",remote:"","reserve-keyword":"",placeholder:"Please enter a keyword","remote-method":e.querySearchAsync,loading:e.config.loading},{default:Object(r["withCtx"])((function(){return[(Object(r["openBlock"])(!0),Object(r["createElementBlock"])(r["Fragment"],null,Object(r["renderList"])(e.config.keywordList,(function(e){return Object(r["openBlock"])(),Object(r["createBlock"])(p,{key:e,label:e,value:e},null,8,["label","value"])})),128))]})),_:1},8,["modelValue","remote-method","loading"])]})),_:1}),Object(r["createVNode"])(C,null,{default:Object(r["withCtx"])((function(){return[Object(r["createVNode"])(x,{modelValue:e.config.ruleForm.language1,"onUpdate:modelValue":t[1]||(t[1]=function(t){return e.config.ruleForm.language1=t}),onChange:e.changeLang1,filterable:"",placeholder:"language1","fit-input-width":"",clearable:""},{default:Object(r["withCtx"])((function(){return[(Object(r["openBlock"])(!0),Object(r["createElementBlock"])(r["Fragment"],null,Object(r["renderList"])(e.config.languageList,(function(e){return Object(r["openBlock"])(),Object(r["createBlock"])(p,{key:e[0],label:e[0]+"-"+e[1],value:e[0]},null,8,["label","value"])})),128))]})),_:1},8,["modelValue","onChange"])]})),_:1}),Object(r["createVNode"])(C,null,{default:Object(r["withCtx"])((function(){return[Object(r["createVNode"])(x,{modelValue:e.config.ruleForm.language2,"onUpdate:modelValue":t[2]||(t[2]=function(t){return e.config.ruleForm.language2=t}),onChange:e.changeLang2,placeholder:"language2","fit-input-width":"",clearable:""},{default:Object(r["withCtx"])((function(){return[(Object(r["openBlock"])(!0),Object(r["createElementBlock"])(r["Fragment"],null,Object(r["renderList"])(e.config.languageList,(function(e){return Object(r["openBlock"])(),Object(r["createBlock"])(p,{key:e[0],label:e[0]+"-"+e[1],value:e[0]},null,8,["label","value"])})),128))]})),_:1},8,["modelValue","onChange"])]})),_:1}),Object(r["createVNode"])(C,null,{default:Object(r["withCtx"])((function(){return[Object(r["createVNode"])(B,{type:"primary",onClick:t[3]||(t[3]=function(t){return e.submitForm("ruleForm")}),plain:""},{default:Object(r["withCtx"])((function(){return[l]})),_:1})]})),_:1})]})),_:1},8,["model"])]})),_:1}),Object(r["createVNode"])(P,null,{default:Object(r["withCtx"])((function(){return[Object(r["createElementVNode"])("div",i,[Object(r["createVNode"])(q,{gutter:8,style:{"align-items":"center"}},{default:Object(r["withCtx"])((function(){return[Object(r["createVNode"])(I,{span:8},{default:Object(r["withCtx"])((function(){return[Object(r["createElementVNode"])("div",u,[s,Object(r["createVNode"])(A,{max:e.config.maxSim,min:e.config.minSim,modelValue:e.config.value1,"onUpdate:modelValue":t[4]||(t[4]=function(t){return e.config.value1=t}),"format-tooltip":e.formatTooltip,step:.01,"show-stops":""},null,8,["max","min","modelValue","format-tooltip","step"])])]})),_:1}),Object(r["createVNode"])(I,{span:14},{default:Object(r["withCtx"])((function(){return[Object(r["createVNode"])(M,{class:"box-item",effect:"dark",content:"Download",placement:"top-start"},{default:Object(r["withCtx"])((function(){return[Object(r["createVNode"])(H,{style:{float:"right","margin-right":"20px","margin-left":"10px"},class:"icon-self el-icon-download",onClick:e.exportExcel},{default:Object(r["withCtx"])((function(){return[Object(r["createVNode"])(D)]})),_:1},8,["onClick"])]})),_:1}),Object(r["createVNode"])(M,{class:"box-item",effect:"dark",content:"Show All Data",placement:"top-start"},{default:Object(r["withCtx"])((function(){return[Object(r["createVNode"])(H,{style:{float:"right"},class:Object(r["normalizeClass"])([{"bg-blue":e.config.showAllData},"icon-self el-icon-data-line"]),onClick:e.showAll},{default:Object(r["withCtx"])((function(){return[Object(r["createVNode"])(J)]})),_:1},8,["class","onClick"])]})),_:1}),d]})),_:1})]})),_:1})]),Object(r["createVNode"])(q,{class:"main"},{default:Object(r["withCtx"])((function(){return[Object(r["createVNode"])(I,{span:12},{default:Object(r["withCtx"])((function(){return[Object(r["createElementVNode"])("div",f,Object(r["toDisplayString"])(e.config.Text1)+" ----------"+Object(r["toDisplayString"])("similarly: "+Math.round(100*e.config.simLisValue)/100),1),Object(r["createElementVNode"])("div",{id:"text1",class:"grid-content bg-purple box-text",ref:"text1",onMouseover:t[9]||(t[9]=function(t){return e.changeFlag(!1)})},[(Object(r["openBlock"])(!0),Object(r["createElementBlock"])(r["Fragment"],null,Object(r["renderList"])(e.config.fa_data.ST,(function(n){return Object(r["openBlock"])(),Object(r["createElementBlock"])("span",{key:n,onContextmenu:t[8]||(t[8]=Object(r["withModifiers"])((function(t){return e.getTranlate("left",t)}),["prevent"]))},["<br>"===n.content?(Object(r["openBlock"])(),Object(r["createElementBlock"])("div",b,g)):"=="==n.content.substr(-2,2)?(Object(r["openBlock"])(),Object(r["createElementBlock"])("p",j,[Object(r["createElementVNode"])("b",O,Object(r["toDisplayString"])(n.content),1)])):-1===n.pair_id?(Object(r["openBlock"])(),Object(r["createElementBlock"])("b",h,Object(r["toDisplayString"])(n.content),1)):n.sim<e.config.value1&&n.sim>0?(Object(r["openBlock"])(),Object(r["createElementBlock"])("b",v,Object(r["toDisplayString"])(n.content),1)):(Object(r["openBlock"])(),Object(r["createElementBlock"])("b",{key:4,onClick:t[5]||(t[5]=function(t){return e.doCopy(t,"left")}),class:Object(r["normalizeClass"])({"bg-demo":e.config.showAllData}),sim:n.sim,pair_id:n.pair_id,onMouseover:t[6]||(t[6]=function(t){return e.wikiMouseover(t)}),onMouseleave:t[7]||(t[7]=function(t){return e.wikiMouseLeave(t)})},[Object(r["createTextVNode"])(Object(r["toDisplayString"])(n.content),1),Object(r["withDirectives"])(Object(r["createElementVNode"])("b",{class:"num_tag"},Object(r["toDisplayString"])(n.pair_id),513),[[r["vShow"],e.config.showAllData]])],42,k))],32)})),128))],544)]})),_:1}),Object(r["createVNode"])(I,{span:12},{default:Object(r["withCtx"])((function(){return[Object(r["createElementVNode"])("div",y,Object(r["toDisplayString"])(e.config.Text2),1),Object(r["createElementVNode"])("div",{id:"text2",class:"grid-content bg-purple-light box-text",ref:"text2",onMouseover:t[14]||(t[14]=function(t){return e.changeFlag(!0)})},[(Object(r["openBlock"])(!0),Object(r["createElementBlock"])(r["Fragment"],null,Object(r["renderList"])(e.config.fa_data.TT,(function(n){return Object(r["openBlock"])(),Object(r["createElementBlock"])("span",{key:n,onContextmenu:t[13]||(t[13]=Object(r["withModifiers"])((function(t){return e.getTranlate("right",t)}),["prevent"]))},["<br>"==n.content?(Object(r["openBlock"])(),Object(r["createElementBlock"])("div",w,S)):"=="==n.content.substr(-2,2)?(Object(r["openBlock"])(),Object(r["createElementBlock"])("p",V,[Object(r["createElementVNode"])("b",_,Object(r["toDisplayString"])(n.content),1)])):-1===n.pair_id?(Object(r["openBlock"])(),Object(r["createElementBlock"])("b",L,Object(r["toDisplayString"])(n.content),1)):n.sim<e.config.value1?(Object(r["openBlock"])(),Object(r["createElementBlock"])("b",N,Object(r["toDisplayString"])(n.content),1)):(Object(r["openBlock"])(),Object(r["createElementBlock"])("b",{key:4,onClick:t[10]||(t[10]=function(t){return e.doCopy(t,"right")}),class:Object(r["normalizeClass"])({"bg-demo":e.config.showAllData}),sim:n.sim,pair_id:n.pair_id,onMouseover:t[11]||(t[11]=function(t){return e.wikiMouseover(t)}),onMouseleave:t[12]||(t[12]=function(t){return e.wikiMouseLeave(t)})},[Object(r["createTextVNode"])(Object(r["toDisplayString"])(n.content),1),Object(r["withDirectives"])(Object(r["createElementVNode"])("b",{class:"num_tag"},Object(r["toDisplayString"])(n.pair_id),513),[[r["vShow"],e.config.showAllData]])],42,E))],32)})),128))],544)]})),_:1})]})),_:1})]})),_:1}),Object(r["createVNode"])(U)])}var T=n("b85c"),F=(n("b680"),n("25f0"),n("b64b"),n("99af"),n("159b"),n("2b3d"),n("9861"),n("6821")),A=n.n(F),I=n("bc3a"),D=n.n(I),H=n("3ef4"),M="";function J(e){var t="";if(e){for(var n in e)t+="&"+encodeURIComponent(n)+"="+encodeURIComponent(e[n]);t.length>0&&(t=t.substring(1))}return t}D.a.defaults.timeout=5e5,D.a.defaults.baseURL="/baseApi",D.a.interceptors.response.use((function(e){console.log(e);var t=e.data,n=t.message;if(console.log(e),"blob"==e.request.responseType)return e;switch(t.code){case 401:n||(n="登录信息已失效，请重新登录！"),H["a"].error(n);break;case 403:n||(n="没有操作权限！"),H["a"].error(n);break;case 500:n||(n="服务器发生未知错误！"),H["a"].error(n);break;default:break}return t}),(function(e){return e.response?H["a"].error(e.response.status+"："+e.response.statusText):H["a"].error(e.message),Promise.reject(e)}));var q={get:function(e,t){return D()({method:"get",url:"".concat(M).concat(e),params:t,headers:{"Content-Type":"application/x-www-form-urlencoded"}})},blob:function(e,t){return D()({method:"post",url:"".concat(M).concat(e),params:t,headers:{"Content-Type":"application/json;charset=utf-8"},responseType:"blob"})},post:function(e,t){return D()({method:"post",url:"".concat(M).concat(e),data:t,transformRequest:[J],headers:{"Content-Type":"application/x-www-form-urlencoded"}})},put:function(e,t){return D()({method:"put",url:"".concat(M).concat(e),data:t,transformRequest:[J],headers:{"Content-Type":"application/x-www-form-urlencoded"}})},delete:function(e,t){return D()({method:"delete",url:"".concat(M).concat(e),data:t,headers:{}})},postByJson:function(e,t){return D()({method:"post",url:"".concat(M).concat(e),data:t,headers:{"Content-Type":"application/json;charset=utf-8"}})},putByJson:function(e,t){return D()({method:"put",url:"".concat(M).concat(e),data:t,headers:{"Content-Type":"application/json"}})},getWithoutAuth:function(e,t){return D()({method:"get",url:"".concat(M).concat(e),data:t})},postWithoutAuth:function(e,t){return D()({method:"post",url:"".concat(M).concat(e),data:t,transformRequest:[J],headers:{"Content-Type":"application/json"}})}},P=q,U=(n("e9c4"),n("4328")),R=n.n(U),z=D.a.create({baseURL:"/trans",timeout:5e3});D.a.defaults.headers.post["Content-Type"]="application/x-www=-form-urlencoded";var K=function(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{},t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:"application/x-www-form-urlencoded";return"application/x-www-form-urlencoded"===t?R.a.stringify(e):"application/json"===t?JSON.stringify(e):e};function W(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{};return new Promise((function(n,o){z.post(e,K(t)).then((function(e){n(e.data)})).catch((function(e){o(e)}))}))}var $=function(e,t){return W("/trans/vip/translate"+t,e)},G=function(e){return P.postByJson("/get_keyword_options",e)},Q=function(e){return P.postByJson("/get_wiki_title_options",e)},X=function(e){return P.postByJson("/analyze",e)},Y=function(e){return P.blob("/export_to_excel",e)},Z=n("2295"),ee=n("5502"),te=n("8ba5"),ne=n("c329"),oe=Object(r["defineComponent"])({name:"Home",components:{Footer:ne["a"],Header:te["a"]},setup:function(){var e=Object(r["reactive"])({routeData:[],temp:0,drawer:!1,Text1:"ST",Text2:"TT",maxSim:10,minSim:0,flag:!0,simLisValue:0,value1:0,showAllData:!1,fa_data:[],simListOn:{},simListOff:{},languageList:[["en","Steve Jobs"]],language1List:[["en","Steve Jobs"]],language2List:[["zh","史蒂夫·乔布斯l"]],translatedLanguage:"",ruleForm:{keyword:"steve jobs",language1:"en",language2:"zh",languageText1:"Steve Jobs",languageText2:"史蒂夫·乔布斯"},rules:{keyword:[{required:!0,message:"please input keywords",trigger:"blur"}],language1:[{required:!0,message:"please select",trigger:"blur"}],language2:[{required:!0,message:"please select",trigger:"blur"}]},keywordList:[]}),t=Object(ee["b"])(),n=(Object(o["c"])(),function(){e.showAllData=!e.showAllData}),a=function(e){return e.toFixed(2)},c=function(){var n={keyword:e.ruleForm.keyword,language_code1:e.ruleForm.language1,wiki_title1:e.ruleForm.languageText1,language_code2:e.ruleForm.language2,wiki_title2:e.ruleForm.languageText2};if("steve jobs"!==n.keyword){var o=t.getters.getHistList?t.getters.getHistList:[],r=n;r["res"]={},r["date"]=(new Date).toLocaleString(),r["id"]=Date.now()+Math.ceil(1e3*Math.random()).toString(),o.push(r),t.commit("setHistList",o)}X(n).then((function(t){if(t.success){var n=Object.keys(t.result);e.fa_data=t.result,e.Text1=n[0],e.Text2=n[1],e.maxSim=t.result.maxSim,e.minSim=t.result.minSim}else H["a"].error(t.message)}))},l=function(t,n){var o="demo",r=n.target.firstChild.textContent,a="left"===t?e.ruleForm.language1:e.ruleForm.language2,c="left"===t?e.ruleForm.language2:e.ruleForm.language1,l=A()("20210620000867906".concat(r).concat(o,"0NNfT6b27iPaMVw9hAgp")),i="20210620000867906",u={q:r,from:a,to:c,appid:"20210620000867906",salt:o,sign:l},s="?q=".concat(r,"&from=").concat(a,"&to=").concat(c,"&appid=").concat(i,"&salt=").concat(o,"&sign=").concat(l);$(u,s).then((function(t){e.translatedLanguage=t.trans_result[0].dst,Object(Z["a"])({title:"Translation",message:e.translatedLanguage,duration:6e3})}))},i=function(e){se.push(e)},u=(Object(r["ref"])([]),function(t,n){var o={query:t};G(o).then((function(t){e.keywordList=t.result.keyword_options}))}),s=function(t){var n=t.target.getAttribute("pair_id").toString();e.simLisValue=t.target.getAttribute("sim").toString(),document.querySelectorAll('[pair_id="'+n+'"]').forEach((function(e){e.classList.add("bg_blue")}))},d=function(t){document.querySelectorAll("b").forEach((function(e){e.classList.remove("bg_blue")})),e.simLisValue=0},f=function(t){e.flag=t},b=function(){console.log(1)},m=function(){console.log(1)},p=function(t){Q({keyword:t}).then((function(t){e.ruleForm.language1="",e.ruleForm.language2="",e.languageList=t.result.wiki_title_options}))},g=function(e,t){if("left"===t){var n=e.target.getAttribute("pair_id").toString(),o=document.querySelectorAll('[pair_id="'+n+'"]'),r=o[1]?o[1].offsetTop:0,a=document.getElementById("text2");a&&r&&(a.scrollTop=r-60)}else{var c=e.target.getAttribute("pair_id").toString(),l=document.querySelectorAll('[pair_id="'+c+'"]'),i=l[0]?l[0].offsetTop:0,u=document.getElementById("text1");u&&i&&(u.scrollTop=i-60)}},j=function(t){var n,o=e.languageList,r=Object(T["a"])(o);try{for(r.s();!(n=r.n()).done;){var a=n.value;if(a[0]===t){e.ruleForm.languageText1=a[1];break}}}catch(c){r.e(c)}finally{r.f()}},O=function(){Y({keyword:e.ruleForm.keyword,language1:e.ruleForm.language1,language2:e.ruleForm.language2}).then((function(e){var t=window.URL.createObjectURL(new Blob([e.data],{type:"application/vnd.ms-excel"})),n=document.createElement("a");n.download="export.xlsx",n.href=t,n.click()}))},h=function(t){var n,o=e.languageList,r=Object(T["a"])(o);try{for(r.s();!(n=r.n()).done;){var a=n.value;if(a[0]===t){e.ruleForm.languageText2=a[1];break}}}catch(c){r.e(c)}finally{r.f()}};return Object(r["watch"])((function(){return e.ruleForm.keyword}),(function(e){p(e)})),Object(r["onMounted"])((function(){c()})),{showAll:n,submitForm:c,getTranlate:l,changeFlag:f,sysHandleScroll:b,exterHandleScroll:m,wikiMouseover:s,wikiMouseLeave:d,querySearchAsync:u,config:e,go:i,doCopy:g,changeLang1:j,changeLang2:h,exportExcel:O,formatTooltip:a}}}),re=(n("09bc"),n("6b0d")),ae=n.n(re);const ce=ae()(oe,[["render",B],["__scopeId","data-v-64675157"]]);var le=ce,ie=[{path:"/",name:"Home",component:le},{path:"/about",name:"About",component:function(){return n.e("chunk-4baa741f").then(n.bind(null,"f820"))}},{path:"/help",name:"Help",component:function(){return n.e("chunk-2d216dc7").then(n.bind(null,"c3ef"))}},{path:"/history",name:"History",component:function(){return n.e("chunk-2d2259e5").then(n.bind(null,"e4bb"))}}],ue=Object(o["a"])({history:Object(o["b"])("/"),routes:ie}),se=t["a"]=ue},bdf3:function(e,t,n){e.exports=n.p+"img/logo3.adde1892.png"},c1ca:function(e,t,n){"use strict";n("cfd5")},c329:function(e,t,n){"use strict";var o=n("7a23"),r=function(e){return Object(o["pushScopeId"])("data-v-be089ee2"),e=e(),Object(o["popScopeId"])(),e},a=r((function(){return Object(o["createElementVNode"])("p",null,"Copyright © 2021 Centre for Translation, HKBU",-1)})),c=r((function(){return Object(o["createElementVNode"])("p",null,"Disclaimer | Privacy Statement",-1)}));function l(e,t,n,r,l,i){var u=Object(o["resolveComponent"])("el-footer");return Object(o["openBlock"])(),Object(o["createBlock"])(u,null,{default:Object(o["withCtx"])((function(){return[a,c]})),_:1})}var i={name:"Footer"},u=(n("15ee"),n("6b0d")),s=n.n(u);const d=s()(i,[["render",l],["__scopeId","data-v-be089ee2"]]);t["a"]=d},cd49:function(e,t,n){"use strict";n.r(t);n("e260"),n("e6cf"),n("cca6"),n("a79d");var o=n("7a23"),r=n("c3a1");n("7437");function a(e,t){var n=Object(o["resolveComponent"])("router-view");return Object(o["openBlock"])(),Object(o["createBlock"])(n)}var c=n("6b0d"),l=n.n(c);const i={},u=l()(i,[["render",a]]);var s=u,d=n("afbc"),f=(n("fb6a"),n("a434"),n("5502")),b=n("53ca"),m=(n("498a"),n("e9c4"),{clearLocalItem:function(){window.localStorage.clear()},setLocalItem:function(e,t){e&&""!=(e=e.trim())&&(t&&"object"==Object(b["a"])(t)&&(t=JSON.stringify(t)),window.localStorage.setItem(e,t))},removeLocalItem:function(e){e&&""!=(e=e.trim())&&window.localStorage.removeItem(e)},getLocalItem:function(e){return e&&""!=(e=e.trim())?window.localStorage.getItem(e):""},getLocalJsonItem:function(e){if(!e||""==(e=e.trim()))return null;var t=window.localStorage.getItem(e);return t&&""!=t?JSON.parse(t):null},setSessionItem:function(e,t){e&&""!=(e=e.trim())&&(t&&"object"==Object(b["a"])(t)&&(t=JSON.stringify(t)),sessionStorage.setItem(e,t))},getSessionJsonItem:function(e){if(!e||""==(e=e.trim()))return null;var t=sessionStorage.getItem(e);return t&&""!=t?JSON.parse(t):null}}),p=m,g=Object(f["a"])({state:{HistList:[],UnSolveList:[]},mutations:{setHistList:function(e,t){e.HistList=t,e.HistList.length>10?p.setLocalItem("HistList",e.HistList.slice(-10)):p.setLocalItem("HistList",e.HistList)}},actions:{delHistList:function(e,t){var n=p.getLocalJsonItem("HistList"),o=!1;for(var r in n)if(n[r]["id"]===t){n.splice(r,1);o=!0,p.setLocalItem("HistList",n);break}return o}},modules:{},getters:{getHistList:function(){return p.getLocalJsonItem("HistList")?p.getLocalJsonItem("HistList").reverse():[]}}}),j=n("c848"),O=Object(o["createApp"])(s);for(var h in j)O.component(h,j[h]);O.use(r["a"]),O.use(g).use(d["a"]).mount("#app")},cfd5:function(e,t,n){}});