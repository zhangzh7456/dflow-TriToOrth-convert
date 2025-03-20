
# ------------ parse.py ------------
import argparse
import re
from pathlib import Path

def parse_out_file(input_path: Path, xyz_path: Path, txt_path: Path):
    with open(input_path, 'r') as f:
        lines = [line.rstrip('\n') for line in f]

    # 提取原子总数
    num_atoms = None
    for line in lines:
        if match := re.search(r'NumberOfAtoms\s+(\d+)', line):
            num_atoms = match.group(1)
            break

    # 定位outcoor段落
    outcoor_index = -1
    for i, line in enumerate(lines):
        if "outcoor: Relaxed atomic coordinates" in line:
            outcoor_index = i
            break
    if outcoor_index == -1:
        raise ValueError("找不到'Relaxed atomic coordinates'段落")

    # 提取晶胞模量
    cell_vector_modules = None
    cell_line_index = -1
    for j in range(outcoor_index + 1, len(lines)):
        line = lines[j]
        if match := re.match(r'outcell: Cell vector modules \(Ang\)\s*:\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)', line):
            cell_vector_modules = match.groups()
            cell_line_index = j
            break

    # 提取单位晶胞向量
    unit_cell_vectors = []
    unit_cell_start = -1
    for j in range(outcoor_index + 1, len(lines)):
        if "outcell: Unit cell vectors (Ang):" in lines[j]:
            unit_cell_start = j
            for k in range(j+1, j+4):
                if k < len(lines):
                    unit_cell_vectors.append(lines[k].strip())
            break

    # 排除干扰行
    excluded = set()
    if cell_line_index != -1:
        excluded.add(cell_line_index)
    if unit_cell_start != -1:
        excluded.update(range(unit_cell_start, unit_cell_start+4))

    # 收集原子数据
    atom_data = []
    j = outcoor_index + 1
    while j < len(lines):
        line = lines[j].strip()
        if not line:
            break
        if j in excluded:
            j += 1
            continue
        parts = line.split()
        if len(parts) >= 6:
            atom_data.append((parts[5], parts[0], parts[1], parts[2]))
        j += 1

    # 写入XYZ文件
    with open(xyz_path, 'w') as f:
        f.write(f"{num_atoms or len(atom_data)}\n")
        f.write(" ".join(cell_vector_modules if cell_vector_modules else ["0.0"]*3) + "\n")
        for elem, x, y, z in atom_data:
            f.write(f"{elem} {x} {y} {z}\n")

    # 写入TXT文件
    with open(txt_path, 'w') as f:
        for vec in unit_cell_vectors[:3]:
            f.write(f"{vec}\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--xyz', type=Path, required=True)
    parser.add_argument('--txt', type=Path, required=True)
    args = parser.parse_args()
    
    parse_out_file(args.input, args.xyz, args.txt)

if __name__ == "__main__":
    main()
