from agents.graph import executable_agent
from workers.scheduler import scheduler

if __name__ == "__main__":
    print("AI Research Agent is online.")
    # Option 1: Run once
    # executable_agent.invoke({"task": "Analyze X Company", "iteration_count": 0})
    
    # Option 2: Start the 9:00 AM daily clock
    scheduler.start()