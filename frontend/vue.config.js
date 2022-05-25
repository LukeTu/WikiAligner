module.exports = {
	lintOnSave: false,
	productionSourceMap:false,
	// api测试代理
	devServer: {
		disableHostCheck: true,
		proxy: {
			'/baseApi': {
				target: 'http://127.0.0.1:5000/',
				changeOrigin: true,
				pathRewrite: {
					'^/baseApi': '/api'
				},
			},
			'/trans': {
				target: 'https://fanyi-api.baidu.com/',
				changeOrigin: true,
				pathRewrite: {
				  '^/trans': '/api'
				},
			}
		},
	},
}