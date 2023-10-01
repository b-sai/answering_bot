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
        content = response.get_contents().contents[0]
        html_string = content.extract
        search_text = BeautifulSoup(html_string, "html.parser").get_text()
        score = response.results[0].score
        return search_text, content.url, content.title, score
    
    def get_answer(self, query, search_text):

        # output is a generator
        output = replicate.run(os.environ['MODEL'],
            input = {"prompt": f"answer in as few words as possible.\nGiven the following text:\n{search_text}\nAnswer the following question:\n{query}",
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
            try:
                search_text, url, title, score = self.get_search_results(query)
            except Exception as E:
                await message.channel.send(f"Could not fetch results -- API limit exceeded")
                return
            
            if score < 0.25:
                return
            
            try:
                answer = self.get_answer(query, search_text)
            except Exception as E:
                answer = None

            if answer is not None:
                await message.channel.send(f"{answer}\n\nFor further reading, see [{title}]({url})")
            else:
                await message.channel.send(f"This result might be relevant [{title}]({url})")



async def setup(bot):
    await bot.add_cog(Answering(bot))