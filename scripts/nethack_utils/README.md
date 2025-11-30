# NetHack Utility Data Generation Scripts

This directory contains scripts for generating NetHack runtime data files using the RISC-V simulator.

## Usage

All scripts should be run from the **repository root** (`/home/dev/git/pyrv32`):

```bash
# From repository root
python3 scripts/nethack_utils/run_makedefs_data_v2.py
python3 scripts/nethack_utils/run_makedefs_oracles_v2.py
python3 scripts/nethack_utils/run_makedefs_rumors_v2.py
python3 scripts/nethack_utils/run_makedefs_quest.py
python3 scripts/nethack_utils/run_makedefs_options.py
```

## Files

### Library
- **`nethack_util_runner.py`** - Common library implementing the 7-step clean workflow
  - Step 0: Check initial state
  - Step 1: Clean sim directory
  - Step 2: Copy input files
  - Step 3: Locate argv area
  - Step 4: Run utility in simulator
  - Step 5: Check console output
  - Step 6: Verify output files
  - Step 7: List final state

### Scripts (using refactored library)
- **`run_makedefs_data_v2.py`** - Generate `data` file (53.6M instructions, 205KB)
  - Input: `data.base`
  - Flag: `-d`
  
- **`run_makedefs_oracles_v2.py`** - Generate `oracles` file (1.7M instructions, 5.9KB)
  - Input: `oracles.txt`
  - Flag: `-h`
  
- **`run_makedefs_rumors_v2.py`** - Generate `rumors` file (6.1M instructions, 42KB)
  - Input: `rumors.tru`, `rumors.fal`
  - Flag: `-r`
  
- **`run_makedefs_quest.py`** - Generate `quest.dat` file
  - Input: `quest.txt`
  - Flag: `-q`
  
- **`run_makedefs_options.py`** - Generate `options` file
  - Input: None (compile-time config)
  - Flag: `-v`

## Clean Workflow Pattern

Each script follows a clean, independent workflow:

1. **Cleans** `pyrv32_sim_fs/dat/` completely
2. **Copies** only required input files from `nethack-3.4.3/dat/`
3. **Runs** utility in simulator with proper argv setup
4. **Verifies** output file created with correct size
5. **Shows** console output (if any)
6. **Lists** final filesystem state

This ensures:
- ✅ Independence - each run starts from clean slate
- ✅ Reproducibility - no leftover files affect results
- ✅ Verification - every step is checked
- ✅ Transparency - full visibility into what's happening

## Code Comparison

**Before refactoring:** Each script ~150 lines of duplicated code

**After refactoring:** Each script ~12-17 lines using common library

```python
# Example - simple and clear!
from scripts.nethack_utils.nethack_util_runner import run_makedefs

run_makedefs(
    name="oracles",
    input_files="oracles.txt",
    output_file="oracles",
    flag="-h"
)
```

## Next Steps

After running these scripts:

1. Archive generated files:
   ```bash
   cd nethack-3.4.3/util && make archive-data
   ```

2. Generated files are in `pyrv32_sim_fs/dat/`
3. Archived files go to `nethack_datafiles/usr/games/lib/nethackdir/`
4. Runtime NetHack reads from `pyrv32_sim_fs/usr/games/lib/nethackdir/`

## Adding New Utilities

To add a new utility (e.g., for `lev_comp` or `dgn_comp`):

```python
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.nethack_utils.nethack_util_runner import UtilityRunner

runner = UtilityRunner(
    name="your_utility",
    input_files="input.txt",  # or ["file1.txt", "file2.txt"]
    output_file="output",
    utility_flag="-x",
    binary_path="path/to/utility.bin",
    elf_path="path/to/utility.elf"
)
runner.run()
```

## Legacy Scripts

The original monolithic scripts remain in the repository root:
- `run_makedefs_data.py`
- `run_makedefs_oracles.py`
- `run_makedefs_rumors.py`

These can be kept for reference or removed once the v2 scripts are validated.
