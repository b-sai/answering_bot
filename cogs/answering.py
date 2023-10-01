import discord
from discord.ext import commands
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
from metaphor_python import Metaphor
import os
from bs4 import BeautifulSoup
import replicate

class Answering(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tokenizer = AutoTokenizer.from_pretrained("mrsinghania/asr-question-detection")

        self.model = AutoModelForSequenceClassification.from_pretrained("mrsinghania/asr-question-detection")
        

        self.metaphor = Metaphor(os.environ["METAPHOR_KEY"])
        
    def get_search_results(self, query):
        response = self.metaphor.search(
        query,
        num_results=1,
        use_autoprompt=True)
        html_string = response.get_contents().contents[0].extract
        search_text = BeautifulSoup(html_string, "html.parser").get_text()
        return search_text

    def get_answer(self, query, search_text):
        
        # output is a generator
        output = replicate.run(os.environ['MODEL'],
            input = {"prompt": f"""answer in as few words as possible.
                Given the following text:
                {search_text}
                
                Answer the following question:
                
                {query}
                """,
                "max_length":30})
        return "".join(list(output))

    def is_question(self, text):
        inputs = self.tokenizer(text, return_tensors="pt")
        outputs = self.model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1)
        question_probability = probabilities[0][1].item()
        return question_probability > 0.5

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        if self.is_question(text=message.content):
            query = message.content
            search_text = self.get_search_results(query)
            answer = self.get_answer(query, search_text)
            await message.channel.send(answer)
            

async def setup(bot):
    await bot.add_cog(Answering(bot))