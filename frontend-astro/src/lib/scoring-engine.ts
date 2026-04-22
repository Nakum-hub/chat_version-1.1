/**
 * Cyberfyx WeightedScoringEngine
 *
 * Deterministic, zero-latency scoring algorithm for the ISO 27001 compliance chatbot.
 * No LLM required — all scoring is computed client-side from a finite answer set.
 *
 * Algorithm:
 *   score_i = answer_value_i × weight_i
 *   where YES = 1.0 | PARTIAL = 0.5 | NO = 0.0
 *
 *   percentage = (Σ score_i / MAX_WEIGHTED_SCORE) × 100
 *   MAX_WEIGHTED_SCORE = 30  (4×3 + 6×2 + 6×1)
 */

import {
  QUESTIONS,
  MAX_WEIGHTED_SCORE,
  getMaturityLevel,
  MATURITY_CONFIG,
  type AnswerValue,
  type MaturityLevel,
  type ChatbotQuestion,
} from '../data/chatbot-questions';

export const ANSWER_WEIGHT: Record<AnswerValue, number> = {
  yes: 1.0,
  partial: 0.5,
  no: 0.0,
};

export interface AnswerRecord {
  questionId: number;
  answer: AnswerValue;
}

export interface GapItem {
  domain: string;
  tier: 1 | 2 | 3;
  weight: 1 | 2 | 3;
  gap: string;
  recommendation: string;
  severity: 'critical' | 'high' | 'medium';
}

export interface ScoringResult {
  /** Raw weighted score: Σ(answer_value × weight)  */
  rawScore: number;
  /** Maximum possible score = 30 */
  maxScore: number;
  /** Percentage score 0–100 (2 decimal places) */
  percentage: number;
  /** High / Medium / Low */
  maturityLevel: MaturityLevel;
  /** Maturity config (label, colour, description, cta) */
  maturityConfig: typeof MATURITY_CONFIG[MaturityLevel];
  /** Domains where answer was 'no' or 'partial' — sorted by severity */
  gaps: GapItem[];
  /** Counts */
  totalYes: number;
  totalPartial: number;
  totalNo: number;
}

function answerToSeverity(answer: AnswerValue, tier: 1 | 2 | 3): GapItem['severity'] {
  if (answer === 'no' && tier === 1) return 'critical';
  if (answer === 'no' && tier === 2) return 'high';
  return 'medium';
}

export class WeightedScoringEngine {
  /**
   * Compute the full scoring result from an array of answers.
   * Accepts partial answer sets — unanswered questions default to 0 (NO).
   */
  compute(answers: AnswerRecord[]): ScoringResult {
    const answerMap = new Map<number, AnswerValue>();
    for (const a of answers) {
      answerMap.set(a.questionId, a.answer);
    }

    let rawScore = 0;
    let totalYes = 0;
    let totalPartial = 0;
    let totalNo = 0;
    const gaps: GapItem[] = [];

    for (const q of QUESTIONS) {
      const answer = answerMap.get(q.id) ?? 'no';
      const contribution = ANSWER_WEIGHT[answer] * q.weight;
      rawScore += contribution;

      if (answer === 'yes') totalYes++;
      else if (answer === 'partial') totalPartial++;
      else totalNo++;

      // Collect gaps for partial and no answers
      if (answer !== 'yes') {
        gaps.push({
          domain: q.domain,
          tier: q.tier,
          weight: q.weight,
          gap: q.gap,
          recommendation: q.recommendation,
          severity: answerToSeverity(answer, q.tier),
        });
      }
    }

    const percentage = Math.round((rawScore / MAX_WEIGHTED_SCORE) * 10000) / 100;
    const maturityLevel = getMaturityLevel(percentage);

    // Sort gaps: critical first, then high, then medium; within tier by weight desc
    const severityOrder: Record<GapItem['severity'], number> = {
      critical: 0,
      high: 1,
      medium: 2,
    };
    gaps.sort((a, b) => {
      const sev = severityOrder[a.severity] - severityOrder[b.severity];
      if (sev !== 0) return sev;
      return b.weight - a.weight;
    });

    return {
      rawScore: Math.round(rawScore * 100) / 100,
      maxScore: MAX_WEIGHTED_SCORE,
      percentage,
      maturityLevel,
      maturityConfig: MATURITY_CONFIG[maturityLevel],
      gaps,
      totalYes,
      totalPartial,
      totalNo,
    };
  }

  /**
   * Returns progress percentage for a given number of answered questions.
   */
  progressPercent(answeredCount: number): number {
    return Math.round((answeredCount / QUESTIONS.length) * 100);
  }
}

export const scoringEngine = new WeightedScoringEngine();
