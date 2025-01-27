import yfinance as yf
import re
import pandas as pd


import warnings
warnings.filterwarnings("ignore")

class FinancialKPIs:
    def __init__(self, ticker):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        self.financials = self.stock.financials
        self.balance_sheet = self.stock.balance_sheet
        self.cashflow = self.stock.cashflow
        self.info = self.stock.info

        # Rename the columns to year
        self.financials.columns = [col.year for col in self.financials.columns]
        self.balance_sheet.columns = [col.year for col in self.balance_sheet.columns]
        self.cashflow.columns = [col.year for col in self.cashflow.columns]

    def get_years_of_data(self):
        return list(self.financials.columns)

    def get_financial_kpis(self, years):
        kpis = {}
        for i, year in enumerate(years):
            if year in self.financials.columns:
                kpis[f'Total Revenue {year}'] = self.financials.loc['Total Revenue'][year] if 'Total Revenue' in self.financials.index else 'N/A'
                if i < len(years) - 1:
                    next_year = years[i + 1]
                    kpis[f'Revenue Growth Rate {year}'] = ((self.financials.loc['Total Revenue'][year] - self.financials.loc['Total Revenue'][next_year]) / self.financials.loc['Total Revenue'][next_year] * 100) if 'Total Revenue' in self.financials.index else 'N/A'
                kpis[f'Gross Profit {year}'] = self.financials.loc['Gross Profit'][year] if 'Gross Profit' in self.financials.index else 'N/A'
                kpis[f'Gross Margin {year}'] = (kpis[f'Gross Profit {year}'] / kpis[f'Total Revenue {year}'] * 100) if kpis[f'Gross Profit {year}'] != 'N/A' and kpis[f'Total Revenue {year}'] != 'N/A' else 'N/A'
                kpis[f'Net Profit {year}'] = self.financials.loc['Net Income'][year] if 'Net Income' in self.financials.index else 'N/A'
                kpis[f'Net Profit Margin {year}'] = (kpis[f'Net Profit {year}'] / kpis[f'Total Revenue {year}'] * 100) if kpis[f'Net Profit {year}'] != 'N/A' and kpis[f'Total Revenue {year}'] != 'N/A' else 'N/A'
                kpis[f'EBITDA {year}'] = self.financials.loc['EBITDA'][year] if 'EBITDA' in self.financials.index else 'N/A'
                kpis[f'Operating Profit Margin {year}'] = (self.financials.loc['Operating Income'][year] / kpis[f'Total Revenue {year}'] * 100) if 'Operating Income' in self.financials.index else 'N/A'
        return kpis

    def get_cost_and_expense_kpis(self, years):
        kpis = {}
        for year in years:
            if year in self.financials.columns:
                kpis[f'Cost of Goods Sold (COGS) {year}'] = self.financials.loc['Cost Of Revenue'][year] if 'Cost Of Revenue' in self.financials.index else 'N/A'
                kpis[f'Operating Expenses (OPEX) {year}'] = self.financials.loc['Operating Expense'][year] if 'Operating Expense' in self.financials.index else 'N/A'
                kpis[f'Cost-to-Revenue Ratio {year}'] = (kpis[f'Operating Expenses (OPEX) {year}'] / self.financials.loc['Total Revenue'][year] * 100) if kpis[f'Operating Expenses (OPEX) {year}'] != 'N/A' and 'Total Revenue' in self.financials.index else 'N/A'
        return kpis

    def get_cash_flow_kpis(self, years):
        kpis = {}
        for year in years:
            if year in self.cashflow.columns:
                kpis[f'Free Cash Flow (FCF) {year}'] = self.cashflow.loc['Free Cash Flow'][year] if 'Free Cash Flow' in self.cashflow.index else 'N/A'
                kpis[f'Operating Cash Flow {year}'] = self.cashflow.loc['Operating Cash Flow'][year] if 'Operating Cash Flow' in self.cashflow.index else 'N/A'
        return kpis

    def get_balance_sheet_kpis(self, years):
        kpis = {}
        for year in years:
            if year in self.balance_sheet.columns:
                kpis[f'Total Assets {year}'] = self.balance_sheet.loc['Total Assets'][year] if 'Total Assets' in self.balance_sheet.index else 'N/A'
                kpis[f'Total Liabilities {year}'] = self.balance_sheet.loc['Total Liabilities Net Minority Interest'][year] if 'Total Liabilities Net Minority Interest' in self.balance_sheet.index else 'N/A'
                kpis[f'Equity {year}'] = kpis[f'Total Assets {year}'] - kpis[f'Total Liabilities {year}'] if kpis[f'Total Assets {year}'] != 'N/A' and kpis[f'Total Liabilities {year}'] != 'N/A' else 'N/A'
                kpis[f'Debt-to-Equity Ratio {year}'] = kpis[f'Total Liabilities {year}'] / kpis[f'Equity {year}'] if kpis[f'Equity {year}'] != 'N/A' else 'N/A'
                kpis[f'Current Ratio {year}'] = self.balance_sheet.loc['Current Assets'][year] / self.balance_sheet.loc['Current Liabilities'][year] if 'Current Assets' in self.balance_sheet.index and 'Current Liabilities' in self.balance_sheet.index else 'N/A'
        return kpis

    def get_market_kpis(self):
        # Market KPIs are typically current values and not historical
        kpis = {}
        kpis['Market Capitalization'] = self.info['marketCap'] if 'marketCap' in self.info else 'N/A'
        kpis['Enterprise Value (EV)'] = self.info['enterpriseValue'] if 'enterpriseValue' in self.info else 'N/A'
        kpis['Price-to-Earnings (P/E) Ratio'] = self.info['trailingPE'] if 'trailingPE' in self.info else 'N/A'
        return kpis

    def get_performance_kpis(self):
        # Performance KPIs are typically current values and not historical
        kpis = {}
        kpis['Return on Assets (ROA)'] = self.info['returnOnAssets'] if 'returnOnAssets' in self.info else 'N/A'
        kpis['Return on Equity (ROE)'] = self.info['returnOnEquity'] if 'returnOnEquity' in self.info else 'N/A'
        return kpis
    
    def get_all(self):
        years_of_data = self.get_years_of_data()
        print(f"Years of data available: {years_of_data}")
        results_data={}
        if len(years_of_data) >= 3:
            last_3_years = years_of_data[:3]
            
            financial_kpis=self.get_financial_kpis(last_3_years)
            results_data["financial_kpis"]=financial_kpis
            
            cost_and_expense_kpis=self.get_cost_and_expense_kpis(last_3_years)
            results_data["cost_and_expense_kpis"]=cost_and_expense_kpis
            
            cash_flow_kpis=self.get_cash_flow_kpis(last_3_years)
            results_data["cash_flow_kpis"]=cash_flow_kpis
            
            balance_sheet_kpis=self.get_balance_sheet_kpis(last_3_years)
            results_data["balance_sheet_kpis"]=balance_sheet_kpis
            
            performance_kpis=self.get_performance_kpis()
            results_data["performance_kpis"]=performance_kpis
            
            market_kpis=self.get_market_kpis()
            results_data["market_kpis"]=market_kpis
            return results_data
        else:
            return "Not enough data available for the last 3 years."

