"""Settings API — user rules and preferences."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db.engine import get_db
from src.db.models import UserRule
from src.core.operation_logger import log_operation

router = APIRouter()


DEFAULT_RULES = """# 用户自定义规则

## 关注领域
- 优先关注中国宏观经济和货币政策
- 对新能源、科技互联网行业保持高度敏感

## 回答风格
- 回答要简洁，控制在 3-5 段以内
- 使用专业但易懂的语言
- 遇到数据时标注来源

## 分类偏好
- 涉及"央行""利率"的文章优先归类到"货币政策"
- 涉及"财报""估值"的文章优先归类到"财报解读"
"""


class RulesResponse(BaseModel):
    rules: str


class RulesUpdateRequest(BaseModel):
    rules: str


@router.get("/rules", response_model=RulesResponse)
def get_rules(db: Session = Depends(get_db)):
    rule = db.query(UserRule).first()
    if not rule:
        return {"rules": DEFAULT_RULES}
    return {"rules": rule.rules or DEFAULT_RULES}


@router.put("/rules")
def update_rules(req: RulesUpdateRequest, db: Session = Depends(get_db)):
    rule = db.query(UserRule).first()
    if not rule:
        rule = UserRule(rules=req.rules)
        db.add(rule)
    else:
        rule.rules = req.rules
    db.commit()
    db.refresh(rule)
    log_operation(
        "rules_updated",
        target_type="user_rule",
        target_id=rule.id,
        details={"rules_length": len(rule.rules) if rule.rules else 0},
        db=db,
    )
    return {"rules": rule.rules}
