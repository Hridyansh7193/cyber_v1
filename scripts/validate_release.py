import os
import sys
import time
import json
import argparse
import importlib
from typing import List, Dict, Any, Type

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.validators.utils import ValidationResult, ValidatorStatus, logger
from scripts.validators.base_validator import BaseValidator
from scripts.validators.command_runner import CommandRunner

MODES = {
    "quick": ["V000", "V001", "V003", "V004"],
    "standard": ["V000", "V001", "V003", "V004", "V005", "V006", "V008"],
    "ci": ["V000", "V002", "V003", "V006", "V004", "V011"],
    "full": None  # None means run everything
}

def load_config() -> Dict[str, Any]:
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'validation.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def discover_validators() -> List[Type[BaseValidator]]:
    validators = []
    validators_dir = os.path.join(os.path.dirname(__file__), 'validators')
    
    for filename in sorted(os.listdir(validators_dir)):
        if filename.endswith("_validator.py") and filename != "base_validator.py":
            module_name = f"scripts.validators.{filename[:-3]}"
            module = importlib.import_module(module_name)
            if hasattr(module, "VALIDATOR"):
                validators.append(getattr(module, "VALIDATOR"))
    
    # Sort by ID
    validators.sort(key=lambda v: getattr(v, "validator_id", "V999"))
    return validators

def print_summary(results: List[ValidationResult], total_runtime: float):
    print("\n" + "="*50)
    print("Validator Runtime Summary")
    print("="*50)
    
    overall_exit = 0
    for res in results:
        status_name = res.status.name
        print(f"{res.validator_id} {res.name:<20} {status_name:<10} {res.runtime:>6.2f} s")
        if res.status in (ValidatorStatus.FAIL, ValidatorStatus.INTERNAL_ERROR):
            overall_exit = 1
            
    print("-" * 50)
    print(f"Total Runtime: {total_runtime:.2f} s")
    print("="*50 + "\n")
    return overall_exit

def main():
    parser = argparse.ArgumentParser(description="BugHunter Release Validation Framework")
    parser.add_argument("--mode", choices=["quick", "standard", "full", "ci"], default="full", help="Validation mode")
    args = parser.parse_args()

    logger.info(f"Starting BugHunter Release Validation in '{args.mode}' mode...")
    
    config = load_config()
    runner = CommandRunner()
    
    validator_classes = discover_validators()
    
    allowed_ids = MODES[args.mode]
    if allowed_ids is not None:
        validator_classes = [v for v in validator_classes if v.validator_id in allowed_ids or v.validator_id == "V012"]
        # Ensure Summary Validator (V012) and Framework (V000) are always considered if appropriate

    # Track statuses by name and ID for dependency checking
    run_statuses = {}
    results = []
    
    start_time = time.time()

    for VClass in validator_classes:
        instance = VClass(config, runner)
        logger.info(f"Running [{instance.validator_id}] {instance.name}...")
        
        # Check dependencies
        skip = False
        failed_dep = ""
        for req in instance.required:
            if run_statuses.get(req, ValidatorStatus.SKIPPED) not in (ValidatorStatus.PASS, ValidatorStatus.WARNING):
                skip = True
                failed_dep = req
                break
                
        if skip:
            logger.warning(f"  -> Skipping due to failed dependency: {failed_dep}")
            res = instance.skip_result(f"Skipped because dependency '{failed_dep}' failed or skipped.")
        else:
            try:
                t0 = time.time()
                res = instance.validate()
                res.runtime = time.time() - t0
            except Exception as e:
                logger.error(f"  -> Internal Error: {e}")
                res = instance.internal_error_result(e)
                
        run_statuses[instance.name.lower()] = res.status
        run_statuses[instance.validator_id] = res.status
        results.append(res)
        
        logger.info(f"  -> Result: {res.status.name} ({res.runtime:.2f}s)")

    total_runtime = time.time() - start_time
    
    # Expose results to summary validator if it was run
    # (The summary validator will load all JSON reports, but in-memory is nice too if needed)
    
    exit_code = print_summary(results, total_runtime)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
