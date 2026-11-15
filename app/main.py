from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import uuid

from app.core.processor import VideoProcessor
from app import database

app = FastAPI(title="智能视频监控与决策分析平台 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

Path("outputs").mkdir(exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

database.init_db()
print("正在启动系统，准备加载 YOLO 模型...")
processor = VideoProcessor()


def run_video_processing(task_id: str, input_path: str, original_filename: str):
    try:
        result_data = processor.process(input_path=input_path, output_dir="outputs")
        if result_data:
            video_filename = Path(result_data["video_path"]).name
            video_url = f"/outputs/{video_filename}"
            database.save_task(
                task_id, original_filename, "completed",
                result_data["max_persons"], result_data["total_intrusions"], video_url
            )
            for alarm in result_data["alarm_records"]:
                database.save_alarm(
                    task_id, alarm["frame_idx"], alarm["time_sec"], alarm["snapshot_url"]
                )
            print(f"任务 {task_id} 处理完成并入库！")
        else:
            database.save_task(task_id, original_filename, "failed")
    except Exception as e:
        print(f"处理出错: {e}")
        database.save_task(task_id, original_filename, "failed")


@app.post("/api/upload", summary="上传视频并开始分析")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(('.mp4', '.avi')):
        raise HTTPException(status_code=400, detail="只支持 mp4 或 avi 格式")

    task_id = str(uuid.uuid4())[:8]
    input_path = Path("data") / f"{task_id}_{file.filename}"
    Path("data").mkdir(exist_ok=True)

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    database.save_task(task_id, file.filename, "processing")
    background_tasks.add_task(run_video_processing, task_id, str(input_path), file.filename)
    return {"message": "上传成功", "task_id": task_id}


@app.get("/api/status/{task_id}", summary="查询任务进度")
async def get_status(task_id: str):
    status_data = database.get_task_status(task_id)
    if not status_data:
        raise HTTPException(status_code=404, detail="找不到该任务")
    return {"task_id": task_id, **status_data}


@app.get("/api/alarms", summary="查询所有告警记录")
async def get_alarms():
    alarms = database.get_all_alarms()
    return {"total": len(alarms), "data": alarms}


@app.get("/api/stats/overview", summary="获取总览统计数据")
async def get_overview():
    return database.get_overview_stats()

@app.get("/api/stats/trend", summary="获取图表趋势数据")
async def get_trend():
    return database.get_trend_data()
#智能体分析报告接口
@app.get("/api/report", summary="获取智能分析报告")
async def get_report():
    data = database.get_agent_analysis_data()

    # 改用 HTML 标签排版
    html_report = "<div style='font-family: sans-serif;'>"

    if data["total_videos"] == 0:
        return {"report": "<h3>智能安防分析报告</h3><p>系统暂无监控数据，请先上传视频进行分析。</p>"}

    # 1. 总体态势
    html_report += "<h3>智能安防分析报告</h3>"
    html_report += "<h4>1. 总体态势</h4>"
    html_report += f"<p>系统今日共处理了 <strong style='color:#3b82f6;'>{data['total_videos']}</strong> 段监控视频，累计发生 <strong style='color:#ef4444;'>{data['total_alarms']}</strong> 次区域入侵告警。</p>"

    # 2. 风险定位
    html_report += "<h4>2. 风险定位</h4>"
    if data["total_alarms"] > 10:
        html_report += f"<p><strong style='color:#ef4444;'>高风险预警</strong>：当前系统安全态势严峻。特别是批次为 <code>{data['high_risk_task']}</code> 的监控任务，爆发了 {data['high_risk_count']} 次入侵。</p>"
    elif data["total_alarms"] > 0:
        html_report += f"<p>整体安全态势平稳，但在批次 <code>{data['high_risk_task']}</code> 中发现了 {data['high_risk_count']} 次违规行为，需引起注意。</p>"
    else:
        html_report += "<p>态势极度良好，所有区域均未发现人员违规入侵。</p>"

    # 3. 行动建议
    html_report += "<h4>3. 决策与行动建议</h4>"
    html_report += "<ul style='padding-left: 20px; line-height: 1.8;'>"
    if data["total_alarms"] > 10:
        html_report += "<li><strong>立即行动</strong>：建议安保人员立刻前往高频告警区域进行现场巡查。</li>"
        html_report += "<li><strong>系统调整</strong>：检查该区域的物理围挡是否损坏，或在网页设置中将该区域风险等级调高。</li>"
    elif data["total_alarms"] > 0:
        html_report += "<li><strong>日常巡检</strong>：建议在每日交接班时，复查该批次的告警截图，确认是人员误闯还是系统误报。</li>"
    else:
        html_report += "<li>保持现有监控策略，维持定期巡检即可。</li>"
    html_report += "</ul></div>"

    return {"report": html_report}

@app.get("/")
def home():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/web/")