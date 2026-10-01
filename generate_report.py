import subprocess
from collections import defaultdict
import datetime
import io
import os
import sys
import html

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

COLLEGE_NAME = "Swami Keshvanand Institute of Technology, Management & Gramothan, Jaipur"
DEPARTMENT_NAME = "Department of Computer Science & Engineering"

def get_repo_info():
    repo_name, branch_name = "Project-Repository", "main"
    try:
        root_path = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], encoding='utf-8').strip()
        repo_name = os.path.basename(root_path)
    except Exception:
        try:
            remote_url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'], encoding='utf-8').strip()
            repo_name = remote_url.rstrip('/').split('/')[-1].replace('.git', '')
        except Exception:
            repo_name = os.path.basename(os.getcwd())
    try:
        branch_name = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], encoding='utf-8').strip()
    except Exception: pass
    return repo_name, branch_name

def get_git_metrics(interval="weekly"):
    today = datetime.date.today()
    git_args = ['git', 'log', '--no-merges', '--pretty=format:COMMIT|||%h|||%an|||%ad|||%s', '--date=short', '--numstat']
    if interval == "weekly":
        since_date = (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        git_args.append(f"--since={since_date}")
        scope_title = f"Last 7 Days (Since {since_date})"
    elif interval == "monthly":
        since_date = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        git_args.append(f"--since={since_date}")
        scope_title = f"Last 30 Days (Since {since_date})"
    else:
        scope_title = "Complete Project Lifecycle (All Commits)"
    try:
        raw_output = subprocess.check_output(git_args, encoding='utf-8', errors='replace')
    except subprocess.CalledProcessError:
        return None, None, None, scope_title

    students = defaultdict(lambda: {"commits": 0, "added": 0, "deleted": 0, "active_days": set()})
    timeline_activity = defaultdict(lambda: defaultdict(int))
    student_logs = defaultdict(list)
    current_author, current_date_str = None, None

    for line in raw_output.strip().split('\n'):
        line = line.strip()
        if not line: continue
        if line.startswith('COMMIT|||'):
            parts = line.split('|||')
            if len(parts) >= 5:
                sha, author, date_str, msg = parts[1].strip(), parts[2].strip(), parts[3].strip(), parts[4].strip()
                if "bot" in author.lower() or "github-actions" in author.lower():
                    current_author = None; continue
                current_author, current_date_str = author, date_str
                students[current_author]["commits"] += 1
                students[current_author]["active_days"].add(current_date_str)
                student_logs[current_author].append((date_str, sha, msg))
                try:
                    dt = datetime.datetime.strptime(current_date_str, "%Y-%m-%d").date()
                    if interval == "weekly": period_key = dt.strftime("%a (%b %d)")
                    elif interval == "monthly": period_key = f"{dt.isocalendar()[0]}-W{dt.isocalendar()[1]:02d}"
                    else: period_key = dt.strftime("%Y-%m")
                    timeline_activity[period_key][current_author] += 1
                except Exception: pass
        elif current_author and not line.startswith('COMMIT|||'):
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                students[current_author]["added"] += int(parts[0])
                students[current_author]["deleted"] += int(parts[1])
    return students, timeline_activity, student_logs, scope_title

def create_charts(students, timeline_activity, interval):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8))
    authors, periods = list(students.keys()), sorted(timeline_activity.keys())
    if periods and authors:
        for author in authors:
            counts = [timeline_activity[p].get(author, 0) for p in periods]
            ax1.plot(periods, counts, marker='o', linewidth=2, label=author)
        ax1.set_title(f"Commit Timeline ({interval.capitalize()})", fontsize=10, fontweight='bold')
        ax1.set_ylabel("Commits"); ax1.tick_params(axis='x', rotation=30)
        ax1.grid(True, linestyle='--', alpha=0.5); ax1.legend(fontsize=8)
    else: ax1.text(0.5, 0.5, "No commits found", ha='center', va='center')
    if authors:
        net_loc = [students[a]["added"] - students[a]["deleted"] for a in authors]
        ax2.bar(authors, net_loc, color=['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F'][:len(authors)], width=0.45)
        ax2.set_title("Net Lines of Code Written", fontsize=10, fontweight='bold')
        ax2.set_ylabel("LOC (Added - Deleted)"); ax2.grid(axis='y', linestyle='--', alpha=0.5)
    else: ax2.text(0.5, 0.5, "No LOC changes", ha='center', va='center')
    plt.tight_layout()
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=200); plt.close()
    img_buffer.seek(0)
    return Image(img_buffer, width=500, height=170)

