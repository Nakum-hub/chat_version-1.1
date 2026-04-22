import { describe, expect, it } from 'vitest';
import { QUESTIONS } from '../chatbot-questions';

describe('QUESTIONS', () => {
  it('includes the expected 16 assessment questions', () => {
    expect(QUESTIONS).toHaveLength(16);
  });

  it('has a non-empty question for every domain', () => {
    for (const question of QUESTIONS) {
      expect(question.question.trim(), `question missing for "${question.domain}"`).toBeTruthy();
    }
  });

  it('does not contain unresolved placeholder tokens', () => {
    for (const question of QUESTIONS) {
      expect(
        question.question,
        `placeholder found for "${question.domain}"`
      ).not.toMatch(/%%[A-Z0-9_]+%%|USER_QUERY/i);
    }
  });
});
