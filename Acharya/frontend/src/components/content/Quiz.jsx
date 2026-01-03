import { useState } from 'react';
import './Quiz.css';

const Quiz = ({ questions }) => {
    const [currentQuestion, setCurrentQuestion] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [showResult, setShowResult] = useState(false);
    const [score, setScore] = useState(0);
    const [answers, setAnswers] = useState([]);

    if (!questions || questions.length === 0) {
        return (
            <div className="quiz-empty">
                <div className="empty-icon">🎯</div>
                <h3>No Quiz Available</h3>
                <p>Quiz questions are being generated or not available for this subtopic.</p>
            </div>
        );
    }

    const quizData = parseQuiz(questions);

    if (quizData.length === 0) {
        return (
            <div className="quiz-empty">
                <div className="empty-icon">🎯</div>
                <h3>No Quiz Available</h3>
                <p>Could not parse quiz data.</p>
            </div>
        );
    }

    const current = quizData[currentQuestion];
    const isAnswered = selectedAnswer !== null;
    const isCorrect = selectedAnswer === current.correctIndex;

    const handleSelect = (index) => {
        if (isAnswered) return;
        setSelectedAnswer(index);

        const newAnswers = [...answers, {
            question: currentQuestion,
            selected: index,
            correct: current.correctIndex,
            isCorrect: index === current.correctIndex
        }];
        setAnswers(newAnswers);

        if (index === current.correctIndex) {
            setScore(score + 1);
        }
    };

    const handleNext = () => {
        if (currentQuestion < quizData.length - 1) {
            setCurrentQuestion(currentQuestion + 1);
            setSelectedAnswer(null);
        } else {
            setShowResult(true);
        }
    };

    const handleRestart = () => {
        setCurrentQuestion(0);
        setSelectedAnswer(null);
        setShowResult(false);
        setScore(0);
        setAnswers([]);
    };

    if (showResult) {
        const percentage = Math.round((score / quizData.length) * 100);
        let message = '';
        let emoji = '';

        if (percentage >= 80) {
            message = 'Excellent! You\'ve mastered this topic!';
            emoji = '🎉';
        } else if (percentage >= 60) {
            message = 'Good job! Keep practicing!';
            emoji = '👍';
        } else if (percentage >= 40) {
            message = 'Not bad! Review the material and try again.';
            emoji = '📚';
        } else {
            message = 'Keep studying! You\'ll get better!';
            emoji = '💪';
        }

        return (
            <div className="quiz-results animate-slideUp">
                <div className="results-card">
                    <div className="results-emoji">{emoji}</div>
                    <h2 className="results-title">Quiz Complete!</h2>
                    <div className="results-score">
                        <span className="score-number gradient-text">{score}</span>
                        <span className="score-divider">/</span>
                        <span className="score-total">{quizData.length}</span>
                    </div>
                    <div className="results-percentage">
                        <div className="percentage-bar">
                            <div
                                className="percentage-fill"
                                style={{ width: `${percentage}%` }}
                            />
                        </div>
                        <span className="percentage-text">{percentage}%</span>
                    </div>
                    <p className="results-message">{message}</p>
                    <button className="restart-btn" onClick={handleRestart}>
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M1 4V10H7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M3.51 15C4.15 16.94 5.36 18.63 7.01 19.85C8.66 21.07 10.66 21.73 12.72 21.75C14.78 21.76 16.8 21.14 18.47 19.96C20.15 18.77 21.39 17.11 22.07 15.19C22.75 13.27 22.83 11.18 22.32 9.21C21.8 7.25 20.7 5.49 19.15 4.17C17.59 2.86 15.65 2.04 13.6 1.85C11.55 1.66 9.49 2.1 7.69 3.11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                        <span>Try Again</span>
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="quiz">
            <div className="quiz-header">
                <div className="quiz-progress">
                    <span className="progress-text">
                        Question {currentQuestion + 1} of {quizData.length}
                    </span>
                    <div className="progress-bar">
                        <div
                            className="progress-fill"
                            style={{ width: `${((currentQuestion + 1) / quizData.length) * 100}%` }}
                        />
                    </div>
                </div>
                <div className="quiz-score">
                    Score: <span className="score-value">{score}</span>
                </div>
            </div>

            <div className="quiz-card animate-slideUp" key={currentQuestion}>
                <div className="question-number">Q{currentQuestion + 1}</div>
                <h3 className="question-text">{current.question}</h3>

                <div className="options-list">
                    {current.options.map((option, index) => {
                        let optionClass = 'option';
                        if (isAnswered) {
                            if (index === current.correctIndex) {
                                optionClass += ' correct';
                            } else if (index === selectedAnswer) {
                                optionClass += ' incorrect';
                            }
                        }
                        if (index === selectedAnswer) {
                            optionClass += ' selected';
                        }

                        return (
                            <button
                                key={index}
                                className={optionClass}
                                onClick={() => handleSelect(index)}
                                disabled={isAnswered}
                            >
                                <span className="option-letter">
                                    {String.fromCharCode(65 + index)}
                                </span>
                                <span className="option-text">{option}</span>
                                {isAnswered && index === current.correctIndex && (
                                    <span className="option-icon correct-icon">✓</span>
                                )}
                                {isAnswered && index === selectedAnswer && index !== current.correctIndex && (
                                    <span className="option-icon incorrect-icon">✗</span>
                                )}
                            </button>
                        );
                    })}
                </div>

                {isAnswered && (
                    <div className={`feedback ${isCorrect ? 'correct' : 'incorrect'}`}>
                        {isCorrect ? (
                            <>
                                <p>🎉 Correct! Well done!</p>
                                {current.explanation && (
                                    <p className="explanation">💡 {current.explanation}</p>
                                )}
                            </>
                        ) : (
                            <>
                                <p>❌ Incorrect. The correct answer is: <strong>{current.options[current.correctIndex]}</strong></p>
                                {current.explanation && (
                                    <p className="explanation">💡 {current.explanation}</p>
                                )}
                            </>
                        )}
                    </div>
                )}

                <div className="quiz-actions">
                    <button
                        className="next-btn"
                        onClick={handleNext}
                        disabled={!isAnswered}
                    >
                        {currentQuestion < quizData.length - 1 ? (
                            <>
                                <span>Next Question</span>
                                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                    <path d="M12 5L19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                            </>
                        ) : (
                            <>
                                <span>See Results</span>
                                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M9 11L12 14L22 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    <path d="M21 12V19C21 20.1046 20.1046 21 19 21H5C3.89543 21 3 20.1046 3 19V5C3 3.89543 3.89543 3 5 3H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

// Parse quiz from various formats
const parseQuiz = (questions) => {
    if (Array.isArray(questions)) {
        return questions.map(q => ({
            question: q.question || q.q || 'Question',
            options: q.options || q.choices || [q.a, q.b, q.c, q.d].filter(Boolean) || ['Option 1', 'Option 2', 'Option 3', 'Option 4'],
            correctIndex: q.correctIndex ?? q.answer ?? q.correct ?? 0
        }));
    }

    if (typeof questions === 'string') {
        try {
            const parsed = JSON.parse(questions);
            if (Array.isArray(parsed)) {
                return parsed.map(q => ({
                    question: q.question || q.q || 'Question',
                    options: q.options || q.choices || [q.a, q.b, q.c, q.d].filter(Boolean) || ['Option 1', 'Option 2', 'Option 3', 'Option 4'],
                    correctIndex: q.correctIndex ?? q.answer ?? q.correct ?? 0
                }));
            }
        } catch {
            // Return empty if can't parse
            return [];
        }
    }

    return [];
};

export default Quiz;
