from discord.ext import commands
from discord import Message, User, DMChannel
from dataclasses import dataclass
from enum import Enum
import json
import logging
import os
import random


logger = logging.getLogger(__name__)


class State(Enum):
    ANSWERING = 0
    WAITING = 1


@dataclass
class Participant:
    '''Class for keeping track of a user taking a quiz'''
    user: User
    current_question: int
    num_questions: int
    questions: list
    score_sheet: list
    state: State


class QuizBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.participants = dict()
        self._load_quiz()

    def _load_quiz(self, path=None):
        if path is None:
            path = os.path.join(os.getcwd(), 'data', 'quiz.json')

        with open(path) as f:
            self.quiz = json.load(f)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.id != self.bot.user.id:
            if isinstance(message.channel, DMChannel):
                logger.info('Received DM')
                await self._init_talk(message)

    async def _init_talk(self, message: Message):
        if message.author not in self.participants:
            if message.content == 'start quiz':
                await self._start_quiz(message)
                await self._send_question(message)
        else:
            participant = self.participants[message.author]
            if participant.state == State.ANSWERING:
                await self._process_answer(message)
                self.next_question(message.author)

                if participant.current_question == participant.num_questions:
                    await self._end_quiz(message)
                else:
                    await message.channel.send('Next question')
                    await self._send_question(message)

    async def _start_quiz(self, message: Message):
        logger.info(f'Starting quiz with {message.author.name}')
        questions = setup_quiz(self.quiz)
        self.add_participant(message.author, questions)
        await message.channel.send(f'Hello! Starting {self.quiz["name"]} now!')

    async def _send_question(self, message: Message):
        question = self.get_current_question(message.author)
        msg = _format_question(question)
        logger.info(f'Sending question to {message.author.name}')
        await message.channel.send(msg)

    async def _process_answer(self, message: Message):

        result = self.check_answer(message.author, message.content)

        if result:
            logger.info(f'Received correct answer {message.author.name}')
            await message.channel.send('Correct')
        else:
            logger.info(f'Received wrong answer {message.author.name}')
            await message.channel.send('Wrong')

    async def _end_quiz(self, message: Message):
        logger.info(f'Quiz ended for {message.author.name}')
        result = self.get_score_sheet(message.author)
        self.end_quiz(message.author)

        await message.channel.send(result)

    def add_participant(self, user, questions):
        participant = Participant(user, 0, len(questions), questions, [], State.WAITING)
        self.participants[user] = participant

    def get_current_question(self, user):
        participant = self.participants[user]
        question = participant.questions[participant.current_question]
        participant.state = State.ANSWERING
        return question

    def check_answer(self, user, answer):
        participant = self.participants[user]
        question = participant.questions[participant.current_question]

        try:
            choice = int(answer) - 1
            answer = question['answers'][choice]
        except ValueError or IndexError:
            answer = answer.content

        participant.state = State.WAITING

        if answer == question['correct_answer']:
            participant.score_sheet.append(1)
            return True
        else:
            participant.score_sheet.append(0)
            return False

    def next_question(self, user):
        participant = self.participants[user]
        participant.current_question += 1

    def get_score_sheet(self, user):
        participant = self.participants[user]
        return _format_results(participant.score_sheet)

    def end_quiz(self, user):
        self.participants.pop(user)


def setup_quiz(quiz):
    questions = quiz['questions']

    if quiz['options']['question_order'] == 'random':
        random.shuffle(questions)

    for question in questions:
        question['correct_answer'] = question['answers'][question['correct']]
        if quiz['options']['answer_order'] == 'random':
            random.shuffle(question['answers'])

    return questions


def _format_question(question):
    text = f'{question["text"]}\n'
    answers = question["answers"]

    i = 1
    for answer in answers:
        text += f'{i}) {answer}\n'
        i += 1

    return text


def _format_results(score_sheet):
    text = 'Your results:\n'
    f_score = 0

    for count, score in enumerate(score_sheet):
        f_score += score
        text += f'Question {count + 1}: {"Correct" if score else "Wrong"}\n'

    text += '\n'

    text += f'Final score: {f_score}'

    return text
