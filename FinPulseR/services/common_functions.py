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

            return{"success": True, "message": "Category created successfully"}

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
