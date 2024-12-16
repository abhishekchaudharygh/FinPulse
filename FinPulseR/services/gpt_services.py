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
        """
        Initialize the ExpenseAnalyzer class.
        :param api_key: OpenAI API key
        """
        openai.api_key = api_key

    @staticmethod
    def create_visualizations(expenses_df):
        """
        Create visualizations for the expense data.
        :param expenses_df: DataFrame containing expense data
        :return: Base64 encoded image string
        """
        plt.figure(figsize=(8, 6))
        sns.barplot(x='category', y='amount', data=expenses_df, errorbar=None)
        plt.title("Spending by Category")
        plt.xlabel("Category")
        plt.ylabel("Amount")
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        return image_base64

    @staticmethod
    async def query_gpt(prompt):
        """
        Query the GPT API with a given prompt.
        :param prompt: The prompt to send to GPT
        :return: GPT response text
        """
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
    def create_email_content(analysis_text, image_base64):
        """
        Create the HTML content for the email.
        :param analysis_text: Insights generated by GPT
        :param image_base64: Base64 encoded image string
        :return: HTML email content
        """
        email_template = """
        <html>
            <body>
                <h2>Monthly Expense Analysis</h2>
                <p>{{ analysis_text }}</p>
                <h3>Spending by Category</h3>
                <img src="data:image/png;base64,{{ image_base64 }}" alt="Spending by Category">
            </body>
        </html>
        """
        template = Template(email_template)
        return template.render(analysis_text=analysis_text, image_base64=image_base64)

    async def analyze_expenses(self, data):
        """
        Analyze expense data, generate insights, and prepare HTML content.
        :param data: Dictionary containing expense data and category limits
        :return: HTML email content
        """
        # Convert expenses to a DataFrame
        expenses_df = pd.DataFrame(data["expenses"])
        expenses_df['date'] = pd.to_datetime(expenses_df['date'])
        expenses_df['month'] = expenses_df['date'].dt.to_period('M')

        # Create visualizations
        image_base64 = self.create_visualizations(expenses_df)

        # Generate insights using GPT
        prompt = f"""
        Analyze the following data for the current month: {expenses_df.to_dict(orient='records')}
        and compare it to category limits {data['category_monthly_limits']}.
        Provide insights in tabular format and suggestions to manage spending.
        """
        analysis_text = await self.query_gpt(prompt)

        # Create email content
        email_html = self.create_email_content(analysis_text, image_base64)
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
        ],
        "category_monthly_limits": {"Food": 3000, "Rent": 5000},
    }

    # Run analysis
    async def main():
        analyzer = ExpenseAnalyzer(api_key=os.getenv("OPENAI_API_KEY"))
        email_content = await analyzer.analyze_expenses(data)
        print(email_content)  # Debugging: Print the generated email HTML

    asyncio.run(main())
