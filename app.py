
import io
import os
import pandas as pd
import matplotlib.pyplot as plt
import gradio as gr
from PIL import Image

# ----------------------------
# Fractional Knapsack Algorithm
# ----------------------------
def fractional_knapsack(df, capacity):
    df = df.copy()
    df["Weight"] = pd.to_numeric(df["Weight"], errors="coerce").fillna(0.0)
    df["Importance"] = pd.to_numeric(df["Importance"], errors="coerce").fillna(0.0)
    # ensure ratio exists for sorting
    df["Importance_per_Weight"] = df["Importance"] / df["Weight"]
    df["Importance_per_Weight"] = df["Importance_per_Weight"].fillna(0.0)

    df = df[df["Weight"] > 0].reset_index(drop=True)
    if df.empty or capacity <= 0:
        return pd.DataFrame(columns=["Item", "Loaded Weight", "Fraction Used", "Utility"])

    df = df.sort_values(by="Importance_per_Weight", ascending=False).reset_index(drop=True)

    remaining = float(capacity)
    result = []

    for _, row in df.iterrows():
        if remaining <= 0:
            break
        weight = float(row["Weight"])
        if weight <= remaining:
            fraction = 1.0
            loaded = weight
        else:
            fraction = remaining / weight
            loaded = remaining

        utility = float(row["Importance"]) * fraction

        result.append({
            "Item": row["Item"],
            "Loaded Weight": round(loaded, 2),
            "Fraction Used": round(fraction, 2),
            "Utility": round(utility, 2)
        })

        remaining -= loaded

    return pd.DataFrame(result)

# ----------------------------
# Multi-Truck Allocation
# ----------------------------
def multi_truck_allocation(df, capacities):
    results = {}
    remaining = df.copy()
    remaining["Weight"] = pd.to_numeric(remaining["Weight"], errors="coerce").fillna(0.0)

    for i, cap in enumerate(capacities, start=1):
        if cap <= 0:
            results[f"Truck {i}"] = pd.DataFrame(columns=["Item", "Loaded Weight", "Fraction Used", "Utility"])
            continue

        res = fractional_knapsack(remaining, cap)
        results[f"Truck {i}"] = res

        # subtract loaded weight from remaining
        for _, row in res.iterrows():
            mask = remaining["Item"] == row["Item"]
            remaining.loc[mask, "Weight"] = remaining.loc[mask, "Weight"] - row["Loaded Weight"]

        remaining = remaining[remaining["Weight"] > 0].reset_index(drop=True)

    return results, remaining

# ----------------------------
# Combined Usage
# ----------------------------
def combined_item_usage(results):
    all_items = []
    for truck, df in results.items():
        if not df.empty:
            temp = df[["Item", "Loaded Weight"]].copy()
            temp["Truck"] = truck
            all_items.append(temp)
    if not all_items:
        return pd.DataFrame(columns=["Item", "Loaded Weight"])
    combined = pd.concat(all_items, ignore_index=True)
    return combined.groupby("Item", as_index=False)["Loaded Weight"].sum()

# ----------------------------
# Plot Helpers (Bar + Pie side-by-side per truck) - FIXED/REPLACED
# ----------------------------
def plot_truck_bar_and_pie(results, figsize=(10,4), dpi=100):
    """
    For each truck in results, create one figure with two subplots:
      - left: bar chart of Loaded Weight per Item
      - right: pie chart of Utility contribution per Item
    Return list of matplotlib figures (not closed).
    """
    figs = []
    # compute a global y-max so bar charts are consistent
    all_weights = []
    for df in results.values():
        if not df.empty:
            all_weights.extend(pd.to_numeric(df.get("Loaded Weight", []), errors="coerce").fillna(0.0).tolist())
    global_max = max(all_weights) if all_weights else 1.0
    y_max = global_max * 1.15

    for truck, df in results.items():
        fig, (ax_bar, ax_pie) = plt.subplots(
            ncols=2, figsize=figsize, dpi=dpi,
            gridspec_kw={"width_ratios":[1,1]}, constrained_layout=False
        )

        # BAR (left)
        if df.empty or df.shape[0] == 0:
            ax_bar.text(0.5, 0.5, "No allocation", ha="center", va="center", fontsize=12)
            ax_bar.axis("off")
        else:
            df_bar = df.copy()
            df_bar["Loaded Weight"] = pd.to_numeric(df_bar["Loaded Weight"], errors="coerce").fillna(0.0)
            items = df_bar["Item"].tolist()
            weights = df_bar["Loaded Weight"].tolist()
            bars = ax_bar.bar(items, weights)
            ax_bar.set_xticks(range(len(items)))
            ax_bar.set_xticklabels(items, rotation=35, ha="right")
            ax_bar.set_ylabel("Loaded Weight (kg)")
            ax_bar.set_ylim(0, max(y_max, max(weights)*1.15 if weights else y_max))
            for rect in bars:
                h = rect.get_height()
                if h > 0:
                    ax_bar.annotate(f"{h:.0f}", xy=(rect.get_x() + rect.get_width()/2, h),
                                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=8)

        ax_bar.set_title(f"{truck} - Loaded Weight per Item")

        # PIE (right)
        if df.empty or "Utility" not in df.columns or df["Utility"].sum() == 0:
            ax_pie.text(0.5, 0.5, "No utility data", ha="center", va="center", fontsize=12)
            ax_pie.axis("off")
        else:
            df_pie = df.copy()
            df_pie = df_pie[df_pie["Utility"] > 0]
            labels = df_pie["Item"].tolist()
            sizes = df_pie["Utility"].tolist()
            ax_pie.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, wedgeprops=dict(edgecolor="w"))
            ax_pie.axis("equal")
            ax_pie.set_title(f"{truck} - Utility Contribution")

        # Let matplotlib adjust spacing so titles/labels don't clip
        fig.tight_layout(pad=1.0)
        figs.append(fig)
        # DO NOT close here; saving function will close after saving
    return figs

