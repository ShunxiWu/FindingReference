import streamlit as st
import openai
from typing import List, Dict
import json
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

# Load environment variables
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'thesis_topic' not in st.session_state:
    st.session_state.thesis_topic = ""

def split_into_paragraphs(text: str) -> List[str]:
    """将文本分割成段落"""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    return paragraphs

def parse_gpt_response(response_text: str) -> List[Dict]:
    """解析GPT响应"""
    try:
        response_text = response_text.strip()
        try:
            parsed = json.loads(response_text)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                return [parsed]
        except:
            cleaned_text = response_text.replace('\n', ' ').replace('\r', '')
            if not cleaned_text.startswith('['):
                cleaned_text = '[' + cleaned_text
            if not cleaned_text.endswith(']'):
                cleaned_text = cleaned_text + ']'
            try:
                return json.loads(cleaned_text)
            except:
                return []
    except:
        return []

def evaluate_citation_relevance(citations: List[Dict], thesis_topic: str) -> List[Dict]:
    """评估一组引用与论文主题的相关性"""
    if not citations or not thesis_topic:
        return citations
        
    try:
        citations_text = json.dumps(citations, ensure_ascii=False)
        eval_prompt = os.getenv("EVALUATION_PROMPT", "").replace("{thesis_topic}", thesis_topic)\
            .replace("{citations}", citations_text)
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a research advisor evaluating citation relevance."},
                {"role": "user", "content": eval_prompt}
            ]
        )
        
        try:
            evaluations = json.loads(response.choices[0].message['content'].strip())
            for citation, evaluation in zip(citations, evaluations):
                citation['relevance_score'] = evaluation.get('score', 0)
                citation['relevance_analysis'] = evaluation.get('analysis', '')
        except Exception as e:
            st.error("Failed to parse evaluation results: " + str(e))
            
        return citations
    except Exception as e:
        st.error(f"Error in evaluation: {str(e)}")
        return citations

def analyze_paragraph(paragraph: str, references: str, thesis_topic: str) -> List[Dict]:
    """分析单个段落并评估引用相关性"""
    try:
        system_prompt = os.getenv("SYSTEM_PROMPT")
        user_prompt = os.getenv("USER_PROMPT")
        
        if not system_prompt or not user_prompt:
            st.error("SYSTEM_PROMPT or USER_PROMPT is not set in the .env file.")
            return []
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt.replace("{references}", references).replace("{text}", paragraph)}
            ]
        )
        
        results = parse_gpt_response(response.choices[0].message['content'].strip())
        
        if results and thesis_topic:
            try:
                eval_response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a research advisor evaluating citation relevance."},
                        {"role": "user", "content": os.getenv("EVALUATION_PROMPT").replace("{thesis_topic}", thesis_topic).replace("{citations}", json.dumps(results))}
                    ]
                )
                
                evaluations = json.loads(eval_response.choices[0].message['content'].strip())
                for citation, evaluation in zip(results, evaluations):
                    citation['relevance_score'] = evaluation.get('score', 0)
                    citation['relevance_analysis'] = evaluation.get('analysis', '')
            except Exception as e:
                st.error(f"Error in evaluation: {str(e)}")
        
        return results if results else []
    except Exception as e:
        st.error(f"Error in paragraph analysis: {str(e)}")
        return []

