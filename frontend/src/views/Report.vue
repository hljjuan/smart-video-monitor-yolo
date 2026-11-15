<template>
  <div>
    <div class="header-title">智能决策分析</div>
    <div class="card">
      <div style="display: flex; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #ebeef5;">
        <div style="width: 40px; height: 40px; background: #ecf5ff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; margin-right: 15px; color: #409EFF;">🤖</div>
        <div>
          <div style="font-weight: bold; font-size: 18px; color: #303133;">AI 安防分析专家</div>
          <div style="color: #909399; font-size: 13px;">基于当前数据库实时数据生成报告</div>
        </div>
      </div>

      <div v-if="loading" style="color: #409EFF; text-align: center; padding: 40px;">
        AI 正在分析历史数据，生成决策建议...
      </div>

      <div
        v-else
        v-html="reportContent"
        style="line-height: 1.8; color: #303133; font-size: 15px; background: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #ebeef5;">
      </div>

      <el-button type="primary" style="margin-top: 20px;" @click="loadReport" :loading="loading">
        重新生成分析报告
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const reportContent = ref('')
const loading = ref(false)

const loadReport = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/report')
    reportContent.value = res.data.report
  } catch (e) {
    reportContent.value = "<span style='color: #F56C6C;'>生成报告失败，请检查后端服务是否正常运行。</span>"
  } finally {
    loading.value = false
  }
}

onMounted(() => loadReport())
</script>