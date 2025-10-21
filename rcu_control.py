import yaml
import os
import subprocess
import json

# ====================================================================
# [GEU-BASE]: وظيفة إنشاء الهيكل الأولي للمشروع
# ====================================================================

def create_project_structure(project_id, lang):
    """تنشئ الهيكل الأساسي للمشروع والمجلدات الضرورية"""
    project_folder = f"projects/{project_id}"
    os.makedirs(project_folder, exist_ok=True)
    
    # إنشاء مجلد .github/workflows إذا لم يكن موجودًا
    os.makedirs(".github/workflows", exist_ok=True)
    
    # إنشاء ملف meta لتوثيق المشروع (C2)
    meta_data = {
        "project_id": project_id,
        "language": lang,
        "status": "C2_PLANNING",
        "deployment_path": f".github/workflows/{project_id}_deploy.yml"
    }
    with open(f"{project_folder}/meta_data.json", 'w') as f:
        json.dump(meta_data, f, indent=4)
        
    # إنشاء ملفات المصدر الوهمية المطلوبة لنجاح الاختبار المبدئي
    with open(f"{project_folder}/main_test.py", 'w') as f:
        f.write("# وحدة الاختبار الوظيفي (SIMU) هنا")
    with open(f"{project_folder}/requirements.txt", 'w') as f:
        f.write("pyyaml") # إضافة تبعية YAML كتجربة
        
    print(f"✅ تم إنشاء هيكل المشروع {project_id} بلغة {lang} بنجاح.")
    return project_folder

# ====================================================================
# [RCEU-GIT]: وظيفة تهيئة المخزن المحلي والربط السحابي (SET:RCEU:CONFIG)
# ====================================================================

def initialize_git(remote_url):
    """
    تقوم بتهيئة Git محليًا، وتضيف ملفات النظام، وتربطها بمخزن عن بعد.
    يتم تشغيل هذه الوظيفة لمرة واحدة فقط.
    """
    try:
        # 1. تهيئة Git محليًا في المجلد الأب (System_Core)
        subprocess.run(["git", "init"], check=True)
        print("✅ Git تم تهيئته بنجاح محليًا.")

        # 2. إضافة مسار المخزن السحابي (Remote)
        # يتم استخدام --force في حالة وجود مخزن آخر مربوط مسبقًا
        subprocess.run(["git", "remote", "add", "origin", remote_url], check=True, capture_output=True, text=True)
        print(f"✅ تم ربط المخزن السحابي: {remote_url}")

        # 3. إضافة جميع ملفات النظام الأولية
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "GIT_INIT: Base System Core (RCEU/GEU) setup"], check=True)
        print("✅ تم إضافة وتثبيت الملفات الأساسية.")

    except subprocess.CalledProcessError as e:
        # تسجيل عجز تأكيدي في حال فشل عملية Git
        print(f"❌ عجز تأكيدي (AD): فشل في تهيئة Git. تحقق من تثبيت Git بشكل صحيح أو عدم وجود مخزن مرتبط مسبقًا.")
        print(f"تفاصيل الخطأ: {e.stderr}")
        raise e

# ====================================================================
# [RCEU-CORE]: وظيفة توليد ملف النشر السحابي (deployment_config.yml)
# ====================================================================

def generate_deployment_config(project_id, project_path, action_type):
    """
    تُنشئ ملف YAML لخطة النشر السحابية (GitHub Actions).
    """
    # .................... [الكود الذي تم كتابته مسبقاً يوضع هنا] ....................
    if action_type == "SIM_TEST":
        job_name = "Run_Functional_Tests"
        script_command = f"python {project_path}/main_test.py"
    elif action_type == "DEL_PACKAGE":
        job_name = "Build_And_Package_Artifact"
        script_command = f"python {project_path}/main_build.py"
    else:
        raise ValueError(f"❌ خطأ يقيني: نوع الإجراء {action_type} غير مدعوم.")

    deployment_config = {
        'name': f'CI/CD - {project_id}',
        'on': {'push': {'branches': ['main']}}, 
        'jobs': {
            'run_job': {
                'name': job_name,
                'runs-on': 'ubuntu-latest',
                'steps': [
                    {'uses': 'actions/checkout@v3'},
                    {'name': 'Setup Python',
                     'uses': 'actions/setup-python@v3',
                     'with': {'python-version': '3.x'}},
                    {'name': 'Install Dependencies',
                     'run': 'pip install -r requirements.txt'},
                    {'name': 'Run Script',
                     'run': script_command},
                ]
            }
        }
    }
    
    config_folder = f".github/workflows"
    os.makedirs(config_folder, exist_ok=True)
    yaml_filename = f"{config_folder}/{project_id}_deploy.yml"

    with open(yaml_filename, 'w') as f:
        yaml.dump(deployment_config, f, sort_keys=False)
        
    print(f"✅ تم إنشاء ملف YAML لخطة النشر {yaml_filename} بنجاح.")
    return yaml_filename

# ====================================================================
# وظيفة محاكاة إطلاق أمر DSL
# ====================================================================

if __name__ == "__main__":
    # 0. تهيئة مسار Git الأولي (يجب تشغيله مرة واحدة)
    # ملاحظة: تم إزالة التعليق عن هذه الوظيفة
    github_repo_url = "https://github.com/essamelaskary4-glitch/System_Core.git" 
    
    print("\n--- محاكاة إطلاق أمر SET:RCEU:CONFIG:INIT_GIT ---")
    initialize_git(github_repo_url) 

    # 1. المرحلة C1/C2: بناء الهيكل الأولي للمشروع
    project_id = "PROJ_ALPHA_001"
    language = "Python"
    project_folder = create_project_structure(project_id, language)
    
    # 2. محاكاة إنشاء ملف YAML للاختبار
    print("\n--- محاكاة إطلاق أمر SIM ---")
    generate_deployment_config(project_id, project_folder, "SIM_TEST")
    
    # 3. محاكاة إنشاء ملف YAML للتجميع النهائي
    print("\n--- محاكاة إطلاق أمر DEL ---")
    generate_deployment_config(project_id, project_folder, "DEL_PACKAGE")