def plot_summary(results, figsize=(6,3), dpi=100):
    totals = {truck: (df["Utility"].sum() if ("Utility" in df.columns and not df.empty) else 0.0)
              for truck, df in results.items()}
    labels = list(totals.keys())
    values = list(totals.values())
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.bar(labels, values)
    ax.set_title("Total Utility per Truck")
    ax.set_ylabel("Utility")
    ax.set_xticklabels(labels, rotation=30, ha='right')
    fig.tight_layout(pad=1.0)
    return [fig]

# ----------------------------
# Convert figures to PIL images for Gradio Gallery (fixed pixel size) - FIXED
# ----------------------------
def figs_to_pil_images(figs, out_size=(1000,420), dpi=100):
    imgs = []
    for fig in figs:
        # ensure a final layout pass
        try:
            fig.tight_layout(pad=1.0)
        except Exception:
            pass
        buf = io.BytesIO()
        # save with bbox_inches and small padding to avoid clipping
        fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.12, dpi=dpi)
        buf.seek(0)
        img = Image.open(buf).convert("RGBA")
        # resize to fixed output size so Gradio gallery boxes are uniform
        img = img.resize(out_size, resample=Image.LANCZOS)
        imgs.append(img)
        buf.close()
        # now explicitly close the figure to free memory
        plt.close(fig)
    return imgs

# ----------------------------
# Default Dataset (has Importance_per_Weight)
# ----------------------------
def default_dataset():
    df = pd.DataFrame({
        "Item": ["Rice", "Water", "Medicine", "Blankets", "Food Packets"],
        "Weight": [100, 250, 310, 50, 250],
        "Importance": [60, 100, 120, 80, 90]
    })
    df["Importance_per_Weight"] = df["Importance"] / df["Weight"]
    return df

# ----------------------------
# Robust CSV loader
# ----------------------------
def load_csv(file_obj):
    if file_obj is None:
        raise ValueError("No file provided")

    # try reading from temp path
    try:
        if hasattr(file_obj, "name") and isinstance(file_obj.name, str) and os.path.exists(file_obj.name):
            return pd.read_csv(file_obj.name)
    except Exception:
        pass

    # try reading as bytes or string content
    try:
        raw = None
        try:
            raw = file_obj.read()
        except Exception:
            try:
                raw = file_obj.file.read()
            except Exception:
                raw = None

        if raw is None:
            raise ValueError("Uploaded file could not be read as bytes")

        if isinstance(raw, bytes):
            return pd.read_csv(io.BytesIO(raw))
        else:
            return pd.read_csv(io.StringIO(raw))
    except Exception as e:
        raise ValueError(f"Unable to read uploaded CSV: {e}")

# ----------------------------
# Parse Capacities
# ----------------------------
def parse_caps(text, n):
    try:
        n = int(n)
    except Exception:
        try:
            n = int(float(n))
        except Exception:
            n = 0
    if not text:
        return [0.0] * n
    parts = [p.strip() for p in str(text).replace(";", ",").split(",") if p.strip()]
    caps = []
    for p in parts:
        try:
            caps.append(float(p))
        except:
            caps.append(0.0)
    while len(caps) < n:
        caps.append(0.0)
    return caps[:n]

