from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from datetime import timedelta

from .models import Question, Choice


def create_question(question_text, days, choice=True):
    """ Creates and returns a question for testing. """
    date = timezone.now() + timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=date)
    if choice:
        create_choice(question)
    return question


def create_question_list(question_text, days, num_questions):
    """ Creates and returns n questions for n equal to num_questions. """
    question_list = []
    for n in range(num_questions):
        question_list.append(
            create_question(f'{question_text} number {n}', days)
        )
    return question_list


def create_choice(question, choice_text=None, votes=0):
	""" Create a choice for a given question object. """
	if choice_text is None:
		choice_text = 'Sample choice'
	choice = Choice.objects.create(
		question = question,
		choice_text = choice_text,
		votes = votes
	)
	return choice


def create_choice_list(question, num_choices, choice_text=None):
	choice_list = []
	if choice_text is None:
		choice_text = 'Sample choice'
	for n in range(num_choices):
		choice_list.append(create_choice(
			question = question,
			choice_text=f'{choice_text} number {n}...'
		))
	return choice_list


class IndexViewTests(TestCase):

    def no_test_no_questions_shown(self):
        """ Checks if the index page has no questions to show. """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
            'This looks too clean. Wanna create your own question?'
        )
        self.assertQuerysetEqual(response.context['question_list'], [])

    def test_index_shows_pasts_questions(self):
        """ Questions published in the past can be shown. """
        question = create_question('A past question', -30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['question_list'], [question])

    def test_index_does_not_show_future_questions(self):
        """ Questions with future date shouldn't be shown. """
        question = create_question('A Future Question', 30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
            'This looks too clean. Wanna create your own question?'
        )
        self.assertQuerysetEqual(response.context['question_list'], [])

    def test_future_and_past_questions(self):
        """ Only 'past questions' have to be shown. """
        past_question = create_question('Another past question', -30)
        future_question = create_question('Another future question', 30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['question_list'], [past_question]
        )

    def test_two_past_question_are_shown(self):
        """ Index page shows two past questions. """
        question1 = create_question('Question 1', -5)
        question2 = create_question('Question 2', -3)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['question_list'],
            [question2, question1]
        )

    def test_no_more_than_five_questions_are_shown(self):
        """ Index page only shows the last five questions. """
        create_question_list('Question', 0.2, 6)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['question_list']), 5)


class QuestionsDetailsView(TestCase):

    def test_past_questions_details_are_shown(self):
        """ Raises a 200 success code for questions already published. """
        question = create_question('A published question', -30)
        response = self.client.get(
            reverse('polls:details', args=(question.id,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question.question_text)

    def test_future_questions_details_are_not_shown(self):
        """ Raises a 404 error code for questions yet to be published. """
        question = create_question('A future question', 30)
        response = self.client.get(
            reverse('polls:details', args=(question.id,))
        )
        self.assertEqual(response.status_code, 404)


class PollsVoteView(TestCase):

	def disabled_test_select_choice_and_vote(self):
		""" Checks if the vote count for a choice
		is updated correctly. """
		question = create_question('A question for testing', -30)
		response = self.client.get(
			reverse('polls:details', args=(question.id,))
		)
		# TODO: find a way to select a choice (in the HTML template) before
		# calling self.client.get(reverse('polls:vote' args=(question.id,)))


	def test_no_choice_selected(self):
		""" Test no seleced choice espected behaviour. """
		question = create_question('A question for testing', -30, choice=False)
		choices = create_choice_list(question, 3)
		response = self.client.get(
			reverse('polls:vote', args=(question.id,))
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(
			response.context['error_message'], 'Select an option!'
		)


class QuestonModelTests(TestCase):

    def test_was_published_recently_with_future_questions(self):
        """ Test if was_published_recently() returns False
        to questions "published" in the future. """
        time = timezone.now() + timedelta(days=30)
        question = Question(pub_date=time)
        self.assertIs(question.was_published_recently(), False)

    def test_was_published_recently_with_past_questions(self):
        """ Test if was_published_recently() returns False
        to questions published +24 hours ago. """
        time = timezone.now() - timedelta(days=2)
        question = Question(pub_date=time)
        self.assertIs(question.was_published_recently(), False)

    def test_was_published_recently_within_the_last_day(self):
        """ Test if was_published_recently() returns True
        to questions published within less thatn 24 hours. """
        time = timezone.now() - timedelta(days=0.5)
        question = Question(pub_date=time)
        self.assertIs(question.was_published_recently(), True)
