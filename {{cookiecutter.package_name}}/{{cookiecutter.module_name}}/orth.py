#!/usr/bin/env python
import argparse
import numpy as np
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Convert triclinic cell to orthogonal')
    parser.add_argument('--input-xyz', type=Path, required=True)
    parser.add_argument('--input-txt', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()

    # 读取原始晶胞向量（来自step1的txt文件）
    with open(args.input_txt, 'r') as f:
        lines = [line.strip() for line in f.readlines()[:3]]
    
    a = np.array([float(x) for x in lines[0].split()])
    b = np.array([float(x) for x in lines[1].split()])
    c = np.array([float(x) for x in lines[2].split()])

    # 读取目标晶胞模量（来自step1的xyz文件第二行）
    with open(args.input_xyz, 'r') as f:
        xyz_lines = f.readlines()
    cell_modules = list(map(float, xyz_lines[1].strip().split()))
    
    # 构建正交晶胞向量
    a1 = np.array([cell_modules[0], 0.0, 0.0])
    b1 = np.array([0.0, cell_modules[1], 0.0])
    c1 = np.array([0.0, 0.0, cell_modules[2]])

    # 读取原子坐标
    data = np.loadtxt(args.input_xyz, dtype=str, skiprows=2)
    
    # 坐标转换计算
    tens = np.array([a, b, c]).T
    inv_tens = np.linalg.inv(tens)
    coord = np.array([[float(num) for num in row[1:]] for row in data])
    converted_coord = np.array([inv_tens @ row for row in coord])
    
    tens1 = np.array([a1, b1, c1]).T 
    final_coords = np.array([tens1 @ row for row in converted_coord])

    # 写入输出文件
    with open(args.output, 'w') as fo:
        fo.write(f"{len(data)}\n")
        fo.write(f"orthogonal box vectors: {a1[0]} {b1[1]} {c1[2]}\n")
        for i, row in enumerate(final_coords):
            fo.write(f"{data[i][0]}  {row[0]:.6f}  {row[1]:.6f}  {row[2]:.6f}\n")

if __name__ == "__main__":
    main()
