from app.services.llm_service import llm
from app.schemas.email_schema import UnifiedEmailSchema
from app.schemas.email_schema import ReplySchema


smart_email_llm = llm.with_structured_output(
    UnifiedEmailSchema
)

reply_llm = llm.with_structured_output(
    ReplySchema
)