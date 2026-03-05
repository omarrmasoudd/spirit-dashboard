import pandas as pd

file_path = "Spirit_Project_Template_CORRECT.xlsx"

xls = pd.ExcelFile(file_path)

summary = []

for sheet in xls.sheet_names:

    df = pd.read_excel(
        file_path,
        sheet_name=sheet,
        header=2
    )

    total_units = df["Unit Number"].notna().sum()

    sold_units = (
        df["Status"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("sold")
        .sum()
    )

    sales_percentage = (
        (sold_units / total_units) * 100
        if total_units > 0 else 0
    )

    summary.append({
        "Project": sheet,
        "Total Units": total_units,
        "Sold Units": sold_units,
        "Sales %": round(sales_percentage, 1)
    })

summary_df = pd.DataFrame(summary)

# sort best selling projects first
summary_df = summary_df.sort_values(
    by="Sales %",
    ascending=False
)

print(summary_df)