from jinja2 import Environment, FileSystemLoader
import datetime
import os

def generate_html_report(ai_analysis, filename="system_report.html"):
    """
    Generate a HTML report from AI analysis
    """
    env = Environment(loader=FileSystemLoader(searchpath="./reports/templates"))
    template = env.get_template("report_template.html")

    html_content = template.render(
        generated=datetime.datetime.now(),
        analysis=ai_analysis
    )

    # Save report
    with open(filename, "w") as f:
        f.write(html_content)
    
    return os.path.abspath(filename)
