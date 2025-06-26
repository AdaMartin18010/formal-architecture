import argparse
from qiskit import QuantumCircuit, Aer, execute

def main():
    parser = argparse.ArgumentParser(description='量子电路模拟与验证')
    parser.add_argument('--circuit', required=True, help='QASM量子电路文件')
    args = parser.parse_args()

    qc = QuantumCircuit.from_qasm_file(args.circuit)
    backend = Aer.get_backend('qasm_simulator')
    job = execute(qc, backend, shots=1024)
    result = job.result()
    counts = result.get_counts()
    print('测量分布:', counts)

if __name__ == '__main__':
    main() 