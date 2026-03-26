# Disaster Relief Distribution System Using Knapsack Fraction

A Python and Gradio based project for optimizing disaster relief distribution using the Fractional Knapsack algorithm. The system allocates limited truck capacity across essential relief items such as water, medicine, blankets, and food packets based on their importance-to-weight ratio.

## Live Demo

[Click here for Live Demo]([https://your-live-demo-url](https://huggingface.co/spaces/Lokeshlokey/Disaster-relief-distribution-system-using-knapsack-fraction)

## How It Works

1. Upload a CSV file or use the built-in sample dataset.
2. Enter the number of trucks.
3. Provide truck capacities as comma-separated values.
4. Run the allocation process.
5. Review item allocation, truck utilization, total utility, leftover items, and generated plots.

## Sample Preview

![Main Interface](https://github.com/user-attachments/assets/dbfc5b39-e60c-4653-b0c8-d929c29180e6)

![Charts and Allocation Output](https://github.com/user-attachments/assets/8d52d199-43d1-4593-af28-d23a61cadf6d)

## Features

- Fractional Knapsack based resource allocation
- Multi-truck distribution support
- CSV upload for custom datasets
- Built-in default dataset for quick testing
- Interactive Gradio user interface
- Visual output with bar charts and pie charts

## Project Structure

```text
Disaster-relief-distribution-system-using-knapsack-fraction/
|-- app.py
|-- requirements.txt
|-- README.md
|-- .gitignore
`-- data/
    `-- sample_resources.csv
```

## Requirements

- Python 3.10 or later
- pip

## Installation

```bash
pip install -r requirements.txt
```

## Run Locally

```bash
python app.py
```

After running the app, Gradio will generate a local URL in the terminal where you can access the interface in your browser.

## CSV Format

The uploaded CSV file must contain the following columns:

```csv
Item,Weight,Importance
Rice,100,60
Water,250,100
Medicine,310,120
```

### Column Description

- `Item`: Name of the relief item
- `Weight`: Weight of the item
- `Importance`: Utility or priority score of the item

## Sample Dataset

A sample dataset is included in `data/sample_resources.csv`.

## Tech Stack

- Python
- Gradio
- Pandas
- Matplotlib
- Pillow

## Notes

- Do not upload `venv/`
- Do not upload `.gradio/`
- Install dependencies from `requirements.txt` after cloning the repository
