# Disaster-relief-distribution-system-using-knapsack-fraction
<img width="1856" height="922" alt="Image" src="https://github.com/user-attachments/assets/dbfc5b39-e60c-4653-b0c8-d929c29180e6" />

<img width="1191" height="508" alt="Image" src="https://github.com/user-attachments/assets/8d52d199-43d1-4593-af28-d23a61cadf6d" />
---
title: Disaster Relief Resource Allocation
emoji: 🚚
colorFrom: blue
colorTo: green
sdk: gradio
app_file: app.py
pinned: false
---

# Disaster Relief Resource Allocation

A Python + Gradio project that demonstrates the Fractional Knapsack algorithm for disaster relief logistics. The app helps allocate limited truck capacity across relief items such as water, medicine, blankets, and food packets based on their importance-to-weight ratio.

## Features

- Fractional Knapsack allocation
- Multi-truck resource distribution
- CSV upload support
- Built-in default dataset
- Gradio-based interactive interface
- Bar and pie chart visualizations

## Project Structure

```text
DAA PBL/
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

## Run The App

```bash
python app.py
```

After running the command, Gradio will start a local web app and print a local URL in the terminal.

## Live Demo

Add your deployed app link here so visitors can open the interface directly from GitHub:

```md
[Live Demo](https://your-live-demo-url)
```

Recommended hosting options for this Gradio app:

- Hugging Face Spaces
- Render
- Railway

Once the app is deployed, replace `https://your-live-demo-url` with the public URL.

## CSV Format

Upload a CSV file with these columns:

```csv
Item,Weight,Importance
Rice,100,60
Water,250,100
Medicine,310,120
```

Column rules:

- `Item`: name of the relief item
- `Weight`: weight of the item
- `Importance`: priority or utility score of the item

## Example Input

A sample dataset is included in `data/sample_resources.csv`.

## Notes For GitHub Upload

- Do not upload `venv/`
- Do not upload `.gradio/`
- Install dependencies from `requirements.txt` after cloning

## Tech Stack

- Python
- Gradio
- Pandas
- Matplotlib
- Pillow
