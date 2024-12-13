import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import Image as ReportLabImage
import numpy as np
from io import BytesIO

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def create_bar_graph(self, categories, money_spent, budget, title):
        """
        Creates a bar graph comparing money spent and budget for given categories.

        Args:
            categories (list): List of category names.
            money_spent (list): List of amounts spent for each category.
            budget (list): List of budget amounts for each category.
            title (str): Title of the graph.

        Returns:
            BytesIO: In-memory image of the graph.
        """
        x = np.arange(len(categories))
        bar_width = 0.4

        plt.figure(figsize=(10, 6))
        plt.bar(x - bar_width / 2, money_spent, width=bar_width, label="Money Spent", color="skyblue")
        plt.bar(x + bar_width / 2, budget, width=bar_width, label="Budget", color="orange")

        plt.xlabel("Categories")
        plt.ylabel("Amount (in currency)")
        plt.title(title)
        plt.xticks(x, categories)
        plt.legend()

        plt.tight_layout()
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        plt.close()
        buffer.seek(0)
        return buffer

    def create_bullet_chart(self, month_expenses, avg_month_expenses, title):
        """
        Creates a bullet chart comparing this month's expenses to the average monthly expenses.

        Args:
            month_expenses (float): This month's expenses.
            avg_month_expenses (float): Average monthly expenses.
            title (str): Title of the chart.

        Returns:
            BytesIO: In-memory image of the chart.
        """
        plt.figure(figsize=(10, 2))
        plt.barh([0], [avg_month_expenses], color='lightgrey', label=f'Average Monthly Expenses: {avg_month_expenses}', height=0.5)
        plt.barh([0], [month_expenses], color='skyblue', label=f'This Month\'s Expenses: {month_expenses}', height=0.3)

        plt.xlabel("Expenses (in currency)")
        plt.title(title)
        plt.yticks([])  # Remove y-axis ticks
        plt.legend(loc='upper right')

        plt.tight_layout()
        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        plt.close()
        buffer.seek(0)
        return buffer

    def generate_pdf(self, output_filename, title, intro_text, graphs, concluding_text):
        """
        Generates a PDF report with the given title, text, and graphs.

        Args:
            output_filename (str): Name of the output PDF file.
            title (str): Title of the report.
            intro_text (str): Introductory text for the report.
            graphs (list): List of tuples (graph_title, graph_buffer).
            concluding_text (str): Concluding text for the report.
        """
        doc = SimpleDocTemplate(output_filename, pagesize=letter)
        elements = []

        # Add title
        elements.append(Paragraph(title, self.styles['Title']))
        elements.append(Spacer(1, 20))

        # Add introductory text
        elements.append(Paragraph(intro_text, self.styles['BodyText']))
        elements.append(Spacer(1, 20))

        # Add graphs
        for graph_title, graph_buffer in graphs:
            elements.append(Paragraph(graph_title, self.styles['Heading2']))
            elements.append(Spacer(1, 10))
            elements.append(ReportLabImage(graph_buffer, width=400, height=200))
            elements.append(Spacer(1, 20))

        # Add concluding text
        elements.append(Paragraph(concluding_text, self.styles['BodyText']))

        # Build the PDF
        doc.build(elements)