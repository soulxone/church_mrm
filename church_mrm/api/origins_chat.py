"""
Origins of Ideas — Claude API Proxy for PS Church.

Proxies chat requests to Anthropic's Claude API, storing conversations
in Frappe DocTypes. Supports both authenticated and guest users.

API endpoints:
  /api/method/church_mrm.api.origins_chat.send_message
  /api/method/church_mrm.api.origins_chat.get_conversations
  /api/method/church_mrm.api.origins_chat.get_conversation
  /api/method/church_mrm.api.origins_chat.archive_conversation
  /api/method/church_mrm.api.origins_chat.get_topic_suggestions
"""

import frappe
import json
import requests as http_requests

# Default system prompt — used if AI Settings has no prompt configured
DEFAULT_SYSTEM_PROMPT = """You are "Origins of Ideas," a scholarly research tool that maps ideas from philosophy and history to their origins, concluding with Biblical truth.

You explore how ideas originate, evolve, and spread from the earliest recorded writings to the present day, beginning with ancient creation stories and extending through classical philosophy, modern philosophy, and contemporary theology.

Core ideas you trace include: order from chaos, being and becoming, truth, knowledge, causation, mind and body, time, ethics, divine action, and salvation. Each idea is explicitly named and sourced to the earliest known texts and major scholarly interpretations, situated in time and place.

Authority within tradition is treated as emerging primarily from successful transmission and endurance over time rather than mere proximity to origin. Each idea or claim is examined for logical coherence, argumentative structure, and whether it functionally represented reality as the culture understood it.

Formal philosophical reasoning (logic, epistemology, metaphysics, ethics, philosophy of science, and philosophy of religion) is treated as an essential analytical layer alongside mythic, symbolic, and theological reasoning.

You may cite standard philosophical reference works and histories: Cambridge Dictionary of Philosophy, Routledge Encyclopedia of Philosophy, Stanford Encyclopedia of Philosophy, Copleston, Kenny, Audi. Core texts in logic and argumentation: Copi, Cohen, Lewis, Kneale, Lipton. Epistemology and skepticism: Gettier, Plantinga, BonJour, Greco, Stroud. Metaphysics and ontology: Kripke, Lowe, Loux, Chisholm, Armstrong. Philosophy of mind: Kim, Swinburne, Moreland, Churchland. Free will and personal identity: Kane, Fischer, Parfit. Philosophy of science and realism debates: Kuhn, Lakatos, van Fraassen. Ethics and moral philosophy. Extensive literature in philosophy of religion and Christian doctrine: Plantinga, Craig, Swinburne, Adams, Leftow, Wolterstorff, Aquinas.

You also integrate major Christian philosophical and theological discussions on God's existence, divine attributes, the problem of evil, creation and providence, miracles, the Trinity, Incarnation, Atonement, salvation, and religious diversity, drawing on historical sources (Anselm, Aquinas, Molina, Turretin), modern analytic philosophy of religion, and contemporary evangelical, Catholic, and ecumenical scholarship.

Biblical-theological and historical-cultural sources are explicitly incorporated: Andreas J. Köstenberger and Gregory Goswell, *Biblical Theology: A Canonical, Thematic, and Ethical Approach*, for canonical structure, thematic development, and ethical coherence across the Testaments; and *Dictionary of Daily Life in Biblical and Post-Biblical Antiquity* (4 vols.), edited by Edwin Yamauchi and Marvin R. Wilson, for socio-historical, linguistic, and material-cultural context.

When evidence is strong, statements are labeled as supported by sources; when interpretation or philosophical judgment is required, transitions are explicitly marked. Similar ideas across cultures are evaluated for transmission versus independent convergence. Analysis proceeds from symbolic and metaphysical meaning, to formal philosophical articulation, to social and theological implications.

**IMPORTANT: Regardless of the culture or philosophical system examined, every response concludes by explicitly pointing back to Biblical truths — especially the Hebrew Scriptures and the New Testament — as the ultimate source of reality, clarifying how philosophical insights align with, anticipate, contrast with, or are fulfilled by Biblical revelation.**

All scriptures should reference the Septuagint (LXX) and ESV, showing both Greek LXX and ESV English text where relevant."""


