from datetime import datetime, timedelta

from sqlalchemy.orm import aliased

from FinPulseR.models import User, Category, Budget, Expense
from sqlalchemy import func


def get_current_user(email: str, db):
    user_obj = db.query(User).filter(User.email == email).first()
    return user_obj.id


def verify_category(user_id: int, data: dict, db):
    category = data.get("category")

    category_obj = db.query(Category).filter(Category.name == category, Category.user_id == user_id).first()
    if category_obj is None:
        if "monthly_limit" in data and data.get("monthly_limit"):
            category_obj = Category()
            category_obj.name = category
            category_obj.user_id = user_id
            db.add(category_obj)
            db.flush()

            budget_obj = Budget()
            budget_obj.category = category_obj.id
            budget_obj.user_id = user_id
            budget_obj.monthly_limit = data.get("monthly_limit")
            db.add(budget_obj)

            return {"success": True, "message": "Category created successfully"}

        else:
            return {"success": False, "message": "Please provide monthly limit for new category"}
    return {"success": True, "message": "Category already present"}


def verify_monthly_limit(user_id, data: dict, db):
    category_obj = db.query(Category).filter(Category.user_id == user_id, Category.name == data.get("category")).first()
    budget_obj = db.query(Budget).filter(Budget.user_id == user_id, Budget.category == category_obj.id).first()

    budget_for_category = budget_obj.monthly_limit
    total_amount = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == user_id,
        Expense.category == data.get("category")
    ).scalar()

    if budget_for_category <= total_amount:
        return {"limit_reached": True,
                "message": f"Your limit was {budget_for_category} and you have spent {total_amount}"}
    else:
        return {"limit_reached": False,
                "message": f"Currently you can spend {budget_for_category - total_amount} in {data.get('category')}"
}


def get_expenses(user_id: int, db):
    current_date = datetime.now().date()
    first_date = datetime(current_date.year, current_date.month, 1).date()
    expense_obj = db.query(
        Expense.id.label('id'),
        Expense.amount.label('amount'),
        Expense.category.label('category'),
        Expense.date.label('date'),
        Expense.description.label('description')
    ).filter(Expense.user_id == user_id, Expense.date >= first_date,
                                                                Expense.date <= current_date).all()

    return expense_obj


def get_monthly_report_data(user_id: int, db):
    current_date = datetime.now().date()
    first_date = datetime(current_date.year, current_date.month, 1).date()

    CategoryAlias = aliased(Category)
    BudgetAlias = aliased(Budget)

    expenses_in_month = (
        db.query(
            Expense.category.label('expense_category_name'),
            func.sum(Expense.amount).label('total_expense'),
            BudgetAlias.monthly_limit.label('budget_limit')
        )
        .join(CategoryAlias, Expense.category == CategoryAlias.name)
        .join(BudgetAlias, CategoryAlias.id == BudgetAlias.category)
        .filter(
            Expense.user_id == user_id,
            Expense.date >= first_date,
            Expense.date <= current_date,
            CategoryAlias.user_id == user_id,
            BudgetAlias.user_id == user_id
        )
        .group_by(Expense.category, CategoryAlias.id, BudgetAlias.monthly_limit)
        .all()
    )

    return expenses_in_month


def get_expense_summary(db, user_id):
    # Define the current date, first day of this month, and 10 months ago
    current_date = datetime.now().date()
    first_date_this_month = datetime(current_date.year, current_date.month, 1).date()
    first_date_10_months_ago = (first_date_this_month - timedelta(days=10 * 30)).replace(day=1)

    result = (
        db.query(
            func.sum(Expense.amount).filter(Expense.date >= first_date_this_month).label('total_expense_this_month'),
            func.avg(Expense.amount).filter(
                Expense.date >= first_date_10_months_ago,
                Expense.date < first_date_this_month
            ).label('average_expense_last_10_months')
        )
        .filter(Expense.user_id == user_id)
        .one()
    )
    total_expense_this_month = result.total_expense_this_month or 0.0
    average_expense_last_10_months = result.average_expense_last_10_months or 0.0

    return total_expense_this_month, average_expense_last_10_months

