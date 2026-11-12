
from drafter import *
from dataclasses import dataclass, field


# -------------------------
# DATA CLASSES
# -------------------------

@dataclass
class Flashcard:
    """Stores the information for one flashcard."""
    question: str
    answer: str
    subject: str
    mastered: bool


@dataclass
class State:
    """Stores information that the application needs while it runs."""
    flashcards: list[Flashcard] = field(default_factory=list)
    username: str = "Student"
    current_subject: str = "All"
    cards_studied: int = 0
    quiz_score: int = 0


# -------------------------
# HOME PAGE
# -------------------------

@route
def index(state: State) -> Page:
    """Displays the home page and navigation buttons."""
    return Page(state, [
        Header("Flashcard Manager"),
        "Welcome to your study application!",
        "Create flashcards, study them, and test your knowledge.",
        Button("Create Flashcard", "create_flashcard"),
        Button("View Flashcards", "view_flashcards"),
        Button("Study Mode", "study_mode"),
        Button("Quiz Mode", "quiz_mode")
    ])


# -------------------------
# CREATE FLASHCARDS
# -------------------------

@route
def create_flashcard(state: State) -> Page:
    """Displays a form where the user can enter a new flashcard."""
    return Page(state, [
        Header("Create a Flashcard"),
        "Enter your question:",
        TextBox("question"),
        "Enter your answer:",
        TextArea("answer"),
        "Enter the subject:",
        TextBox("subject"),
        Button("Save Flashcard", "save_flashcard"),
        Button("Home", "index")
    ])


@route
def save_flashcard(state: State, question: str, answer: str, subject: str) -> Page:
    """Checks the new flashcard information and saves the card."""
    if question.strip() == "" or answer.strip() == "":
        return Page(state, [
            Header("Missing Information"),
            "Please enter both a question and an answer.",
            Button("Try Again", "create_flashcard")
        ])

    new_card = Flashcard(question, answer, subject, False)
    state.flashcards.append(new_card)

    return view_flashcards(state)


# -------------------------
# VIEW FLASHCARDS
# -------------------------

@route
def view_flashcards(state: State) -> Page:
    """Displays all saved flashcards with edit and delete buttons."""
    content = [Header("My Flashcards")]

    if len(state.flashcards) == 0:
        content.append("You have no flashcards yet.")

    for i in range(len(state.flashcards)):
        flashcard = state.flashcards[i]

        content.append("Question: " + flashcard.question)
        content.append("Subject: " + flashcard.subject)
        content.append("Mastered: " + str(flashcard.mastered))

        content.append(
            Button("Edit", "edit_flashcard",
                   [Argument("card_index", i)])
        )

        content.append(
            Button("Delete", "delete_flashcard",
                   [Argument("card_index", i)])
        )

    content.append(Button("Create Flashcard", "create_flashcard"))
    content.append(Button("Home", "index"))

    return Page(state, content)


# -------------------------
# EDIT FLASHCARDS
# -------------------------

@route
def edit_flashcard(state: State, card_index: int) -> Page:
    """Displays a form containing the selected card's current information."""
    flashcard = state.flashcards[card_index]

    return Page(state, [
        Header("Edit Flashcard"),
        "Question:",
        TextBox("question", flashcard.question),
        "Answer:",
        TextArea("answer", flashcard.answer),
        "Subject:",
        TextBox("subject", flashcard.subject),
        Button("Save Changes", "save_edit",
               [Argument("card_index", card_index)]),
        Button("Cancel", "view_flashcards")
    ])


@route
def save_edit(state: State, card_index: int,
              question: str, answer: str, subject: str) -> Page:
    """Updates the selected flashcard with the information from the form."""
    if question.strip() == "" or answer.strip() == "":
        return Page(state, [
            Header("Missing Information"),
            "Please enter both a question and an answer.",
            Button("Back to Flashcards", "view_flashcards")
        ])

    flashcard = state.flashcards[card_index]

    flashcard.question = question
    flashcard.answer = answer
    flashcard.subject = subject

    return view_flashcards(state)


