import json
import os
def wash_data(students):
      if not students:
          return {"error": "数据为空"}
      return students
def analyze(students):
      students = wash_data(students)
      fail = [s for s in students
              if s['math'] < 60 or s['english'] < 60 or s['chinese'] < 60]

      total = len(students)
      fail_count = len(fail)
      avg_math = sum(s['math'] for s in students) / total
      avg_eng = sum(s['english'] for s in students) / total
      avg_chn = sum(s['chinese'] for s in students) / total
      avg_total = (avg_math + avg_eng + avg_chn) / 3
      report = f"""=== 学生成绩分析报告 ===
总人数：{total}
不及格人数：{fail_count}（{'、'.join(s['name'] for s in fail)}）
数学均分：{avg_math:.1f}
英语均分：{avg_eng:.1f}
语文均分：{avg_chn:.1f}
总均分：{avg_total:.1f}
"""
      return report

def data_pipeline(filepath, output_path="students_report.json"):
      # E: 提取
      with open(filepath, "r", encoding="utf-8") as f:
          students = json.load(f)
      # T + L: 变换后存 JSON
      result = {
          "总人数": len(students),
          "不及格人数": len([s for s in students
                           if s['math'] < 60 or s['english'] < 60 or s['chinese'] < 60]),
          "各科均分": {
              "数学": round(sum(s['math'] for s in students) / len(students), 1),
              "英语": round(sum(s['english'] for s in students) / len(students), 1),
              "语文": round(sum(s['chinese'] for s in students) / len(students), 1),
          }
      }
      with open(output_path, "w", encoding="utf-8") as f:
          json.dump(result, f, ensure_ascii=False, indent=2)
      return analyze(students)

print(data_pipeline("data.json"))