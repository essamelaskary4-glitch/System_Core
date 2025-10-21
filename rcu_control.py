import yaml
import os
import subprocess
import json

# ====================================================================
# [GEU-BASE]: وظيفة إنشاء الهيكل الأولي للمشروع (المُحدثة لمشروع API)
# ====================================================================

def create_project_structure(project_id, lang):
    """تنشئ الهيكل الأساسي للمشروع والمجلدات الضرورية"""
    project_folder = f"projects/{project_id}"
    os.makedirs(project_folder, exist_ok=True)
    
    os.makedirs(".github/workflows", exist_ok=True)
    
    # 1. تحديث ملف التوثيق (C2)
    meta_data = {
        "project_id": project_id,
        "language": lang,
        "type": "API_BACKEND", # تحديث نوع المشروع
        "status": "C1_INITIATED",
        "deployment_path": f".github/workflows/{project_id}_deploy.yml"
    }
    with open(f"{project_folder}/meta_data.json", 'w', encoding='utf-8') as f:
        json.dump(meta_data, f, indent=4)
        
    # 2. إنشاء ملف main.py (سكربت تشغيل API الفعلي)
    api_content = f"""
from fastapi import FastAPI

# [GEU-CORE]: تم توليد هذا السكربت بواسطة نظام System_Core
app = FastAPI(title="Inventory Management API - {project_id}")

@app.get("/")
def read_root():
    return {{"Hello": "World", "Service": "Inventory Management API is running!"}}

@app.get("/items/{{item_id}}")
def read_item(item_id: int):
    # محاكاة لاسترجاع عنصر في المخزون
    return {{"item_id": item_id, "name": f"Item {{item_id}}", "quantity": 100}}
"""
    with open(f"{project_folder}/main.py", 'w', encoding='utf-8') as f:
        f.write(api_content.strip())
        
    # 3. إنشاء ملف Dockerfile (لتغليف المشروع)
    docker_content = f"""
# Use official Python image as a base
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY {project_folder}/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY {project_folder}/main.py .

# Expose the port (FastAPI default)
EXPOSE 8000

# Command to run the application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    with open(f"{project_folder}/Dockerfile", 'w', encoding='utf-8') as f:
        f.write(docker_content.strip())

    # 4. تحديث ملف التبعيات (requirements.txt)
    with open(f"{project_folder}/requirements.txt", 'w', encoding='utf-8') as f:
        f.write("fastapi\n") 
        f.write("uvicorn\n")
        f.write("pyyaml\n") # للاحتفاظ بتبعية النظام

    print(f"✅ تم إنشاء هيكل مشروع الـ API {project_id} بلغة {lang} بنجاح.")
    return project_folder

# ====================================================================
# [RCEU-GIT]: وظيفة تهيئة المخزن المحلي والربط السحابي 
# ====================================================================

def initialize_git(remote_url):
    """تقوم بتهيئة Git محليًا، وتضيف ملفات النظام، وتربطها بمخزن عن بعد."""
    try:
        subprocess.run(["git", "init"], check=True)
        print("✅ Git تم تهيئته بنجاح محليًا.")
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True, capture_output=True, text=True)
        print(f"✅ تم ربط المخزن السحابي: {remote_url}")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "GIT_INIT: Base System Core (RCEU/GEU) setup"], check=True)
        print("✅ تم إضافة وتثبيت الملفات الأساسية.")

    except subprocess.CalledProcessError as e:
        print(f"❌ عجز تأكيدي (AD): فشل في تهيئة Git. تفاصيل الخطأ: {e.stderr}")
        raise e

# ====================================================================
# [RCEU-CORE]: وظيفة توليد ملف النشر السحابي (deployment_config.yml)
# *تم تحديث المسارات لتعمل مع main.py الجديد*
# ====================================================================

def generate_deployment_config(project_id, project_path, action_type):
    """تُنشئ ملف YAML لخطة النشر السحابية (GitHub Actions)."""
    
    # 1. تحديد الأوامر التشغيلية الجديدة
    if action_type == "SIM_TEST":
        job_name = "API_Local_Run_Test"
        # أمر التشغيل المحلي لـ FastAPI
        script_command = f"uvicorn {project_path}/main:app --host 127.0.0.1 --port 8000 &" # & للتشغيل في الخلفية
        
    elif action_type == "DEL_PACKAGE":
        job_name = "Docker_Build_And_Push"
        # أمر بناء حاوية Docker (يتطلب إعداد Docker في GitHub Actions)
        script_command = f"docker build -t {project_id}:latest -f {project_path}/Dockerfile ."
        
    else:
        raise ValueError(f"❌ خطأ يقيني: نوع الإجراء {action_type} غير مدعوم.")

    # المسار المصحح لملف requirements.txt
    requirements_path = f"{project_path}/requirements.txt" 

    deployment_config = {
        'name': f'CI/CD - {project_id}',
        'on': {'push': {'branches': ['master']}}, 
        'jobs': {
            'run_job': {
                'name': job_name,
                'runs-on': 'ubuntu-latest',
                'steps': [
                    {'uses': 'actions/checkout@v3'},
                    {'name': 'Setup Python',
                     'uses': 'actions/setup-python@v3',
                     'with': {'python-version': '3.10'}},
                    {'name': 'Install Dependencies',
                     'run': f"pip install -r {requirements_path}"},
                    
                    # يتم استخدام الأمر المخصص لكل نوع إجراء
                    {'name': job_name,
                     'run': script_command},
                ]
            }
        }
    }
    
    config_folder = f".github/workflows"
    os.makedirs(config_folder, exist_ok=True)
    yaml_filename = f"{config_folder}/{project_id}_deploy.yml"

    with open(yaml_filename, 'w', encoding='utf-8') as f:
        yaml.dump(deployment_config, f, sort_keys=False)
        
    print(f"✅ تم إنشاء ملف YAML لخطة النشر {yaml_filename} بنجاح.")
    return yaml_filename

# ====================================================================
# وظيفة محاكاة إطلاق أمر DSL (المحدثة لأمر INV_MGMT)
# ====================================================================

if __name__ == "__main__":
    
    project_id = "PROJ_INV_MGMT" # اسم المشروع الجديد
    language = "Python"
    
    print("\n--- إطلاق أمر CMD:BUILD:API:INV_MGMT ---")
    project_folder = create_project_structure(project_id, language)
    
    print("\n--- محاكاة إطلاق أمر SIM ---")
    generate_deployment_config(project_id, project_folder, "SIM_TEST")
    
    print("\n--- محاكاة إطلاق أمر DEL ---")
    generate_deployment_config(project_id, project_folder, "DEL_PACKAGE")