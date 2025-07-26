from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate


class AiNewsNode:

    def __init__(self,llm):
        """
        Initilize the AINewsNode with API keys for Tavily and GROQ."""

        self.tavily = TavilyClient()
        self.llm =llm
        # This is used to capture various steps in this file so that later can be use for steps shown
        self.state = {}
    
    def fetch_news(self, state:dict) -> dict:
        """
        Fetch AI news based on the specified frequency.

        Args:
            state (dict): The state dicitonary containing 'frequency'.

        Returns:
            dict: Updated state with 'news_data' keuy containing fetched news.
        """
        frequency =  state['messages'][0].content.lower()
        self.state['frequency'] = frequency
        time_range_map = {'daily': 'd', 'weekly': 'w', 'monthly': 'm', 'yearly': 'y'}
        days_map ={'daily':1, 'weekly':7, 'monthly':30, 'yearly':365}
        response = self.tavily.search(
            query="Top Artificial Intelligence (AI) technology news India and globally",
            topic  ='news',
            time_range=time_range_map[frequency],
            include_answer="advanced",
            max_results=15,
            days=days_map[frequency]
            # include_domains =['techcruch.com', "venturebeat.com/ai",.....]   #uncoment and add domains if required
        )


        state['news_data'] = response.get('results', [])
        self.state['news_data'] = state['news_data']
        return state
    

    def summarize_news(self, state:dict) -> dict:
        """
        Summarize the fetched news using LLM.

        Args:
            state (dict): The state dictionary containing 'news_data'.

        Returns:
            dict: Updated state with 'summary' key containing summarized news.
        """
        news_items = self.state['news_data']

        prompt_template =  ChatPromptTemplate.from_messages([
            ("system","""Summarize AI news articles into markdown  format fro each item include:
            
             - Date in **YYYY-MM-DD** format in IST timezone
             -Concise sentense summary from latest news
             -sort news by data wise (latest first)
             -source URl as link
             Use format:
             ### [Date]
             -[Summary](URL)"""),
             ("user","Articles:\n{articles}")
             ])
        
        articles_str = "\n\n".join([
            f"Content: {item.get('content', '')}\nURL: {item.get('url', '')}\nDate: {item.get('published_date', '')}"
            for item in news_items

        ])
        response = self.llm.invoke(
            prompt_template.format(articles=articles_str)
        )
        state['summary'] = response.content
        self.state['summary'] = state['summary']
        return self.state
    
    def save_result(self,state):
        frequency = self.state['frequency']
        summary = self.state['summary']
        filename = f"./AINews/{frequency}_summary.md"
        with open(filename, 'w') as f:
            f.write(f"#{frequency.capitalize()} AI News Summary\n\n")
            f.write(summary)
        self.state['file_path'] = filename
        return self.state
