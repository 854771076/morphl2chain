from main import *
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time
from apscheduler.triggers.cron import CronTrigger
#填入私钥
bot=Morphl2_Bot(private_key='')

def task():
    try:
        bot.open_blind_box()
        bot.sign_in()
        bot.vote()
    except:
        pass
# 创建调度器
scheduler = BackgroundScheduler()

# 定义一个每天9点执行
trigger = CronTrigger(hour=9, minute=0)

# 添加任务到调度器
scheduler.add_job(task, trigger)
task()
# 启动调度器
scheduler.start()

# 让主线程保持运行，以便调度器可以执行任务
try:
    while True:
        time.sleep(1)
except Exception as e:
    logger.error(f"{e}")
    # 关闭调度器
    scheduler.shutdown()