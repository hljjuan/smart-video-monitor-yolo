<template>
  <div class="app-container">
    <!-- 侧边栏 -->
    <div class="sidebar">
      <div class="logo">智能监控平台</div>
      <el-menu :default-active="$route.path" router background-color="#ffffff" text-color="#606266" active-text-color="#409EFF" style="border-right: none;">
        <el-menu-item index="/overview">数据总览</el-menu-item>
        <el-menu-item index="/detect">视频检测</el-menu-item>
        <el-menu-item index="/alarms">告警中心</el-menu-item>
        <el-menu-item index="/report">智能决策</el-menu-item>
      </el-menu>
    </div>

    <!-- 右侧内容区 -->
    <div class="main-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<style>
body { margin: 0; background-color: #f0f2f5; color: #303133; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
.app-container { display: flex; height: 100vh; }
/* 侧边栏纯白，右侧加浅阴影 */
.sidebar { width: 240px; background: #ffffff; box-shadow: 2px 0 8px 0 rgba(29,35,41,.05); z-index: 10; }
.logo { height: 60px; line-height: 60px; text-align: center; font-weight: bold; font-size: 20px; color: #409EFF; letter-spacing: 1px; border-bottom: 1px solid #f0f0f0; }
.main-content { flex: 1; padding: 24px; overflow-y: auto; }
.header-title { font-size: 22px; font-weight: bold; margin-bottom: 24px; color: #303133; }
/* 纯白卡片 */
.card { background: #ffffff; border-radius: 8px; padding: 24px; margin-bottom: 24px; box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05); border: 1px solid #ebeef5; }
</style>