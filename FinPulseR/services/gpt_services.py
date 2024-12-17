import openai
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from jinja2 import Template
import os
from dotenv import load_dotenv

load_dotenv()


class ExpenseAnalyzer:
    def __init__(self, api_key):
        openai.api_key = api_key

    @staticmethod
    def create_visualizations(expenses_df):
        # Spending by category
        plt.figure(figsize=(8, 6))
        sns.barplot(x='category', y='amount', data=expenses_df, errorbar=None)
        plt.title("Spending by Category")
        plt.xlabel("Category")
        plt.ylabel("Amount")
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        category_image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        # Spending pattern throughout the month
        plt.figure(figsize=(10, 6))
        expenses_df['day'] = expenses_df['date'].dt.day
        sns.lineplot(x='day', y='amount', data=expenses_df, marker="o")
        plt.title("Spending Pattern Throughout the Month")
        plt.xlabel("Day of Month")
        plt.ylabel("Amount Spent")
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        pattern_image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        # Current month vs average of last 5 months
        monthly_totals = expenses_df.groupby('month')['amount'].sum().reset_index()
        last_six_months = monthly_totals.tail(6)
        current_month = last_six_months.iloc[-1]
        avg_last_five_months = last_six_months.iloc[:-1]['amount'].mean()

        plt.figure(figsize=(8, 6))
        sns.barplot(x=['Last 5 Months Average', 'Current Month'], y=[avg_last_five_months, current_month['amount']])
        plt.title("Current Month Spending vs Last 5 Months Average")
        plt.ylabel("Amount Spent")
        plt.xlabel("")
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        comparison_image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        return category_image_base64, pattern_image_base64, comparison_image_base64

    @staticmethod
    async def query_gpt(prompt):
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            return response['choices'][0]['message']['content']
        except openai.OpenAIError as e:
            return f"Error: {str(e)}"

    @staticmethod
    def create_email_content(analysis_table, category_image_base64, pattern_image_base64, comparison_image_base64):
        email_template = """
        <html>
            <head>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: #f9f9f9;
                        color: #333;
                    }
                    h2, h3 {
                        text-align: center;
                        color: #444;
                    }
                    .container {
                        width: 80%;
                        margin: 0 auto;
                        background: #fff;
                        padding: 20px;
                        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                        border-radius: 8px;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin: 20px 0;
                    }
                    table th, table td {
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: center;
                    }
                    table th {
                        background-color: #f4f4f4;
                        color: #555;
                    }
                    img {
                        display: block;
                        margin: 20px auto;
                        max-width: 100%;
                        border-radius: 8px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Monthly Expense Analysis</h2>
                    <h3>Spending Insights</h3>
                    {{ analysis_table }}
                    <h3>Spending by Category</h3>
                    <img src="data:image/png;base64,{{ category_image_base64 }}" alt="Spending by Category">
                    <h3>Spending Pattern Throughout the Month</h3>
                    <img src="data:image/png;base64,{{ pattern_image_base64 }}" alt="Spending Pattern Throughout the Month">
                    <h3>Current Month Spending vs Last 5 Months Average</h3>
                    <img src="data:image/png;base64,{{ comparison_image_base64 }}" alt="Spending Comparison">
                </div>
            </body>
        </html>
        """
        template = Template(email_template)
        return template.render(
            analysis_table=analysis_table,
            category_image_base64=category_image_base64,
            pattern_image_base64=pattern_image_base64,
            comparison_image_base64=comparison_image_base64
        )

    async def analyze_expenses(self, data):
        # Convert expenses to a DataFrame
        expenses_df = pd.DataFrame(data["expenses"])
        expenses_df['date'] = pd.to_datetime(expenses_df['date'])
        expenses_df['month'] = expenses_df['date'].dt.to_period('M')

        # Create visualizations
        category_image_base64, pattern_image_base64, comparison_image_base64 = self.create_visualizations(expenses_df)

        # Generate insights using GPT
        prompt = f"""
        Analyze the following data for the last six months: {expenses_df.to_dict(orient='records')}
        and compare the current month's total spending to the average of the last five months.
        Compare spending by category to category limits {data['category_monthly_limits']}.
        Provide insights in the following HTML table format, 
        Also analyse the data and provide insights to the me about my expenses styles and how can I improve provide this insights in html bullets points.

        <table>
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Total Spending</th>
                    <th>Category Limit</th>
                    <th>Exceeded Limit?</th>
                </tr>
            </thead>
            <tbody>
                <!-- Fill rows here -->
            </tbody>
        </table>

        Always return a valid HTML table.
        """
        analysis_table = await self.query_gpt(prompt)
        print(analysis_table)

        # Create email content
        email_html = self.create_email_content(
            analysis_table, category_image_base64, pattern_image_base64, comparison_image_base64
        )
        return email_html


