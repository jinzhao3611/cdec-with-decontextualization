from langchain_core.prompts import PromptTemplate
import inspect

SYSTEM_PROMPT = ""

DECON_PROMPT = PromptTemplate.from_template(
    inspect.cleandoc(
        """
    {article}

    For each sentence in the above article, can you rewrite each sentence by adding more context from the article, such that the sentence stands alone and provides full information about the containing event. 
    The tagged event should be kept unchanged and tagged in the rewrite.
    """
    )
)

DECON_ORI_PROMPT = PromptTemplate.from_template(
    inspect.cleandoc(
        """
    I will provide you with a news article, each sentence in the article is indicated by a numerical identifier [].
    Each event trigger is tagged as trigger_EVENT in all the sentences.

    {article_list}

    For each sentence in the above article, can you rewrite each sentence by adding more context from the article, such that the sentence stands alone and provides full information about the containing event. 
    The tagged event should be kept unchanged and tagged in the rewrite. 
    The output format should be a list of rewritten sentence, each indicated by a numerical identifier [], e.g.,

     [1] rewritten sentence 1
     [2] rewritten sentence 1
     [3] rewritten sentence 1

    The number of rewritten sentences should be the same as the number of sentences in the article. Do not combine or merge sentences in the output.
    """
    )
)

DECON_RICH2_PROMPT = PromptTemplate.from_template(
    inspect.cleandoc(
        """
    You are an intelligent text rewriter that can add contexts to events from each sentence based on the full article.

    I will provide you with a news article, each sentence in the article is indicated by a numerical identifier [].
    Each event trigger is tagged as trigger_EVENT in all the sentences.

    {article_list}

    Rewrite each sentence by adding more context from the article to each of the tagged events. 
    Each rewritten sentence should stand alone and provide full information about the containing events without the need to read the whole article. 
    The tagged events should be kept unchanged in the rewrite.
    The output format should be a list of rewritten sentence, each indicated by a numerical identifier [], e.g.,

     [1] rewritten sentence 1
     [2] rewritten sentence 1
     [3] rewritten sentence 1

    The number of rewritten sentences should be the same as the number of sentences in the article. Do not combine or merge sentences in the output.
    """
    )
)

DECON_RICH2_NUM_PROMPT = PromptTemplate.from_template(
    inspect.cleandoc(
        """
    You are an intelligent text rewriter that can add contexts to events from each sentence based on the full article.

    I will provide you with a news article, each sentence in the article is indicated by a numerical identifier [].
    Each event trigger is tagged as e.g., trigger1_EVENT-1, trigger2_EVENT-2 in all the sentences.

    {article_list}

    Rewrite each sentence by adding more context from the article to each of the tagged events. 
    Each rewritten sentence should stand alone and provide full information about the containing events without the need to read the whole article. 
    The tagged events should be kept unchanged in the rewrite.
    The output format should be a list of rewritten sentence, each indicated by a numerical identifier [], e.g.,

     [1] rewritten sentence 1
     [2] rewritten sentence 1
     [3] rewritten sentence 1

    The number of rewritten sentences should be the same as the number of sentences in the article. Do not combine or merge sentences in the output.
    """
    )
)

DECON_RICH_PROMPT = PromptTemplate.from_template(
    inspect.cleandoc(
        """
    You are an intelligent text rewriter that can add contexts to events from each sentence based on the full article.

    I will provide you with a news article, each sentence in the article is indicated by a numerical identifier [].
    Each event trigger is tagged as trigger_EVENT in all the sentences.

    {article_list}

    Rewrite each sentence by adding contexts from the article to the tagged events. 
    Each rewritten sentence should provide full contexts about its tagged events without the need to read the whole article. 
    The tagged events should be kept unchanged in the rewrite.
    The output format should be a list of rewritten sentence, each indicated by a numerical identifier [], e.g.,

     [1] rewritten sentence 1
     [2] rewritten sentence 1
     [3] rewritten sentence 1

    The number of rewritten sentences should be the same as the number of sentences in the article. Do not combine or merge sentences in the output.
    """
    )
)

DECON_RICH_ECB_PROMPT = PromptTemplate.from_template(
    inspect.cleandoc(
        """
    You are an intelligent text rewriter that can add contexts to events from each sentence based on the full article.

    I will provide you with a news article, each sentence in the article is indicated by a numerical identifier [].
    Each event trigger is tagged as trigger_EVENT in all the sentences.

    {article_list}

    Rewrite each sentence by adding contexts from the article to the tagged events. 
    Each rewritten sentence should provide full contexts about its tagged events with a focus on the 
     
    The tagged events should be kept unchanged in the rewrite.
    The output format should be a list of rewritten sentence, each indicated by a numerical identifier [], e.g.,

     [1] rewritten sentence 1
     [2] rewritten sentence 1
     [3] rewritten sentence 1

    The number of rewritten sentences should be the same as the number of sentences in the article. Do not combine or merge sentences in the output.
    """
    )
)