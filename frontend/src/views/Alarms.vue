<template>
  <div>
    <div class="header-title" style="display: flex; justify-content: space-between; align-items: center;">
      安全告警中心
      <el-button type="primary" plain @click="loadData" :loading="loading">刷新数据</el-button>
    </div>
    <div class="card">
      <el-table :data="alarms" style="width: 100%" v-loading="loading" row-key="id" stripe>
        <el-table-column prop="id" label="告警ID" width="100" align="center" />
        <el-table-column prop="task_id" label="任务批次" width="150" align="center" />
        <el-table-column prop="time_sec" label="视频内时间(秒)" width="150" align="center" />
        <el-table-column label="现场抓拍" align="center">
          <template #default="scope">
            <el-image
              style="width: 120px; height: 68px; border-radius: 6px; border: 1px solid #ebeef5; cursor: pointer;"
              :src="scope.row.snapshot_url"
              :preview-src-list="[scope.row.snapshot_url]"
              :preview-teleported="true"
              fit="cover"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="入库时间" align="center" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const alarms = ref([])
const loading = ref(false)

const loadData = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/alarms')
    alarms.value = res.data.data
  } catch(e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}
onMounted(() => loadData())
</script>


<style>
.el-image-viewer__wrapper {
  z-index: 9999999 !important;
}
.el-image-viewer__mask {
  background: #000 !important;
  opacity: 0.85 !important;
}
</style>