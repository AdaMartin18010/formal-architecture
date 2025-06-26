import argparse
import json

def load_json(path):
    with open(path) as f:
        return json.load(f)

def compare_io(classical, quantum):
    # 假设为简单的字典/列表对比，可根据实际扩展
    return classical == quantum

def main():
    parser = argparse.ArgumentParser(description='经典-量子接口一致性测试')
    parser.add_argument('--input', required=True, help='经典输入数据')
    parser.add_argument('--output', required=True, help='量子模拟输出数据')
    args = parser.parse_args()

    classical = load_json(args.input)
    quantum = load_json(args.output)
    if compare_io(classical, quantum):
        print('经典-量子接口数据一致')
    else:
        print('经典-量子接口数据不一致')
        print('经典输入:', classical)
        print('量子输出:', quantum)

if __name__ == '__main__':
    main() 