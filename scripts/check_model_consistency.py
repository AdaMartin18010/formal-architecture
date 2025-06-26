import argparse
import torch
import json
import numpy as np

def load_model(path):
    return torch.load(path)

def load_input(input_path):
    with open(input_path) as f:
        data = json.load(f)
    return torch.tensor(data)

def compare_outputs(out1, out2, atol=1e-5):
    return np.allclose(out1.detach().numpy(), out2.detach().numpy(), atol=atol)

def main():
    parser = argparse.ArgumentParser(description='AI模型一致性检查')
    parser.add_argument('--model1', required=True)
    parser.add_argument('--model2', required=True)
    parser.add_argument('--input', required=True)
    args = parser.parse_args()

    model1 = load_model(args.model1)
    model2 = load_model(args.model2)
    input_tensor = load_input(args.input)

    out1 = model1(input_tensor)
    out2 = model2(input_tensor)

    if compare_outputs(out1, out2):
        print('模型输出一致')
    else:
        print('模型输出不一致')
        print('模型1输出:', out1)
        print('模型2输出:', out2)

if __name__ == '__main__':
    main() 