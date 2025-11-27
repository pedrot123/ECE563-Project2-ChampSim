import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

PROJECT_DIR = Path("/Users/pedro/Desktop/Coursework/Comp_Arch/Project_2")
CHAMPSIM_ROOT = Path("/Users/pedro/ChampSim")
LOGS_DIR = Path("logs")

CONFIGS = [
    "configs/baseline_config.json", # Default JSON with 4 cores
]

TRACES = [
    "workloads/602.gcc_s-1850B.champsimtrace.xz",
    "workloads/605.mcf_s-472B.champsimtrace.xz",
    "workloads/623.xalancbmk_s-10B.champsimtrace.xz",
]

# Simulation parameters
WARMUP_INSTR = "20000000"
SIM_INSTR    = "80000000"

def run_trace(cmd, out_file):
    with out_file.open("w") as f:
        subprocess.run(
            cmd,
            cwd=CHAMPSIM_ROOT,
            stdout=f,
            stderr=subprocess.STDOUT,
            check=True,
        )
    print(f"Output saved to {out_file}")


def main():
    for config_path in CONFIGS:
        config_path = PROJECT_DIR / Path(config_path)
        config_name = config_path.stem

        print(f"\n==============================")
        print(f" Config: {config_path}")
        print(f"==============================")

        # Configure ChampSim
        subprocess.run(
            ["./config.sh", str(config_path)],
            cwd=CHAMPSIM_ROOT,
            check=True
        )

        # Build ChampSim
        subprocess.run(
            ["make", "-j"],
            cwd=CHAMPSIM_ROOT,
            check=True
        )

        # Run all 3 workloads in concurrently so im not here for 10 million years
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []

            for trace in TRACES:
                trace_path = PROJECT_DIR / Path(trace)
                trace_label = trace_path.name
                trace_stem  = trace_path.stem

                out_file = PROJECT_DIR / LOGS_DIR / f"{config_name}__{trace_stem}.log"

                print(f"\n--- Running trace {trace_label} with config {config_name}")
                print(f"-> log: {out_file}")

                # Build champsim command
                # One trace per core
                cmd = [
                    "bin/champsim",
                    "--warmup-instructions", WARMUP_INSTR,
                    "--simulation-instructions", SIM_INSTR,
                    str(trace_path),
                    str(trace_path),
                    str(trace_path),
                    str(trace_path)
                ]

                futures.append(
                    executor.submit(run_trace, cmd, out_file)
                )

            for f in futures:
                f.result()


    print("\nAll runs completed.")

if __name__ == "__main__":
    main()
