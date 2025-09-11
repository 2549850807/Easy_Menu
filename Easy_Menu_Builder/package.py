#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Easy Menu Navigator 打包分发脚本
将构建好的程序打包成zip文件便于分发
"""

import os
import sys
import zipfile
from pathlib import Path
import shutil

def create_distribution_package():
    """创建分发包"""
    print("创建分发包...")
    
    # 检查是否存在构建好的程序
    dist_dir = Path("dist/Easy_Menu_Navigator")
    if not dist_dir.exists():
        print("错误: 未找到构建好的程序，请先运行 build.py")
        return False
    
    # 创建分发目录
    package_dir = Path("package")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # 复制程序文件
    print("正在复制程序文件...")
    shutil.copytree(dist_dir, package_dir / "Easy_Menu_Navigator")
    
    # 复制说明文件
    readme_files = ["README_PACKAGED.md", "README.md"]
    for readme in readme_files:
        readme_path = Path(readme)
        if readme_path.exists():
            shutil.copy2(readme_path, package_dir / readme)
    
    # 创建版本信息文件
    version_info = package_dir / "VERSION.txt"
    with open(version_info, "w", encoding="utf-8") as f:
        f.write("Easy Menu Navigator\n")
        f.write("Version: 1.0.0\n")
        f.write("Build Date: " + str(Path.cwd().stat().st_mtime) + "\n")
    
    print("正在创建zip压缩包...")
    
    # 创建zip文件
    zip_filename = "Easy_Menu_Navigator_Windows_Portable.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob("*"):
            if file_path.is_file():
                # 计算在zip中的路径
                arc_name = file_path.relative_to(package_dir)
                zipf.write(file_path, f"Easy_Menu_Navigator/{arc_name}")
    
    print(f"分发包创建成功: {zip_filename}")
    print(f"文件大小: {Path(zip_filename).stat().st_size / 1024 / 1024:.2f} MB")
    
    return True

def main():
    """主函数"""
    print("Easy Menu Navigator 分发包创建工具")
    print("=" * 40)
    
    # 切换到项目目录
    project_dir = Path(__file__).parent.absolute()
    os.chdir(project_dir)
    print(f"当前工作目录: {project_dir}")
    
    # 创建分发包
    success = create_distribution_package()
    
    if success:
        print("\n分发包创建完成!")
        print("您可以将生成的zip文件分发给其他用户")
    else:
        print("\n分发包创建失败!")

if __name__ == '__main__':
    main()