def generate_pdf(interval="weekly"):
    repo_name, branch_name = get_repo_info()
    students, timeline_activity, student_logs, scope_title = get_git_metrics(interval)
    if students is None: return
    date_stamp = datetime.date.today().strftime("%Y-%m-%d")
    report_title = "Weekly Progress Report (Form-3)" if interval == "weekly" else ("Monthly Progress Report (Form-3)" if interval == "monthly" else "Final Project Evaluation Report")
    doc_name = f"{repo_name}_Weekly_Progress_Report_Form-3_{date_stamp}.pdf" if interval == "weekly" else (f"{repo_name}_Monthly_Progress_Report_Form-3_{date_stamp}.pdf" if interval == "monthly" else f"{repo_name}_Final_Report_{date_stamp}.pdf")
    
    doc = SimpleDocTemplate(doc_name, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    college_style = ParagraphStyle('C', parent=styles['Heading1'], fontSize=13.5, leading=17, textColor=colors.HexColor("#0F172A"), alignment=1, spaceAfter=2)
    dept_style = ParagraphStyle('D', parent=styles['Normal'], fontSize=9.5, leading=13, textColor=colors.HexColor("#475569"), alignment=1, spaceAfter=6)
    title_style = ParagraphStyle('T', parent=styles['Heading2'], fontSize=13, leading=17, textColor=colors.HexColor("#1A365D"), alignment=1, spaceAfter=5)
    repo_style = ParagraphStyle('R', parent=styles['Normal'], fontSize=9.5, leading=14, textColor=colors.HexColor("#0F172A"), spaceAfter=3)
    meta_style = ParagraphStyle('M', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor("#64748B"), spaceAfter=8)
    section_style = ParagraphStyle('S', parent=styles['Heading2'], fontSize=10.5, leading=14, textColor=colors.HexColor("#0F172A"), spaceBefore=7, spaceAfter=4)
    sub_section_style = ParagraphStyle('SS', parent=styles['Heading3'], fontSize=9, leading=12, textColor=colors.HexColor("#2563EB"), spaceBefore=5, spaceAfter=2)
    msg_style = ParagraphStyle('Msg', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor("#1E293B"))
    meta_cell_style = ParagraphStyle('MC', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor("#475569"), alignment=1)
    marks_style = ParagraphStyle('Mk', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor("#0F172A"), alignment=1)
    sig_block_style = ParagraphStyle('Sig', parent=styles['Normal'], fontSize=9, leading=15, textColor=colors.HexColor("#0F172A"), alignment=0)

    story = [Paragraph(f"<b>{html.escape(COLLEGE_NAME)}</b>", college_style), Paragraph(f"<b>{html.escape(DEPARTMENT_NAME)}</b>", dept_style), Paragraph(f"<u><b>{report_title}</b></u>", title_style), Spacer(1, 3)]
    story.append(Paragraph(f"<b>Project Repository:</b> <font color='#2563EB'><b>{html.escape(repo_name)}</b></font> &nbsp;|&nbsp; <b>Branch:</b> <code>{html.escape(branch_name)}</code>", repo_style))
    story.append(Paragraph(f"<b>Evaluation Window:</b> {scope_title} &nbsp;|&nbsp; <b>Generated On:</b> {datetime.date.today().strftime('%B %d, %Y')}", meta_style))
    story.append(Paragraph("1. Individual Contribution Breakdown", section_style))
    total_commits = sum(d["commits"] for d in students.values())
    table_data = [["Student Name", "Commits (%)", "Lines Added", "Lines Deleted", "Net LOC", "Active Days"]]
    if students:
    for name, data in students.items():
        total_loc = data["added"] + data["deleted"]

        if total_loc < 1:
            continue

        pct = (data["commits"] / total_commits * 100) if total_commits > 0 else 0
        table_data.append([
            html.escape(name),
            f"{data['commits']} ({pct:.1f}%)",
            f"+{data['added']:,}",
            f"-{data['deleted']:,}",
            f"{data['added'] - data['deleted']:,}",
            f"{len(data['active_days'])} days"
        ])
    table = Table(table_data, colWidths=[120, 80, 80, 80, 80, 100])
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('ALIGN', (0, 1), (0, -1), 'LEFT'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5), ('TOPPADDING', (0, 0), (-1, -1), 3.5), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")), ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")])]))
    story.extend([table, Spacer(1, 6), Paragraph("2. Visual Trends & Volume", section_style), create_charts(students, timeline_activity, interval), Spacer(1, 6)])
    story.append(Paragraph(f"3. Detailed Commit Logs & Mentor Evaluation ({interval.capitalize()})", section_style))
    if not student_logs: story.append(Paragraph("<i>No commit logs found.</i>", styles['Normal']))
    else:
        for student_name, logs in student_logs.items():
            student_section = [Paragraph(f"<b>Student:</b> {html.escape(student_name)} — <i>{len(logs)} commit(s)</i>", sub_section_style)]
            log_table_data = [["Date", "Hash", "Commit Message", "Mentor Marks (/10)"]]
            first_date, first_sha, first_msg = logs[0]
            log_table_data.append([Paragraph(first_date, meta_cell_style), Paragraph(f"<code>{first_sha}</code>", meta_cell_style), Paragraph(html.escape(first_msg) if first_msg else "(No message)", msg_style), Paragraph("<b>_____ / 10</b>", marks_style)])
            for d, s, m in logs[1:]: log_table_data.append([Paragraph(d, meta_cell_style), Paragraph(f"<code>{s}</code>", meta_cell_style), Paragraph(html.escape(m) if m else "(No message)", msg_style), ""])
            num_rows = len(log_table_data)
            log_table = Table(log_table_data, colWidths=[65, 50, 335, 90])
            log_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#475569")), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('ALIGN', (3, 0), (3, -1), 'CENTER'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 7.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5), ('TOPPADDING', (0, 0), (-1, -1), 2.5), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")), ('ROWBACKGROUNDS', (0, 1), (2, -1), [colors.white, colors.HexColor("#F8FAFC")]), ('SPAN', (3, 1), (3, num_rows - 1)), ('VALIGN', (3, 1), (3, num_rows - 1), 'MIDDLE'), ('BACKGROUND', (3, 1), (3, num_rows - 1), colors.HexColor("#FEF3C7"))]))
            student_section.extend([log_table, Spacer(1, 5)])
            story.append(KeepTogether(student_section))
    story.append(Spacer(1, 16))
    mentor_cell = [Paragraph("<b>Name:</b> ___________________________", sig_block_style), Paragraph("<b>Designation:</b> Project Mentor", sig_block_style), Spacer(1, 6), Paragraph("<b>Signature:</b> ________________________", sig_block_style)]
    coord_cell = [Paragraph("<b>Name:</b> ___________________________", sig_block_style), Paragraph("<b>Designation:</b> Lab Coordinator", sig_block_style), Spacer(1, 6), Paragraph("<b>Signature:</b> ________________________", sig_block_style)]
    sig_table = Table([[mentor_cell, coord_cell]], colWidths=[270, 270])
    sig_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (0, -1), 0), ('LEFTPADDING', (1, 0), (1, -1), 40)]))
    story.append(KeepTogether(sig_table))
    doc.build(story)
    print(f"\n[SUCCESS] Generated: {doc_name}")

if __name__ == "__main__":
    generate_pdf(sys.argv[1].lower() if len(sys.argv) > 1 else "weekly")