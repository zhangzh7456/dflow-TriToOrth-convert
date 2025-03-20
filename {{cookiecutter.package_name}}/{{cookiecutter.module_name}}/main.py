import os
import glob
from pathlib import Path
from dflow import (
    config, 
    s3_config,
    Step, 
    Workflow, 
    upload_artifact
)
from dflow.plugins import bohrium
from dflow.plugins.bohrium import TiefblueClient
from dflow.python import (
    OP, 
    OPIO, 
    Artifact, 
    OPIOSign, 
    PythonOPTemplate,
)

# 基于Bohrium账号配置ARGO服务器
config["host"] = "https://workflows.deepmodeling.com"
config["k8s_api_server"] = "https://workflows.deepmodeling.com"
config["namespace"] = "argo"

bohrium.config["username"] = "<Bohrium-email>"
bohrium.config["password"] = "<Bohrium-password>"
bohrium.config["project_id"] = "<Bohrium-project_id>"

s3_config["repo_key"] = "oss-bohrium"
s3_config["storage_client"] = TiefblueClient()

class OutfileParser(OP):
    @classmethod
    def get_input_sign(cls):
        return OPIOSign({
            "out_file": Artifact(Path),
            "parse_script": Artifact(Path)
        })

    @classmethod
    def get_output_sign(cls):
        return OPIOSign({
            "xyz_out": Artifact(Path),
            "txt_out": Artifact(Path),
        })

    def execute(self, op_in: OPIO) -> OPIO:
        xyz_path = Path("output.xyz")
        txt_path = Path("cell_vectors.txt")
        
        import subprocess
        subprocess.run([
            "python", str(op_in["parse_script"]),
            "--input", str(op_in["out_file"]),
            "--xyz", str(xyz_path),
            "--txt", str(txt_path),
        ], check=True)

        return OPIO({
            "xyz_out": xyz_path,
            "txt_out": txt_path,
        })

class OrthoConverter(OP):
    @classmethod
    def get_input_sign(cls):
        return OPIOSign({
            "input_xyz": Artifact(Path),
            "input_txt": Artifact(Path),
            "orth_script": Artifact(Path)
        })

    @classmethod
    def get_output_sign(cls):
        return OPIOSign({
            "converted_xyz": Artifact(Path),
        })

    def execute(self, op_in: OPIO) -> OPIO:
        # 动态安装 numpy
        import subprocess
        subprocess.run([
            "python", "-m", "pip", "install", "numpy"
        ], check=True)
        
        output_path = Path("converted.xyz")
        
        subprocess.run([
            "python", str(op_in["orth_script"]),
            "--input-xyz", str(op_in["input_xyz"]),
            "--input-txt", str(op_in["input_txt"]),
            "--output", str(output_path),
        ], check=True)

        return OPIO({
            "converted_xyz": output_path,
        })

def find_single_file(pattern: str) -> Path:
    files = glob.glob(pattern)
    if len(files) != 1:
        raise ValueError(f"需要且只能存在1个{pattern}文件，当前找到: {files}")
    return Path(files[0])

def build_workflow():
    wf = Workflow(name="crystal-converter")
    
    # 上传必要文件
    out_file = upload_artifact(find_single_file("*.out"))
    parse_script = upload_artifact(find_single_file("parse.py"))
    orth_script = upload_artifact(find_single_file("orth.py"))
    
    # Step1: 解析文件
    step1 = Step(
        name="parse-step",
        template=PythonOPTemplate(
            OutfileParser,
            image="python:3.8",
        ),
        artifacts={
            "out_file": out_file,
            "parse_script": parse_script
        },
    )
    
    # Step2: 正交化转换（移除了 commands 参数）
    step2 = Step(
        name="convert-step",
        template=PythonOPTemplate(
            OrthoConverter,
            image="python:3.8",  # 保持镜像不变
        ),
        artifacts={
            "input_xyz": step1.outputs.artifacts["xyz_out"],
            "input_txt": step1.outputs.artifacts["txt_out"],
            "orth_script": orth_script
        },
    )
    
    wf.add(step1)
    wf.add(step2)
    return wf

if __name__ == "__main__":
    try:
        workflow = build_workflow()
        
        if os.getenv("DEBUG_MODE"):
            workflow.debug()
            print("本地调试模式")
        else:
            result = workflow.submit()
            print(f"工作流ID: {result.workflow_id}")
            
    except Exception as e:
        print(f"错误: {str(e)}")