def main():
    st.set_page_config(
        page_title="Literature Citation Indexing Tool",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("Literature Citation Indexing Tool")
    
    st.subheader("Thesis Topic")
    thesis_topic = st.text_area(
        "Enter your thesis topic and research objectives",
        value=st.session_state.thesis_topic,
        height=150
    )
    st.session_state.thesis_topic = thesis_topic
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Reference List")
        references = st.text_area("Enter reference list", height=300)
    with col2:
        st.subheader("Text to Analyze")
        text = st.text_area("Enter text", height=300)
    
    if st.button("Analyze Citations"):
        if text and references:
            # 调试输出
            st.write("Debug - Starting analysis")
            st.write(f"Debug - Text length: {len(text)}")
            st.write(f"Debug - References length: {len(references)}")
            
            # 清空之前的分析结果
            st.session_state.analysis_results = {}
            progress_bar = st.progress(0)
            status_container = st.empty()
            results_container = st.container()
            
            paragraphs = split_into_paragraphs(text)
            st.write(f"Debug - Found {len(paragraphs)} paragraphs")
            
            with results_container:
                for i, paragraph in enumerate(paragraphs):
                    status_container.text(f"Analyzing paragraphs: {i+1}/{len(paragraphs)}")
                    progress_bar.progress((i + 1) / len(paragraphs))
                    
                    results = analyze_paragraph(paragraph, references, thesis_topic)
                    # 无论是否有结果，都存入 session_state（可以选存或不存）
                    st.session_state.analysis_results[i] = results

                    with st.expander(f"Paragraph {i+1}", expanded=True):
                        cols = st.columns([5, 5])
                    grouped = {}
                    for item in results:
                        loc = item.get('location', '')
                        grouped.setdefault(loc, []).append(item)
                        
                    # 为每个 location 分配颜色（可以根据需要调整颜色列表）
                    color_mapping = {}
                    colors = ["#FFFF99", "#FFCC99", "#FF9999", "#99FF99", "#99CCFF", "#FF99CC", "#CCFF99"]
                    for idx, loc in enumerate(grouped.keys()):
                        color_mapping[loc] = colors[idx % len(colors)]
                        
                    with st.expander(f"Paragraph {i+1}", expanded=True):
                        cols = st.columns([5, 5])
                        
                        # 左列：引用分析展示，同时对引用位置应用相应颜色
                        with cols[0]:
                            st.markdown("#### Citations and Analysis")
                            if results:
                                for loc, group in grouped.items():
                                    st.markdown(
                                        f"**Cited Text:**  \n"
                                        f"<span style='background-color: {color_mapping[loc]}; padding: 2px;'>{loc}</span>",
                                        unsafe_allow_html=True
                                    )
                                    st.markdown("**Citations and Matched References:**")
                                    for entry in group:
                                        st.markdown(
                                            f"- **Citation:** _{entry.get('citation', 'No citation found')}_  \n"
                                            f"  **Matched Reference:** _{entry.get('matched_reference', 'No matched reference found')}_"
                                        )
                                    st.markdown(f"**Score:** {group[0].get('relevance_score', 'N/A')}/10")
                                    st.markdown(f"**Analysis:** {group[0].get('relevance_analysis', 'No analysis available')}")
                                    st.markdown("---")
                            else:
                                st.markdown("No citations found.")
                        
                        # 右列：原文高亮显示，与左侧颜色对应
                        with cols[1]:
                            st.markdown("#### Original Text")
                            highlighted_paragraph = paragraph
                            if results:
                                for loc in color_mapping.keys():
                                    highlighted_paragraph = highlighted_paragraph.replace(
                                        loc, f"<span style='background-color: {color_mapping[loc]}; padding: 2px;'>{loc}</span>"
                                    )
                            st.markdown(highlighted_paragraph, unsafe_allow_html=True)
                                
            status_container.empty()
            progress_bar.empty()
            st.success("Analysis Complete!")
            
            if st.button("Export to CSV"):
                try:
                    rows = []
                    for para_num, citations in st.session_state.analysis_results.items():
                        for citation in citations:
                            rows.append({
                                'Paragraph': int(para_num) + 1,
                                'Citation': citation.get('citation', ''),  # 修改：使用正确的键"citation"
                                'Reference': citation.get('matched_reference', ''),
                                'Context': citation.get('location', ''),
                                'Relevance_Score': citation.get('relevance_score', ''),
                                'Analysis': citation.get('relevance_analysis', '')
                            })
                    
                    df = pd.DataFrame(rows)
                    filename = f"citations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    df.to_csv(filename, index=False)
                    st.success(f"Exported to {filename}")
                except Exception as e:
                    st.error(f"Export error: {str(e)}")

if __name__ == "__main__":
    main()
