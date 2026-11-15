<template>
  <div>
    <div class="header-title">全局态势总览</div>

    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px;">
      <div class="card">
        <div style="color: #909399; margin-bottom: 10px;">累计处理视频</div>
        <div style="font-size: 48px; color: #409EFF; font-weight: bold; font-family: monospace;">{{ stats.total_videos }}</div>
      </div>
      <div class="card">
        <div style="color: #909399; margin-bottom: 10px;">累计安全告警</div>
        <div style="font-size: 48px; color: #F56C6C; font-weight: bold; font-family: monospace;">{{ stats.total_alarms }}</div>
      </div>
      <div class="card">
        <div style="color: #909399; margin-bottom: 10px;">历史最高客流(人)</div>
        <div style="font-size: 48px; color: #67C23A; font-weight: bold; font-family: monospace;">{{ stats.max_persons }}</div>
      </div>
    </div>

    <div class="card" style="margin-top: 24px;">
      <div ref="chartRef" style="height: 380px; width: 100%;"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const stats = ref({ total_videos: 0, total_alarms: 0, max_persons: 0 })
const chartRef = ref(null)

onMounted(async () => {
  const chart = echarts.init(chartRef.value)
  chart.showLoading({ text: '数据加载中...', color: '#409EFF' })

  try {
    const resStats = await axios.get('/api/stats/overview')
    stats.value = resStats.data

    const resTrend = await axios.get('/api/stats/trend')
    const trendData = resTrend.data

    chart.hideLoading()
    chart.setOption({
      backgroundColor: 'transparent',
      title: { text: '近7日处理视频与告警趋势', textStyle: { color: '#303133', fontSize: 16 }, left: 'center', top: 10 },
      tooltip: { trigger: 'axis' },
      legend: { data: ['处理视频数', '告警次数'], textStyle: { color: '#606266' }, top: 40 },
      grid: { left: '4%', right: '4%', bottom: '5%', top: '25%', containLabel: true },
      xAxis: {
        type: 'category', data: trendData.dates,
        axisLabel: { color: '#606266' }, axisLine: { lineStyle: { color: '#DCDFE6' } }
      },
      yAxis: {
        type: 'value', axisLabel: { color: '#606266' },
        splitLine: { lineStyle: { color: '#EBEEF5' } }
      },
      series: [
        {
          name: '处理视频数', type: 'line', smooth: true, data: trendData.video_counts,
          itemStyle: { color: '#409EFF' }, lineStyle: { width: 3 },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(64, 158, 255, 0.4)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
            ])
          }
        },
        {
          name: '告警次数', type: 'bar', data: trendData.alarm_counts,
          itemStyle: { color: '#F56C6C', borderRadius: [4, 4, 0, 0] }, barWidth: '30%'
        }
      ]
    })
  } catch (e) {
    chart.hideLoading()
  }
})
</script>