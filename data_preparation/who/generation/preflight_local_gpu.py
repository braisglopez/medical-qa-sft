import importlib.util
import sys


REQUIRED = ("torch", "unsloth", "transformers")


def main():
    print("[PREFLIGHT] Python:", sys.version.replace("\n", " "))

    missing = [name for name in REQUIRED if importlib.util.find_spec(name) is None]
    if missing:
        raise SystemExit("[PREFLIGHT] Missing Python packages: " + ", ".join(missing))

    import torch

    print("[PREFLIGHT] torch:", torch.__version__)
    print("[PREFLIGHT] cuda available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("[PREFLIGHT] cuda device count:", torch.cuda.device_count())
        print("[PREFLIGHT] cuda device 0:", torch.cuda.get_device_name(0))
    else:
        raise SystemExit("[PREFLIGHT] CUDA is not available in this job.")

    print("[PREFLIGHT] OK")


if __name__ == "__main__":
    main()
