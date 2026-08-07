from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

def create_presentation():
    prs = Presentation()
    
    # Slide Layouts
    title_slide_layout = prs.slide_layouts[0]
    bullet_slide_layout = prs.slide_layouts[1]
    
    # ---------------------------------------------------
    # Title Slide
    # ---------------------------------------------------
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = "Code Generation Capstone"
    subtitle.text = "Multi-task Code Synthesis & Agentic Pipeline\nExecutive Presentation"
    
    # ---------------------------------------------------
    # Slide 1: Problem Statement & High-Level Solution
    # ---------------------------------------------------
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    
    title_shape.text = "Problem Statement & High-Level Solution"
    
    tf = body_shape.text_frame
    tf.text = "Problem: Developers spend significant time translating code across languages, writing boilerplate, and adding documentation manually."
    
    p = tf.add_paragraph()
    p.text = "Solution: A multi-task code synthesis system built on a fine-tuned Qwen2.5-Coder-0.5B-Instruct model."
    
    p = tf.add_paragraph()
    p.text = "Approach: A LangGraph-based agentic pipeline that routes, generates, executes, judges, and fixes code autonomously."
    
    p = tf.add_paragraph()
    p.text = "Key Capabilities:"
    p.level = 0
    
    p = tf.add_paragraph()
    p.text = "Natural Language to Python (NL2Py)"
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Java to Python Translation (Java2Py)"
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Code to Documentation & Commenting"
    p.level = 1

    # ---------------------------------------------------
    # Slide 2: What We Built
    # ---------------------------------------------------
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    
    title_shape.text = "What We Built"
    
    tf = body_shape.text_frame
    tf.text = "A unified multi-task model checkpoint handling 4 distinct code generation tasks."
    
    p = tf.add_paragraph()
    p.text = "An Agentic Pipeline: NL / Java / pseudocode → Java → Python → Sandbox Execute → LLM Judge → Fix Loop."
    
    p = tf.add_paragraph()
    p.text = "Interactive Interfaces: FastAPI backend and a Gradio web application deployed on Hugging Face Spaces."
    
    p = tf.add_paragraph()
    p.text = "[ Play Recorded Video Demo Here ]"
    p.font.bold = True
    from pptx.dml.color import RGBColor
    p.font.color.rgb = RGBColor(0, 102, 204)

    # ---------------------------------------------------
    # Slide 3: Architecture & Sequence Diagram
    # ---------------------------------------------------
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    
    title_shape.text = "Architecture & Sequence"
    
    tf = body_shape.text_frame
    tf.text = "LangGraph Agent Flow: Route → Retrieve (RAG) → Generate → Execute → Judge → Fix."
    
    p = tf.add_paragraph()
    p.text = "Execution Sandbox: Dockerized environment for safe code execution and testing."
    
    p = tf.add_paragraph()
    p.text = "Two-Stage LoRA Fine-Tuning:"
    
    p = tf.add_paragraph()
    p.text = "Stage 1: Specialize on Java to Python (AVATAR-TC)."
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Stage 2: Multi-task learning (NL2Py, Code2Doc, Comments)."
    p.level = 1
    
    # Add the generated architecture diagram image
    img_path = "architecture_diagram.png"
    slide.shapes.add_picture(img_path, Inches(1.5), Inches(3.5), width=Inches(7))

    # ---------------------------------------------------
    # Slide 4: Technical Specifications & Model Capabilities
    # ---------------------------------------------------
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    
    title_shape.text = "Technical Specifications & Capabilities"
    
    tf = body_shape.text_frame
    tf.text = "Base Model: Qwen2.5-Coder-0.5B-Instruct (Parameter-efficient LoRA fine-tuning)."
    
    p = tf.add_paragraph()
    p.text = "Datasets:"
    
    p = tf.add_paragraph()
    p.text = "AVATAR-TC & CoDocBench (Java to Python)"
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "MBPP (Natural Language to Python)"
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "DocuMint (Code to Documentation)"
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Evaluation Metrics: BLEU, BERTScore, CodeBLEU, CodeBERTScore, and Sandbox Execution Accuracy."
    
    p = tf.add_paragraph()
    p.text = "Inference: RAG pipeline integration and MPS/CUDA hardware acceleration."

    # ---------------------------------------------------
    # Slide 5: Learnings & Limitations
    # ---------------------------------------------------
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    
    title_shape.text = "Learnings & Limitations"
    
    tf = body_shape.text_frame
    tf.text = "Model Size: As a 0.5B parameter model, quality varies by task complexity and input length."
    
    p = tf.add_paragraph()
    p.text = "Training Bias: Primarily trained on Python; Java translation quality relies heavily on training dataset coverage."
    
    p = tf.add_paragraph()
    p.text = "Agentic Overhead: The execution and fix loop significantly improves accuracy but increases latency."
    
    p = tf.add_paragraph()
    p.text = "Future Work: Scaling to larger models (e.g., 7B) and expanding the language support matrix."

    # ---------------------------------------------------
    # Slide 6: Q & A
    # ---------------------------------------------------
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    
    title_shape.text = "Q & A"
    
    tf = body_shape.text_frame
    tf.text = "Thank You!"
    
    p = tf.add_paragraph()
    p.text = "Questions?"
    
    # Save presentation
    prs.save("Executive_Presentation.pptx")
    print("Presentation saved as Executive_Presentation.pptx")

if __name__ == "__main__":
    create_presentation()
