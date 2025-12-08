import urllib.request
import json
from datetime import datetime, timezone, timedelta

# Configuration
GIST_URL = "https://gist.githubusercontent.com/swamjay/4e8f901e7ef660c3d912ba7fc8ad4960/raw/tasks.json"
WEATHER_URL = "https://wttr.in/Ames+Iowa?u&format=%t+%C"
TIMEZONE_OFFSET = -6  # Central Standard Time (CST). Change to -5 for CDT (daylight saving)

DAY_START = 6   # 6 AM
DAY_END = 18    # 6 PM
TOTAL_SECTIONS = 12


def fetch_tasks():
    """Fetch tasks from GitHub Gist"""
    try:
        req = urllib.request.Request(GIST_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return {"vdpam": [], "vdl": [], "personal": []}


def fetch_weather():
    """Fetch weather from wttr.in"""
    try:
        req = urllib.request.Request(WEATHER_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode().strip()
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return "N/A"


def get_current_time():
    """Get current time in Central Time"""
    utc_now = datetime.now(timezone.utc)
    central_time = utc_now + timedelta(hours=TIMEZONE_OFFSET)
    return central_time


def format_datetime(dt):
    """Format datetime for display"""
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    day_name = days[dt.weekday()]
    month_name = months[dt.month - 1]
    
    hour = dt.hour
    minute = dt.minute
    ampm = 'AM' if hour < 12 else 'PM'
    
    if hour == 0:
        hour = 12
    elif hour > 12:
        hour -= 12
    
    return f"{day_name}, {month_name} {dt.day}, {dt.year}  {hour}:{minute:02d} {ampm}"


def get_section(hour):
    """Calculate current section of the day"""
    if hour < DAY_START:
        return 0, "Before Day"
    elif hour >= DAY_END:
        return TOTAL_SECTIONS, "Day Complete"
    else:
        section = hour - DAY_START + 1
        return section, f"Section {section} of {TOTAL_SECTIONS}"


def render_tasks(tasks):
    """Render task list as HTML"""
    if not tasks:
        return '<div class="task"><span class="checkbox">☐</span><span class="task-text">No tasks</span></div>'
    
    html = ""
    for task in tasks:
        checkbox = "☑" if task.get("done", False) else "☐"
        done_class = "done" if task.get("done", False) else ""
        task_text = task.get("task", "")[:30]  # Truncate long tasks
        html += f'''<div class="task">
          <span class="checkbox">{checkbox}</span>
          <span class="task-text {done_class}">{task_text}</span>
        </div>\n'''
    return html


def render_progress_bar(section):
    """Render the progress bar HTML"""
    html = ""
    for i in range(1, TOTAL_SECTIONS + 1):
        filled = "filled" if i <= section else "empty"
        html += f'<div class="progress-box {filled}"></div>\n'
    return html


def build_html():
    """Build the complete HTML page"""
    
    # Fetch data
    print("Fetching tasks...")
    tasks = fetch_tasks()
    
    print("Fetching weather...")
    weather = fetch_weather()
    
    # Get time info
    current_time = get_current_time()
    datetime_str = format_datetime(current_time)
    section_num, section_text = get_section(current_time.hour)
    
    print(f"Current time: {datetime_str}")
    print(f"Section: {section_text}")
    print(f"Weather: {weather}")
    
    # Render components
    vdpam_html = render_tasks(tasks.get("vdpam", []))
    vdl_html = render_tasks(tasks.get("vdl", []))
    personal_html = render_tasks(tasks.get("personal", []))
    progress_html = render_progress_bar(section_num)
    
    # Build final HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=800, height=480, initial-scale=1.0">
  <title>Jay's Dashboard</title>
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

    body {{
      font-family: 'Courier New', monospace;
      background: #ffffff;
      color: #000000;
      width: 800px;
      height: 480px;
      overflow: hidden;
      padding: 12px;
    }}

    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 8px;
      border-bottom: 2px solid #000;
      margin-bottom: 10px;
    }}

    .date-time {{
      font-size: 18px;
      font-weight: bold;
    }}

    .weather {{
      font-size: 18px;
      font-weight: bold;
    }}

    .progress-section {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      padding: 10px 0;
      border-bottom: 2px solid #000;
      margin-bottom: 10px;
    }}

    .section-label {{
      font-size: 16px;
      font-weight: bold;
      min-width: 140px;
    }}

    .progress-bar {{
      display: flex;
      gap: 4px;
    }}

    .progress-box {{
      width: 28px;
      height: 18px;
      border: 2px solid #000;
    }}

    .progress-box.filled {{
      background: #000;
    }}

    .progress-box.empty {{
      background: #fff;
    }}

    .time-labels {{
      font-size: 12px;
      font-weight: bold;
    }}

    .columns {{
      display: flex;
      height: 340px;
    }}

    .column {{
      flex: 1;
      padding: 0 10px;
      border-right: 2px solid #000;
    }}

    .column:last-child {{
      border-right: none;
    }}

    .column-header {{
      font-size: 20px;
      font-weight: bold;
      text-align: center;
      padding-bottom: 8px;
      margin-bottom: 10px;
      border-bottom: 1px solid #000;
    }}

    .task {{
      display: flex;
      align-items: flex-start;
      gap: 8px;
      padding: 6px 0;
      font-size: 14px;
    }}

    .checkbox {{
      font-size: 18px;
      line-height: 1;
    }}

    .task-text {{
      line-height: 1.3;
    }}

    .task-text.done {{
      text-decoration: line-through;
      opacity: 0.6;
    }}

    .updated {{
      position: absolute;
      bottom: 5px;
      right: 10px;
      font-size: 10px;
      opacity: 0.5;
    }}
  </style>
</head>
<body>
  <div class="header">
    <div class="date-time">{datetime_str}</div>
    <div class="weather">Ames: {weather}</div>
  </div>

  <div class="progress-section">
    <span class="time-labels">6AM</span>
    <span class="section-label">{section_text}</span>
    <div class="progress-bar">
      {progress_html}
    </div>
    <span class="time-labels">6PM</span>
  </div>

  <div class="columns">
    <div class="column">
      <div class="column-header">VDPAM</div>
      <div class="task-list">
        {vdpam_html}
      </div>
    </div>
    <div class="column">
      <div class="column-header">VDL</div>
      <div class="task-list">
        {vdl_html}
      </div>
    </div>
    <div class="column">
      <div class="column-header">Personal</div>
      <div class="task-list">
        {personal_html}
      </div>
    </div>
  </div>

  <div class="updated">Updated: {datetime_str}</div>
</body>
</html>'''

    # Write to file
    with open("index.html", "w") as f:
        f.write(html)
    
    print("✅ index.html generated successfully!")


if __name__ == "__main__":
    build_html()