# Example Usage
if __name__ == "__main__":
    import asyncio

    # Example data
    data = {
        "expenses": [
            {"id": 28, "amount": 1200.0, "category": "Rent", "date": "2024-12-13", "description": "cretine"},
            {"id": 29, "amount": 500.0, "category": "Food", "date": "2024-12-13", "description": "Eat food at dominos"},
            {"id": 30, "amount": 40.0, "category": "Food", "date": "2024-12-13", "description": "Eat bhelpuri"},
            {"id": 31, "amount": 40.0, "category": "Food", "date": "2024-12-16", "description": "Eat bhelpuri"},
            {"id": 32, "amount": 4000.0, "category": "Food", "date": "2024-12-16", "description": "Eat bhelpuri"},
            {"id": 33, "amount": 1000.0, "category": "Food", "date": "2024-12-16", "description": "Eat bhelpuri"},
            {"id": 34, "amount": 1534.82, "category": "Entertainment", "date": "2024-11-20",
             "description": "Gym subscription"},
            {"id": 35, "amount": 4738.44, "category": "Utilities", "date": "2024-11-17",
             "description": "Electricity bill"},
            {"id": 36, "amount": 331.88, "category": "Food", "date": "2024-11-16", "description": "Gym subscription"},
            {"id": 37, "amount": 90.21, "category": "Utilities", "date": "2024-12-07",
             "description": "Gym subscription"},
            {"id": 38, "amount": 1186.48, "category": "Utilities", "date": "2024-11-17",
             "description": "Electricity bill"},
            {"id": 39, "amount": 2824.5, "category": "Food", "date": "2024-12-01",
             "description": "Coffee at Starbucks"},
            {"id": 40, "amount": 1914.26, "category": "Food", "date": "2024-12-11", "description": "Bought snacks"},
            {"id": 41, "amount": 3746.48, "category": "Entertainment", "date": "2024-12-09",
             "description": "Gym subscription"},
            {"id": 42, "amount": 2018.31, "category": "Entertainment", "date": "2024-12-08",
             "description": "Electricity bill"},
            {"id": 43, "amount": 4363.56, "category": "Entertainment", "date": "2024-12-13",
             "description": "Gym subscription"},
            {"id": 44, "amount": 3666.81, "category": "Transport", "date": "2024-12-13", "description": "Bus ticket"},
            {"id": 45, "amount": 4186.39, "category": "Rent", "date": "2024-11-24",
             "description": "Coffee at Starbucks"},
            {"id": 46, "amount": 237.97, "category": "Rent", "date": "2024-12-08", "description": "Gym subscription"},
            {"id": 47, "amount": 174.64, "category": "Transport", "date": "2024-12-14", "description": "Bought snacks"},
            {"id": 48, "amount": 3272.18, "category": "Rent", "date": "2024-11-29",
             "description": "Coffee at Starbucks"},
            {"id": 49, "amount": 2390.96, "category": "Transport", "date": "2024-11-22", "description": "Paid rent"},
            {"id": 50, "amount": 3009.41, "category": "Rent", "date": "2024-10-29",
             "description": "Coffee at Starbucks"},
            {"id": 51, "amount": 3927.28, "category": "Food", "date": "2024-10-17", "description": "Bought snacks"},
            {"id": 52, "amount": 3538.21, "category": "Entertainment", "date": "2024-11-13",
             "description": "Dinner with friends"},
            {"id": 53, "amount": 2265.07, "category": "Utilities", "date": "2024-10-29",
             "description": "Dinner with friends"},
            {"id": 54, "amount": 4992.12, "category": "Entertainment", "date": "2024-10-31",
             "description": "Dinner with friends"},
            {"id": 55, "amount": 4761.28, "category": "Transport", "date": "2024-11-13",
             "description": "Gym subscription"},
            {"id": 56, "amount": 919.95, "category": "Food", "date": "2024-10-18", "description": "Grocery shopping"},
            {"id": 57, "amount": 2723.74, "category": "Utilities", "date": "2024-11-07",
             "description": "Electricity bill"},
            {"id": 58, "amount": 268.91, "category": "Food", "date": "2024-11-01",
             "description": "Coffee at Starbucks"},
            {"id": 59, "amount": 480.1, "category": "Utilities", "date": "2024-10-23", "description": "Paid rent"},
            {"id": 60, "amount": 295.67, "category": "Rent", "date": "2024-10-21", "description": "Grocery shopping"},
            {"id": 61, "amount": 513.95, "category": "Entertainment", "date": "2024-11-02",
             "description": "Dinner with friends"},
            {"id": 62, "amount": 4084.52, "category": "Rent", "date": "2024-10-27", "description": "Bought snacks"},
            {"id": 63, "amount": 239.45, "category": "Transport", "date": "2024-10-22",
             "description": "Dinner with friends"},
            {"id": 64, "amount": 1959.0, "category": "Rent", "date": "2024-10-27",
             "description": "Dinner with friends"},
            {"id": 65, "amount": 3604.7, "category": "Food", "date": "2024-11-09", "description": "Gym subscription"},
            {"id": 66, "amount": 3103.26, "category": "Entertainment", "date": "2024-11-14",
             "description": "Gym subscription"},
            {"id": 67, "amount": 4945.05, "category": "Transport", "date": "2024-11-02",
             "description": "Grocery shopping"},
            {"id": 68, "amount": 1857.4, "category": "Entertainment", "date": "2024-09-23",
             "description": "Electricity bill"},
            {"id": 69, "amount": 2009.36, "category": "Food", "date": "2024-10-10", "description": "Bought snacks"},
            {"id": 70, "amount": 3503.17, "category": "Rent", "date": "2024-09-30", "description": "Bought snacks"},
            {"id": 71, "amount": 2018.42, "category": "Entertainment", "date": "2024-10-08",
             "description": "Grocery shopping"},
            {"id": 72, "amount": 1841.29, "category": "Food", "date": "2024-09-24", "description": "Gym subscription"},
            {"id": 73, "amount": 851.46, "category": "Transport", "date": "2024-10-10", "description": "Movie night"},
            {"id": 74, "amount": 4507.1, "category": "Transport", "date": "2024-10-02", "description": "Bought snacks"},
            {"id": 75, "amount": 1243.65, "category": "Transport", "date": "2024-10-03",
             "description": "Electricity bill"},
            {"id": 76, "amount": 4088.95, "category": "Transport", "date": "2024-09-26",
             "description": "Gym subscription"},
            {"id": 77, "amount": 4696.09, "category": "Entertainment", "date": "2024-10-13",
             "description": "Electricity bill"},
            {"id": 78, "amount": 4938.72, "category": "Transport", "date": "2024-10-08",
             "description": "Bought snacks"},
            {"id": 79, "amount": 3797.02, "category": "Transport", "date": "2024-09-26",
             "description": "Dinner with friends"},
            {"id": 80, "amount": 4536.88, "category": "Food", "date": "2024-10-04", "description": "Grocery shopping"},
            {"id": 81, "amount": 750.18, "category": "Food", "date": "2024-09-12", "description": "Paid rent"},
            {"id": 82, "amount": 1528.55, "category": "Food", "date": "2024-08-27", "description": "Bought snacks"},
            {"id": 83, "amount": 2626.77, "category": "Entertainment", "date": "2024-08-29",
             "description": "Electricity bill"},
            {"id": 84, "amount": 783.77, "category": "Utilities", "date": "2024-08-26", "description": "Movie night"},
            {"id": 85, "amount": 1870.71, "category": "Utilities", "date": "2024-09-09", "description": "Bus ticket"},
            {"id": 86, "amount": 4691.35, "category": "Food", "date": "2024-08-30", "description": "Paid rent"},
            {"id": 87, "amount": 992.62, "category": "Utilities", "date": "2024-08-23",
             "description": "Coffee at Starbucks"}
        ],
        "category_monthly_limits": {"Food": 3000, "Rent": 5000, "Entertainment": 5000, "Utilities": 6000, "Transport": 5000},
    }

    # Run analysis
    async def main():
        analyzer = ExpenseAnalyzer(api_key=os.getenv("OPENAI_API_KEY"))
        email_content = await analyzer.analyze_expenses(data)

        filename = 'email.html'
        with open(filename, 'w') as file:
            file.write(email_content)

    asyncio.run(main())