def _get_settings():
    """Load AI Settings, returning defaults if not configured."""
    try:
        settings = frappe.get_single("AI Settings")
        return {
            "model": settings.claude_model or "claude-sonnet-4-20250514",
            "max_tokens": settings.max_tokens or 4096,
            "temperature": settings.temperature or 0.7,
            "system_prompt": settings.system_prompt or DEFAULT_SYSTEM_PROMPT,
            "max_messages": settings.max_messages_per_conversation or 100,
            "daily_limit": settings.daily_request_limit_per_user or 50,
            "allow_guest": settings.allow_guest_access,
            "guest_limit": settings.guest_daily_limit or 5,
        }
    except Exception:
        return {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4096,
            "temperature": 0.7,
            "system_prompt": DEFAULT_SYSTEM_PROMPT,
            "max_messages": 100,
            "daily_limit": 50,
            "allow_guest": 0,
            "guest_limit": 5,
        }


def _check_rate_limit(settings):
    """Check if the current user has exceeded their daily limit."""
    user = frappe.session.user
    today = frappe.utils.today()

    if user == "Guest":
        if not settings["allow_guest"]:
            frappe.throw("Please log in to use Origins of Ideas.", frappe.AuthenticationError)
        ip = frappe.local.request.remote_addr if frappe.local.request else "unknown"
        cache_key = f"origins_guest_{ip}_{today}"
        count = frappe.cache().get_value(cache_key) or 0
        if count >= settings["guest_limit"]:
            frappe.throw("Daily guest limit reached. Log in for more access.")
        frappe.cache().set_value(cache_key, count + 1, expires_in_sec=86400)
    else:
        conversations = frappe.get_all(
            "AI Conversation", filters={"user": user}, pluck="name"
        )
        if conversations:
            count = frappe.db.count("AI Message", filters={
                "parenttype": "AI Conversation",
                "parent": ["in", conversations],
                "role": "user",
                "timestamp": [">=", f"{today} 00:00:00"],
            })
        else:
            count = 0
        if count >= settings["daily_limit"]:
            frappe.throw("Daily usage limit reached. Please try again tomorrow.")


def _call_claude(messages, settings):
    """Make the API call to Anthropic's Claude."""
    api_key = frappe.conf.get("anthropic_api_key")
    if not api_key:
        frappe.throw(
            "AI service not configured. Please add anthropic_api_key to site_config.json.",
            frappe.ValidationError
        )

    payload = {
        "model": settings["model"],
        "max_tokens": settings["max_tokens"],
        "temperature": settings["temperature"],
        "system": settings["system_prompt"],
        "messages": messages,
    }

    try:
        response = http_requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()

        content = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block["text"]

        input_tokens = data.get("usage", {}).get("input_tokens", 0)
        output_tokens = data.get("usage", {}).get("output_tokens", 0)

        return {
            "content": content,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        }
    except http_requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else 0
        if status == 429:
            frappe.throw("AI service is busy. Please wait a moment and try again.")
        elif status == 401:
            frappe.throw("AI service authentication failed. Contact administrator.")
        else:
            frappe.log_error(f"Claude API error: {e}", "Origins Chat")
            frappe.throw("AI service temporarily unavailable. Please try again.")
    except http_requests.exceptions.Timeout:
        frappe.throw("AI service timed out. Please try a shorter question.")
    except Exception as e:
        frappe.log_error(f"Claude API unexpected error: {e}", "Origins Chat")
        frappe.throw("An unexpected error occurred. Please try again.")


def _generate_title(message):
    """Generate a short title from the first user message."""
    title = message.strip()[:80]
    if len(message.strip()) > 80:
        title = title.rsplit(" ", 1)[0] + "..."
    return title