def data_preprocessing(financial_details):
    str_data={"kpi_names":[],"years":[],"values":[]}
    for key in financial_details.keys():
        keys_data=financial_details[key]
        for key, value in keys_data.items():
            match = re.search(r"(\d{4})$", key)  # Check for year at the end
            if match:
                year = match.group(1)
                kpi_name = key[:match.start()].strip()
            else:
                # Handle KPIs without a year
                year= "N/A"
                kpi_name=key

            str_data['kpi_names'].append(kpi_name)
            str_data['years'].append(year)
            str_data['values'].append(value)
    
    df=pd.DataFrame(str_data)
    df["years"].replace({"N/A":df[df['years']!="N/A"]['years'].max()},inplace=True)
    # Perform pivot
    pivot_df = df.pivot(index="kpi_names", columns="years", values="values")
    financial_details2=pivot_df.to_csv()
    return financial_details2


# Dictionary containing all the KPIs mentioned
kpi_dictionary = {
    "Financial KPIs": {
        "Total Revenue": "Total income generated by the company from its operations.",
        "Revenue Growth Rate": "Percentage increase in revenue over a specific period.",
        "Recurring Revenue (ARR/MRR)": "Annual or monthly recurring revenue generated by subscriptions or recurring customers.",
        "Revenue per Customer": "Average revenue earned per customer over a specific period.",
        "Gross Profit": "Total revenue minus the cost of goods sold (COGS).",
        "Gross Margin": "Gross profit as a percentage of total revenue.",
        "Net Profit": "Total revenue minus all expenses, taxes, and costs.",
        "Net Profit Margin": "Net profit as a percentage of total revenue.",
        "EBITDA": "Earnings before interest, taxes, depreciation, and amortization.",
        "Operating Profit Margin": "Operating income as a percentage of revenue."
    },
    "Cost and Expense KPIs": {
        "Cost of Goods Sold (COGS)": "Direct costs of producing goods or services sold by the company.",
        "Operating Expenses (OPEX)": "Expenses incurred during normal business operations.",
        "Cost-to-Revenue Ratio": "Operating expenses as a proportion of total revenue."
    },
    "Cash Flow KPIs": {
        "Free Cash Flow (FCF)": "Cash generated after accounting for capital expenditures.",
        "Operating Cash Flow": "Cash generated from regular business operations.",
        "Cash Conversion Cycle (CCC)": "Time taken to convert inventory into cash through sales."
    },
    "Balance Sheet KPIs": {
        "Total Assets": "Total value of assets owned by the company.",
        "Total Liabilities": "Total value of liabilities owed by the company.",
        "Equity": "Difference between total assets and total liabilities.",
        "Debt-to-Equity Ratio": "Measure of financial leverage calculated by dividing total liabilities by equity.",
        "Current Ratio": "Measure of liquidity calculated by dividing current assets by current liabilities."
    },
    "Market KPIs": {
        "Market Capitalization": "Total market value of a company's outstanding shares.",
        "Enterprise Value (EV)": "Measure of a company's total value, including debt and equity.",
        "Price-to-Earnings (P/E) Ratio": "Valuation ratio comparing a company's current share price to its earnings per share."
    },
    "Performance KPIs": {
        "Return on Assets (ROA)": "Net income as a percentage of total assets.",
        "Return on Equity (ROE)": "Net income as a percentage of shareholder's equity.",
        "Asset Turnover Ratio": "Efficiency ratio that shows how effectively assets are used to generate revenue."
    },
    "Customer KPIs": {
        "Customer Acquisition Cost (CAC)": "Cost associated with acquiring a new customer.",
        "Lifetime Value (LTV)": "Predicted revenue a customer will generate during their lifetime.",
        "LTV-to-CAC Ratio": "Comparison of the lifetime value of a customer to the cost of acquiring them."
    }
}