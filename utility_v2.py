from langchain_community.document_transformers import Html2TextTransformer
from langchain_community.document_loaders import AsyncChromiumLoader
# from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_community.document_loaders import AsyncHtmlLoader
from googlesearch import search  
import io
import requests
from PyPDF2 import PdfReader
from llm import one_limit_call,one_limit_call_1
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup



class WebSearch():
    def __init__(self):
        pass
    
    def do_search(self,query,top_n, tbs='0'):
        search_url_obj=search(query, tld = "co.in", num = top_n , stop = top_n, pause = 2) 
#         search_urls=[link for link in search_url_obj]
        search_urls=[link for link in search_url_obj if "ambitionbox" not in link]
        print("search_urls ::",search_urls)
        return search_urls
    
    def fecth_text(self,query,top_n=5, tbs='0'):
        search_urls=self.do_search(query,top_n=top_n)
        text_docs=[]
        for url in search_urls:
            print("Url is processing:",url)
            url_low = str(url).lower()
            if url_low.endswith(".pdf") :
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (X11; Windows; Windows x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36'}
                    print("PDF FILE PROCESS")
                    # Fetch the PDF and load it into memory
                    response = requests.get(url=url, headers=headers, timeout=30)
                    # Load the PDF into a BytesIO object
                    on_fly_mem_obj = io.BytesIO(response.content)
                    pdf_reader = PdfReader(on_fly_mem_obj)
                    # Extract text from each page
                    pdf_text = ""
                    for idx, page in enumerate(pdf_reader.pages):
                        pdf_text += page.extract_text() + "\n"
                        if idx>2:
                            break
                    # pdf_text_limit=' '.join(pdf_text.split(" ")[:20000])
                    # Store the extracted text
                    # print(pdf_text)
                    text_docs.append([{"source": url, "content": pdf_text}])
                except:
                    print("Url Not process ::",url)
            elif "businesswire" in url_low or "business-standard" in url_low:
                pass
            else:
                try:
                    loader = AsyncHtmlLoader([url],ignore_load_errors=True)
                    docs = loader.load()
                    html2text = Html2TextTransformer()
                    docs_transformed = html2text.transform_documents(docs)
                    # docs_transformed=str(docs_transformed)
                    # docs_transformed=' '.join(docs_transformed.split(" ")[:20000])
                    # print(docs_transformed)
                    text_docs.append(docs_transformed)
                except:
                    print("Url Not process ::",url)
        return text_docs


def data_financial_preprocessing(target_company,text_docs_list):
    final_summerize_response=[]
    for i,doc in enumerate(text_docs_list):
        print("-------------------------------------------------------------------------")
        if 'content' in text_docs_list[i][0]:
            context=text_docs_list[i][0]['content']
            prompt_=get_financial_prompt(target_company,context)
            extracted_data,usage=one_limit_call(prompt_)
            # print(extracted_data)
            final_summerize_response.append(extracted_data)
        else:
            context=text_docs_list[i][0].page_content
            prompt_=get_financial_prompt(target_company,context)
            extracted_data,usage=one_limit_call(prompt_)
            # print(extracted_data)
            final_summerize_response.append(extracted_data)
    final_data='\n\n'.join(final_summerize_response)
    return final_data

def data_org_preprocessing(target_company,text_docs_list):
    final_summerize_response=[]
    for i,doc in enumerate(text_docs_list):
        print("-------------------------------------------------------------------------")
        if 'content' in text_docs_list[i][0]:
            context=text_docs_list[i][0]
            prompt_=get_org_prompt(target_company,context)
            extracted_data,usage=one_limit_call_1(prompt_)
            print(extracted_data)
            final_summerize_response.append(extracted_data)
        else:
            context=text_docs_list[i][0]
            prompt_=get_org_prompt(target_company,context)
            extracted_data,usage=one_limit_call_1(prompt_)
            print(extracted_data)
            final_summerize_response.append(extracted_data)
    final_data='\n\n'.join(final_summerize_response).replace("{","{{").replace("}","}}")
    return final_data


def get_financial_prompt(target_company,context):
    prompt_=f"""You are a structured data extraction specialist trained to extract financial and lead qualification data for sales and investment analysis. Your goal is to analyze web search results and extract only the most relevant details about {target_company}, ensuring accuracy and completeness while presenting the information in a structured JSON format. Do not include any data related to other companies.

    Below is the key guidelines for extracting the data:
    1. Extract structured information from web search results related to {target_company} company only. Identify key financial, operational and reputational details.
    2. Extract yearly revenue, profit, funding details and other financial information from the provided context.
    3. Always extract all the details yearly. If multiple financial reports exist, use the latest available data.
    4. Focus on financial deatils of {target_company}.
    5. Identify positive and negative mentions from news articles, press releases and financial data.
    6. Extract market trends, competition and growth prospects.
    7. No any relevant information found return 'NA'.
    8. Ensure that all extracted information is relevant and accurate, strictly based on the provided context for {target_company}. Do not include any incorrect details or information about any other company.

    Here is the data of payee customers:{context}
    response: """
    return prompt_


def get_org_prompt(target_company,context):
    prompt_=f"""You are an expert in corporate structures, specializing in identifying decision-making hierarchies within organizations.  Your task is to find relevant executives and stakeholders at {target_company}, including their names, roles, professional contact details and LinkedIn profiles. Your work provides Convera with direct access to financial decision-makers, enabling effective outreach and engagement with potential payee customers.

    Below is the key guidelines for extracting the data:
    1. Extract structured information from web search results related to {target_company} company only.
    2. Look for founding year, milestones.
    3. Extract from the official website, LinkedIn.
    4. Use LinkedIn, Bloomberg and official websites to verify CEO, CFO and executive team details.
    5. Extract the LinkedIn URL from the `source` field in the document. If the `source` contains a LinkedIn URL (e.g., it includes "linkedin.com"), return the full URL; otherwise, return `None`.
    6. Include tenure, past experience, and notable achievements of leaders.
    7. No any relevant information found return 'NA'.
    8. Ensure that all extracted information is relevant and accurate, strictly based on the provided context for {target_company}. Do not include any incorrect details or information about any other company.

    company_context:{context} """+\
    """Below is a sample example of the final output:
    ```{{"company_name": "<company_name>",
  "company_website": "<company_website>",
  "company_linkedin_profile": "<company_linkedin_profile>",
  "founding_year": "<founding_year>",
  "executives": [{{
      "name": "<executive_name>",
      "role": "<executive_role>",
      "tenure": "<executive_tenure>",
       "linkedin_profile": "<linkedin_profile_url>",
       "contact_email": "<office_email>"}}]}}```
    final output shoud be in JSON format only:
    response: """
    return prompt_


def get_summary_prompt(topic,context):
    # Topic: {topic}  
    prompt_ = f"""Please generate a concise summary (50-100 words) realted to the company {topic} from the news data.
If there is no relevant information in the news data, return "NA."

news data: {context}  
Summary:
"""
    return prompt_


def create_gauge_chart(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Customer Lead Potential", 'font': {'size': 14}},
        gauge={'axis': {'range': [0, 10]},
               'bar': {'color': "blue"},
               'steps': [
                   {'range': [0, 4], 'color': "red"},
                   {'range': [4, 7], 'color': "yellow"},
                   {'range': [7, 10], 'color': "green"}
               ]
              }
    ))

    fig.update_layout(
        margin={'t': 40, 'b': 10, 'l': 0, 'r': 0},
        height=150 ,
        width=300
    )
    
    return fig



def get_page_title_and_description(url):
    try:
        # Fetch the content of the URL
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title
        title = soup.title.string if soup.title else "No title found"

        # Extract meta description
        description = "No description found"
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            description = meta_desc["content"]
        else:
            # Some websites use Open Graph tags for descriptions
            og_desc = soup.find("meta", attrs={"property": "og:description"})
            if og_desc and og_desc.get("content"):
                description = og_desc["content"]

        return title.strip(), description.strip()

    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {e}", None