# ----------------------------
# Run Allocation (robust + consistent outputs)
# ----------------------------
def run_allocation(file_obj, use_default, n_trucks, caps_text):
    # Load dataset
    try:
        if use_default or file_obj is None:
            df = default_dataset()
        else:
            df = load_csv(file_obj)
            # add the ratio column for uploaded CSVs
            df["Importance_per_Weight"] = df["Importance"] / df["Weight"]
    except Exception as e:
        empty_df = pd.DataFrame(columns=["Item", "Weight", "Importance"])
        return (
            f"Error reading CSV: {e}",
            "<b>Error loading file</b>",
            empty_df,
            "",
            "",
            empty_df,
            []
        )

    # Validate columns
    required = {"Item", "Weight", "Importance"}
    if not required.issubset(df.columns):
        empty_df = pd.DataFrame(columns=["Item", "Weight", "Importance"])
        return (
            "CSV must contain Item, Weight, Importance",
            "<b>Error: wrong CSV format</b>",
            empty_df,
            "",
            "",
            empty_df,
            []
        )

    df["Item"] = df["Item"].astype(str)

    # Parse number of trucks as int
    try:
        n_int = int(n_trucks)
    except Exception:
        try:
            n_int = int(float(n_trucks))
        except Exception:
            n_int = 0

    caps = parse_caps(caps_text, n_int)
    results, leftover = multi_truck_allocation(df, caps)
    combined = combined_item_usage(results)

    # Create combined bar+pie figures for each truck
    figs = []
    figs.extend(plot_truck_bar_and_pie(results))
    # also include a small summary if desired
    figs.extend(plot_summary(results))

    gallery_images = figs_to_pil_images(figs, out_size=(1000,420), dpi=100) if figs else []

    # Utilization text lines
    util_lines = []
    for i, (t, df_t) in enumerate(results.items(), start=1):
        used = df_t["Loaded Weight"].sum() if not df_t.empty else 0.0
        cap = caps[i - 1] if i - 1 < len(caps) else 0.0
        util = (used / cap * 100) if cap > 0 else 0.0
        util_lines.append(f"{t}: {used} / {cap} ({util:.1f}%)")

    total_utility = sum((df_t["Utility"].sum() if ("Utility" in df_t.columns and not df_t.empty) else 0.0)
                        for df_t in results.values())

    # Build HTML for allocations (shows whatever columns are present in allocation dfs)
    allocations_html = ""
    for t, df_t in results.items():
        allocations_html += f"<h4>{t}</h4>"
        allocations_html += (df_t.to_html(index=False) if not df_t.empty else "<i>No allocation</i>")

    return (
        "Success",
        allocations_html,
        combined if not combined.empty else pd.DataFrame(columns=["Item", "Loaded Weight"]),
        "\n".join(util_lines),
        f"Total Utility: {total_utility:.2f}",
        leftover if not leftover.empty else pd.DataFrame(columns=["Item", "Weight", "Importance"]),
        gallery_images
    )

# ----------------------------
# Gradio Interface (with Clear Dataset and Reset All buttons)
# ----------------------------
with gr.Blocks() as demo:
    gr.Markdown("## 🚚 Disaster Relief Resource Allocation (Fractional Knapsack)")

    with gr.Row():
        with gr.Column(scale=2):
            file_in = gr.File(label="Upload CSV (optional)")
            use_default = gr.Checkbox(label="Use Default Dataset", value=True)

            show_default_btn = gr.Button("Show Default Dataset")
            default_preview = gr.Dataframe(value=default_dataset(), label="Default Dataset", interactive=False)

            # Clear & Reset buttons
            clear_btn = gr.Button("Clear Dataset")
            reset_all_btn = gr.Button("Reset All")

            n_trucks = gr.Number(label="Number of Trucks", value=2, precision=0)
            capacities = gr.Textbox(label="Truck Capacities", placeholder="e.g. 230, 350, 235")
            run_btn = gr.Button("Run Allocation")

        with gr.Column(scale=1):
            status = gr.Textbox(label="Status")
            allocations_html = gr.HTML()
            combined_table = gr.Dataframe(label="Combined Usage")
            util_text = gr.Textbox(label="Utilization", lines=4, max_lines=10)
            total_util_text = gr.Textbox(label="Total Utility")
            leftover_table = gr.Dataframe(label="Leftover Items")

    # Use single-column gallery for combined bar+pie images and taller height
    gallery = gr.Gallery(label="Plots", columns=1, height=480)

    # show default dataset
    def show_default():
        return default_dataset(), True

    show_default_btn.click(show_default, outputs=[default_preview, use_default])

    # clear dataset: empty dataframe, uncheck use_default, clear file upload
    def clear_dataset():
        empty_df = pd.DataFrame()
        return empty_df, False, None

    clear_btn.click(clear_dataset, outputs=[default_preview, use_default, file_in])

    # reset_all: clear everything (dataset preview, checkbox, file upload, status, html, tables, gallery)
    def reset_all():
        empty_df = pd.DataFrame()
        return (
            empty_df,   # default_preview
            False,      # use_default
            None,       # file_in
            "",         # status
            "",         # allocations_html
            pd.DataFrame(), # combined_table
            "",         # util_text
            "",         # total_util_text
            pd.DataFrame(), # leftover_table
            []          # gallery images
        )

    reset_all_btn.click(
        reset_all,
        outputs=[default_preview, use_default, file_in, status, allocations_html,
                 combined_table, util_text, total_util_text, leftover_table, gallery]
    )

    def on_run(f, d, n, c):
        try:
            n_int = int(n)
        except Exception:
            try:
                n_int = int(float(n))
            except Exception:
                n_int = 0
        return run_allocation(f, d, n_int, c)

    run_btn.click(
        on_run,
        inputs=[file_in, use_default, n_trucks, capacities],
        outputs=[status, allocations_html, combined_table, util_text, total_util_text, leftover_table, gallery]
    )

if __name__ == "__main__":
    demo.launch()
