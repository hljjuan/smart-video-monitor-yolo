import sqlite3
from pathlib import Path

DB_PATH = Path("data/monitor.db")
def init_db():
    """初始化数据库，建两张表：任务表 和 告警表"""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            filename TEXT,
            status TEXT,
            max_persons INTEGER,
            total_intrusions INTEGER,
            video_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alarms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT,
            frame_idx INTEGER,
            time_sec REAL,
            snapshot_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def save_task(task_id, filename, status, max_persons=0, total_intrusions=0, video_url=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO tasks (task_id, filename, status, max_persons, total_intrusions, video_url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (task_id, filename, status, max_persons, total_intrusions, video_url))
    conn.commit()
    conn.close()
def get_task_status(task_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT status, video_url, total_intrusions FROM tasks WHERE task_id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"status": row[0], "video_url": row[1], "total_intrusions": row[2]}
    return None


def save_alarm(task_id, frame_idx, time_sec, snapshot_url):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO alarms (task_id, frame_idx, time_sec, snapshot_url)
        VALUES (?, ?, ?, ?)
    ''', (task_id, frame_idx, time_sec, snapshot_url))
    conn.commit()
    conn.close()


def get_all_alarms():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, task_id, frame_idx, time_sec, snapshot_url, created_at FROM alarms ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    alarms = []
    for row in rows:
        alarms.append({
            "id": row[0], "task_id": row[1], "frame_idx": row[2],
            "time_sec": row[3], "snapshot_url": row[4], "created_at": row[5]
        })
    return alarms


def get_overview_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
    total_videos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM alarms")
    total_alarms = cursor.fetchone()[0]
    cursor.execute("SELECT MAX(max_persons) FROM tasks")
    max_persons = cursor.fetchone()[0] or 0
    conn.close()
    return {"total_videos": total_videos, "total_alarms": total_alarms, "max_persons": max_persons}


def get_agent_analysis_data():
    """获取供智能体分析的数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_videos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM alarms")
    total_alarms = cursor.fetchone()[0]

    # 找出最容易发生入侵的“高危视频”（告警次数最多）
    cursor.execute("SELECT task_id, COUNT(*) as c FROM alarms GROUP BY task_id ORDER BY c DESC LIMIT 1")
    high_risk_task = cursor.fetchone()

    conn.close()
    return {
        "total_videos": total_videos,
        "total_alarms": total_alarms,
        "high_risk_task": high_risk_task[0] if high_risk_task else "暂无",
        "high_risk_count": high_risk_task[1] if high_risk_task else 0
    }


def get_trend_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 获取过去 7 天的日期列表（包括今天）
    import datetime
    today = datetime.date.today()
    dates = [(today - datetime.timedelta(days=i)).strftime('%m-%d') for i in range(6, -1, -1)]

    video_counts = []
    alarm_counts = []

    for d in dates:
        # 注意：SQLite 的 created_at 格式是 "YYYY-MM-DD HH:MM:SS"
        # 我们只需要匹配月份和日期（MM-DD）
        # 这里用 LIKE '%MM-DD%' 来模糊查询当天的数据
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status='completed' AND created_at LIKE ?", (f'%-{d} %',))
        video_counts.append(cursor.fetchone()[0])

        cursor.execute("SELECT COUNT(*) FROM alarms WHERE created_at LIKE ?", (f'%-{d} %',))
        alarm_counts.append(cursor.fetchone()[0])

    conn.close()
    return {
        "dates": dates,
        "video_counts": video_counts,
        "alarm_counts": alarm_counts
    }