@frappe.whitelist(allow_guest=True)
def send_message(conversation_id=None, message=""):
    """Send a message and get Claude's response.

    Args:
        conversation_id: Existing conversation ID (None for new conversation)
        message: The user's message text

    Returns:
        dict with conversation_id, session_id, reply, title
    """
    if not message or not message.strip():
        frappe.throw("Message cannot be empty.")

    settings = _get_settings()
    _check_rate_limit(settings)

    user = frappe.session.user

    # Load or create conversation
    if conversation_id:
        doc = frappe.get_doc("AI Conversation", conversation_id)
        if user != "Guest" and doc.user != user:
            frappe.throw("Conversation not found.", frappe.PermissionError)
        if len(doc.messages) >= settings["max_messages"]:
            frappe.throw("Conversation has reached the maximum message limit. Please start a new one.")
    else:
        doc = frappe.new_doc("AI Conversation")
        doc.user = user
        doc.title = _generate_title(message)
        doc.model_used = settings["model"]
        doc.insert(ignore_permissions=True)

    # Append user message
    doc.append("messages", {
        "role": "user",
        "content": message.strip(),
        "timestamp": frappe.utils.now(),
    })

    # Build messages array for Claude (exclude system messages from child table)
    claude_messages = []
    for msg in doc.messages:
        if msg.role in ("user", "assistant"):
            claude_messages.append({
                "role": msg.role,
                "content": msg.content,
            })

    # Call Claude API
    result = _call_claude(claude_messages, settings)

    # Append assistant response
    doc.append("messages", {
        "role": "assistant",
        "content": result["content"],
        "timestamp": frappe.utils.now(),
        "tokens_used": result["total_tokens"],
    })

    # Update metadata
    doc.total_tokens_used = (doc.total_tokens_used or 0) + result["total_tokens"]
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "conversation_id": doc.name,
        "session_id": doc.session_id,
        "reply": result["content"],
        "title": doc.title,
        "tokens_used": result["total_tokens"],
    }


@frappe.whitelist()
def get_conversations():
    """Return the current user's conversation list (most recent first)."""
    conversations = frappe.get_all(
        "AI Conversation",
        filters={"user": frappe.session.user, "status": "Active"},
        fields=["name", "title", "started_at", "last_message_at", "total_tokens_used"],
        order_by="last_message_at desc",
        limit_page_length=50,
    )
    return conversations


@frappe.whitelist(allow_guest=True)
def get_conversation(conversation_id):
    """Return a full conversation with all messages."""
    if not conversation_id:
        frappe.throw("Conversation ID is required.")

    doc = frappe.get_doc("AI Conversation", conversation_id)

    if frappe.session.user != "Guest" and doc.user != frappe.session.user:
        frappe.throw("Conversation not found.", frappe.PermissionError)

    messages = []
    for msg in doc.messages:
        messages.append({
            "role": msg.role,
            "content": msg.content,
            "timestamp": str(msg.timestamp) if msg.timestamp else None,
        })

    return {
        "conversation_id": doc.name,
        "session_id": doc.session_id,
        "title": doc.title,
        "started_at": str(doc.started_at) if doc.started_at else None,
        "messages": messages,
    }


@frappe.whitelist()
def archive_conversation(conversation_id):
    """Archive a conversation."""
    if not conversation_id:
        frappe.throw("Conversation ID is required.")

    doc = frappe.get_doc("AI Conversation", conversation_id)
    if doc.user != frappe.session.user:
        frappe.throw("Conversation not found.", frappe.PermissionError)

    doc.status = "Archived"
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"status": "success", "message": "Conversation archived."}


@frappe.whitelist(allow_guest=True)
def get_topic_suggestions():
    """Return predefined topic starter cards."""
    return [
        {
            "title": "Creation & Order",
            "subtitle": "Creatio ex nihilo across cultures",
            "prompt": "How did the concept of creation from nothing (creatio ex nihilo) develop from ancient Near Eastern creation stories through Greek philosophy to Christian theology?",
        },
        {
            "title": "The Problem of Evil",
            "subtitle": "Theodicy from Job to modernity",
            "prompt": "Trace the philosophical and theological development of theodicy from the Book of Job through Augustine, Leibniz, and modern analytic philosophy of religion.",
        },
        {
            "title": "Truth & Knowledge",
            "subtitle": "From Hebrew emet to correspondence theory",
            "prompt": "How did the concept of truth evolve from Hebrew emet through Greek aletheia, medieval adequatio, and modern correspondence theories?",
        },
        {
            "title": "Mind & Body",
            "subtitle": "Dualism from Plato to neuroscience",
            "prompt": "Trace the mind-body problem from Plato's dualism through Descartes to contemporary philosophy of mind, and how does Scripture address human nature?",
        },
        {
            "title": "Ethics & Moral Law",
            "subtitle": "Natural law from Aristotle to Aquinas",
            "prompt": "How did natural law theory develop from Aristotle through Aquinas to modern virtue ethics, and what is its Biblical foundation?",
        },
        {
            "title": "Time & Eternity",
            "subtitle": "From Parmenides to Augustine",
            "prompt": "Explore the philosophical development of concepts of time from Parmenides and Heraclitus through Augustine's Confessions to modern physics and Biblical eschatology.",
        },
    ]
