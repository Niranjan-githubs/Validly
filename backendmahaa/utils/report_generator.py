from fpdf import FPDF
import os
import re
import textwrap

def format_paragraph(text, width=100):
    """Wrap text for a paragraph."""
    if text is None:
        text = ""
    return textwrap.fill(str(text), width=width)

def format_list(items, bullet="-", width=100):
    """Format a list of items as a paragraph."""
    return "\n".join([f"{bullet} {textwrap.fill(str(item), width=width)}" for item in items])

def safe_str(val):
    return str(val) if val is not None else ""

def generate_natural_language_report(analysis: dict) -> dict:
    """Return a dict of section_name: paragraph_text for each report section."""
    sections = {}

    # Header (no section header here)
    title = analysis.get('summary_title', "") or ""
    #description = analysis.get('summary_description', "") or ""
    sections["header"] = f"Title: {title}"

    # Market Analysis
    market = analysis.get('market_analysis', {})
    market_paragraph = (
        f"Industry: {market.get('industry', 'N/A')}\n"
        f"Market Trend: {format_paragraph(market.get('market_trend', 'N/A'))}\n"
        f"TAM: {market.get('TAM', '')}\n"
        f"SAM: {market.get('SAM', '')}\n"
        f"SOM: {market.get('SOM', '')}\n"
        f"Pricing Opportunity: {format_paragraph(market.get('pricing_opportunity', ''))}\n"
        f"Customer Segments: {', '.join(market.get('customer_segments', []) or [])}"
    )
    sections["market"] = market_paragraph

    # Competitors
    competitors = analysis.get('competitors', [])
    if competitors:
        comp_lines = []
        for i, comp in enumerate(competitors[:5], 1):
            name = comp.get('name', comp.get('company_name') or "")
            desc = comp.get('description', 'No description available')
            comp_lines.append(f"{i}. {format_paragraph(name)}: {format_paragraph(desc)}")
        comp_paragraph = "\n".join(comp_lines)
    else:
        comp_paragraph = "No competitors found."
    sections["competitors"] = comp_paragraph

    # Recommendations
    recommendations = analysis.get('recommendations', [])
    if recommendations:
        rec_paragraph = format_list(recommendations, bullet="•")
    else:
        rec_paragraph = "No recommendations available."
    sections["recommendations"] = rec_paragraph

    # Risks
    risks = analysis.get('risks', [])
    if risks:
        risk_paragraph = format_list(risks, bullet="•")
    else:
        risk_paragraph = "No risks identified."
    sections["risks"] = risk_paragraph

    # User Pain Points
    pain_points = analysis.get('user_pain_points', [])
    if pain_points:
        pain_lines = []
        for i, pain in enumerate(pain_points[:3], 1):
            title = pain.get('title') or ""
            comment = pain.get('comment') or ""
            pain_lines.append(f"{i}. {format_paragraph(title)}\n   {format_paragraph(comment)}")
        pain_paragraph = "\n".join(pain_lines)
    else:
        pain_paragraph = "No user pain points found."
    sections["pain_points"] = pain_paragraph

    # Investors
    vcs = analysis.get('venture_capitalists', [])
    angels = analysis.get('angel_investors', [])
    if vcs:
        vc_lines = [f"{i+1}. {vc.get('name', 'N/A')} ({vc.get('focus', '')})" for i, vc in enumerate(vcs[:3])]
        vc_paragraph = "\n".join(vc_lines)
    else:
        vc_paragraph = "No venture capitalists listed."
    if angels:
        angel_lines = [f"{i+1}. {a.get('name', 'N/A')} ({a.get('focus', '')})" for i, a in enumerate(angels[:3])]
        angel_paragraph = "\n".join(angel_lines)
    else:
        angel_paragraph = "No angel investors listed."
    sections["investors"] = f"{vc_paragraph}\n\n{angel_paragraph}"

    return sections

def force_break_long_words(text: str, max_length: int = 15) -> str:
    """
    ULTRA bulletproof function to break ANY long word/URL/string.
    Inserts spaces every max_length characters in words longer than max_length.
    """
    def break_word(word):
        if len(word) <= max_length:
            return word
        # Insert space every max_length characters
        broken = []
        for i in range(0, len(word), max_length):
            chunk = word[i:i+max_length]
            broken.append(chunk)
        return ' '.join(broken)
    
    # Split by any whitespace and break each word
    words = re.split(r'\s+', text)
    broken_words = [break_word(word) for word in words if word]
    return ' '.join(broken_words)

def clean_text_for_pdf(text: str) -> str:
    """Clean text to avoid PDF rendering issues"""
    # Remove non-ASCII characters that might cause issues
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

import os

def add_section_header(pdf, text, width=180):
    pdf.set_font("DejaVu", style="B", size=13)
    pdf.multi_cell(width, 10, text, border=0, align='L')
    pdf.ln(2)
    pdf.set_font("DejaVu", size=11)  # Reset to normal for content

def generate_pdf_from_sections(sections: dict, output_path: str = None) -> bytes:
    pdf = FPDF(format='A4', orientation='P')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    font_path_regular = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
    font_path_bold = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans-Bold.ttf")
    if os.path.exists(font_path_regular):
        pdf.add_font("DejaVu", "", font_path_regular, uni=True)
        if os.path.exists(font_path_bold):
            pdf.add_font("DejaVu", "B", font_path_bold, uni=True)
        pdf.set_font("DejaVu", size=11)
    else:
        pdf.set_font("Arial", size=11)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    effective_width = 180

    pretty_headers = {
        "header": "STARTUP ANALYSIS REPORT",
        "market": "MARKET ANALYSIS",
        "competitors": "COMPETITOR LANDSCAPE",
        "recommendations": "RECOMMENDATIONS",
        "risks": "RISKS",
        "pain_points": "USER PAIN POINTS",
        "investors": "INVESTORS"
    }

    for section_name in ["header", "market", "competitors", "recommendations", "risks", "pain_points", "investors"]:
        if section_name in sections:
            if section_name == "header":
                # Print the main report heading
                pdf.set_font("DejaVu", style="B", size=16)
                pdf.cell(0, 12, pretty_headers["header"], ln=True)
                pdf.ln(2)
                # Print the title in bold
                header_lines = sections["header"].split('\n')
                if header_lines:
                    pdf.set_font("DejaVu", style="B", size=13)
                    pdf.cell(0, 10, header_lines[0], ln=True)  # "Title: ..."
                    pdf.set_font("DejaVu", size=11)
                    for line in header_lines[1:]:
                        pdf.multi_cell(effective_width, 8, line, border=0, align='L')
                pdf.ln(6)
            else:
                add_section_header(pdf, pretty_headers[section_name])
                pdf.set_font("DejaVu", size=11)
                pdf.multi_cell(effective_width, 8, sections[section_name], border=0, align='L')
                pdf.ln(6)

    if output_path:
        pdf.output(output_path)
        return None
    else:
        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            return pdf_output.encode('latin1')
        else:
            return bytes(pdf_output)