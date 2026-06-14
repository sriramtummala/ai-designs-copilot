from dataclasses import dataclass


@dataclass
class PromptContext:
    page_type: str
    audience: str
    brand: str
    channel: str
    retrieved_context: str
    notes: str = ""

    def _notes_line(self) -> str:
        return self.notes.strip() if self.notes and self.notes.strip() else "None provided."


def build_system_prompt(ctx: PromptContext) -> str:
    return f"""You are an AI DesignOps Copilot. Your task is to generate structured content \
based on user requests and provided context. Adhere strictly to brand guidelines, design \
system rules, and CMS page rules. Ensure the output is compliant, on-brand, and meets the \
specified page type and audience requirements.

Context from Knowledge Base:
{ctx.retrieved_context}

User Request Details:
Page Type: {ctx.page_type}
Audience:  {ctx.audience}
Brand:     {ctx.brand}
Channel:   {ctx.channel}
Notes:     {ctx._notes_line()}

Your output MUST be in Markdown format. Do NOT include any conversational text or \
explanations outside the Markdown. Focus on generating the content directly. If you \
cannot generate content based on the provided context, state that clearly."""


def build_user_prompt(ctx: PromptContext) -> str:
    return f"""Generate the content for a '{ctx.page_type}' for the '{ctx.brand}' brand, \
targeting '{ctx.audience}' on the '{ctx.channel}' channel.
Additional notes: {ctx._notes_line()}

Ensure the content is structured according to the provided context and follows all relevant guidelines."""


def build_messages(ctx: PromptContext) -> list[dict]:
    """Return a messages list ready for the Claude / OpenAI chat API."""
    return [
        {"role": "user", "content": build_user_prompt(ctx)},
    ]
