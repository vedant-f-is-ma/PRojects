import gradio as gr

def mood_translator(text):
    if not text.strip():
        return "🤔 Please say *something*..."
    
    text = text.lower()
    if "happy" in text or "excited" in text:
        return "😄 You're radiating joy!"
    elif "sad" in text or "tired" in text:
        return "😔 Sending you virtual hugs!"
    elif "angry" in text or "mad" in text:
        return "😡 Take a breath, it’ll pass."
    else:
        return "🤖 I'm trying to read your vibe... interesting!"

interface = gr.Interface(
    fn=mood_translator,
    inputs="text",
    outputs="text",
    title="🎭 Mood Translator",
    description="Tell me how you feel, and I’ll translate it into a mood!",
    theme="soft"
)

interface.launch()
