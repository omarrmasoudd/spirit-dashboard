import pandas as pd

def load_portfolio_data(file_path):

    xls = pd.ExcelFile(file_path)

    summary = []
    portfolio_total_value = 0
    portfolio_sold_value = 0

    for sheet in xls.sheet_names:

        df = pd.read_excel(file_path, sheet_name=sheet, header=2)

        total_units = df["Unit Number"].notna().sum()

        sold_units = (
            df["Status"]
            .astype(str)
            .str.lower()
            .eq("sold")
            .sum()
        )

        sales_percentage = (
            (sold_units / total_units) * 100
            if total_units > 0 else 0
        )

        df["Total Unit Price"] = pd.to_numeric(
            df["Total Unit Price"],
            errors="coerce"
        )

        total_value = df["Total Unit Price"].sum()

        sold_value = df[
            df["Status"]
            .astype(str)
            .str.lower() == "sold"
        ]["Total Unit Price"].sum()

        portfolio_total_value += total_value
        portfolio_sold_value += sold_value

        summary.append({
            "Project": sheet,
            "Total Units": total_units,
            "Sold Units": sold_units,
            "Sales %": round(sales_percentage,1),
            "Total Value": total_value,
            "Sold Value": sold_value
        })

    summary_df = pd.DataFrame(summary)

    portfolio_remaining_value = (
        portfolio_total_value - portfolio_sold_value
    )

    return (
        xls,
        summary_df,
        portfolio_total_value,
        portfolio_sold_value,
        portfolio_remaining_value
    )