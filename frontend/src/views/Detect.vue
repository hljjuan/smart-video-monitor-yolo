<template>
  <div>
    <div class="header-title">视频智能解析</div>
    <div class="card">
      <el-upload
        drag action="#" :auto-upload="false" :show-file-list="false" :on-change="handleFileChange"
        style="border: 2px dashed #DCDFE6; border-radius: 8px; background: #fafafa;"
      >
        <div style="font-size: 40px; margin-bottom: 10px; color: #c0c4cc;">☁️</div>
        <div style="color: #606266;">点击或拖拽视频至此区域上传</div>
      </el-upload>

      <div v-if="selectedFile" style="margin-top: 20px; display: flex; justify-content: space-between; align-items: center; background: #f4f4f5; padding: 12px 20px; border-radius: 8px;">
        <span style="color: #303133;">📄 {{ selectedFile.name }}</span>
        <el-button type="primary" @click="upload" :loading="loading">开始智能分析</el-button>
      </div>
    </div>

    <div class="card" v-if="videoUrl">
      <div style="color: #67C23A; margin-bottom: 15px; font-weight: bold;">✅ 解析完成</div>
      <video :src="videoUrl" controls style="width: 100%; border-radius: 8px; border: 1px solid #ebeef5;" autoplay></video>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const selectedFile = ref(null)
const loading = ref(false)
const videoUrl = ref('')

const handleFileChange = (file) => { selectedFile.value = file.raw }

const upload = async () => {
  if (!selectedFile.value) return
  loading.value = true
  videoUrl.value = ''
  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const res = await axios.post('/api/upload', formData)
    const taskId = res.data.task_id
    ElMessage.success('上传成功，后台 AI 处理中...')

    const timer = setInterval(async () => {
      try {
        const statusRes = await axios.get(`/api/status/${taskId}`)
        if (statusRes.data.status === 'completed') {
          clearInterval(timer)
          loading.value = false
          videoUrl.value = statusRes.data.video_url + "?t=" + new Date().getTime()
          ElMessage.success('分析完成！')
        }
      } catch(e) {}
    }, 3000)
  } catch (e) {
    loading.value = false
    ElMessage.error('上传失败')
  }
}
</script>