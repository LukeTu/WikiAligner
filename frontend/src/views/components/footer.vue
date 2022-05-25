<template>
  <el-footer>
      <p>Copyright © 2021 Centre for Translation, HKBU</p>
      <p>Disclaimer | Privacy Statement</p>
    </el-footer>
</template>

<script>
export default {
  name: "Footer"
}
</script>

<style scoped>
.el-footer {
  width: 100%;
  height: 60px; /* footer的高度一定要是固定值*/
  position: absolute;
  bottom: 0;
  left: 0;
  text-align: center;
  color: #909399
}
</style>