# -------------------------
# DELETE FLASHCARDS
# -------------------------

@route
def delete_flashcard(state: State, card_index: int) -> Page:
    """Deletes the flashcard at the selected position in the list."""
    if 0 <= card_index < len(state.flashcards):
        state.flashcards.pop(card_index)

    return view_flashcards(state)


# -------------------------
# STUDY MODE
# -------------------------

@route
def study_mode(state: State, card_index: int = 0) -> Page:
    """Displays one flashcard question at a time during study mode."""
    if len(state.flashcards) == 0:
        return Page(state, [
            Header("No Flashcards"),
            "Create some flashcards before studying!",
            Button("Create Flashcards", "create_flashcard")
        ])

    if card_index >= len(state.flashcards):
        return Page(state, [
            Header("Study Complete!"),
            "You finished studying your flashcards.",
            "Cards studied: " + str(state.cards_studied),
            Button("Study Again", "study_mode"),
            Button("Home", "index")
        ])

    flashcard = state.flashcards[card_index]

    return Page(state, [
        Header("Study Mode"),
        "Question:",
        flashcard.question,
        Button("Reveal Answer", "reveal_answer",
               [Argument("card_index", card_index)])
    ])


@route
def reveal_answer(state: State, card_index: int) -> Page:
    """Displays the answer and gives the user the option to mark the card mastered."""
    flashcard = state.flashcards[card_index]
    state.cards_studied += 1

    return Page(state, [
        Header("Flashcard Answer"),
        "Question: " + flashcard.question,
        "Answer: " + flashcard.answer,
        "Mastered: " + str(flashcard.mastered),
        Button("Mark as Mastered", "mark_mastered",
               [Argument("card_index", card_index)]),
        Button("Next Card", "study_mode",
               [Argument("card_index", card_index + 1)]),
        Button("Home", "index")
    ])


@route
def mark_mastered(state: State, card_index: int) -> Page:
    """Changes the selected flashcard's mastered status to True."""
    state.flashcards[card_index].mastered = True

    return Page(state, [
        Header("Flashcard Updated"),
        "This flashcard has been marked as mastered!",
        Button("View Flashcards", "view_flashcards"),
        Button("Home", "index")
    ])


# -------------------------
# QUIZ MODE
# -------------------------

@route
def quiz_mode(state: State, card_index: int = 0) -> Page:
    """Displays quiz questions and shows the final score when the quiz ends."""
    if len(state.flashcards) == 0:
        return Page(state, [
            Header("No Flashcards"),
            "Create flashcards before taking a quiz!",
            Button("Create Flashcards", "create_flashcard")
        ])

    if card_index == 0:
        state.quiz_score = 0

    if card_index >= len(state.flashcards):
        return Page(state, [
            Header("Quiz Complete!"),
            "Your score: " + str(state.quiz_score)
            + " out of " + str(len(state.flashcards)),
            Button("Try Again", "quiz_mode"),
            Button("Home", "index")
        ])

    flashcard = state.flashcards[card_index]

    return Page(state, [
        Header("Quiz Mode"),
        "Question " + str(card_index + 1),
        flashcard.question,
        "Enter your answer:",
        TextBox("user_answer"),
        Button("Submit Answer", "check_answer",
               [Argument("card_index", card_index)])
    ])


@route
def check_answer(state: State, card_index: int, user_answer: str) -> Page:
    """Checks the user's answer and updates the quiz score if it is correct."""
    correct_answer = state.flashcards[card_index].answer

    if user_answer.strip().lower() == correct_answer.strip().lower():
        state.quiz_score += 1

    return quiz_mode(state, card_index + 1)


# -------------------------
# START THE APPLICATION
# -------------------------

start_server(State())






