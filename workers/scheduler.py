from therapeutic_scheduler import BlockingScheduler
from agents.graph import executable_agent

def start_daily_job():
    # This is what happens when the alarm goes off
    executable_agent.invoke({"task": "Daily Market Report", "iteration_count": 0})

scheduler = BlockingScheduler()
# Set to run every day at 9am
scheduler.add_job(start_daily_job, 'cron', hour=9)
scheduler.start()