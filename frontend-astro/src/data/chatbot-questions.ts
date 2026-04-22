/**
 * Cyberfyx Compliance Evaluation Chatbot — Question Data
 * ISO 27001 Domain Coverage: 16 domains, 3 tiers, weighted scoring
 *
 * Tier 1 Critical    (weight 3) — Governance, Risk, Audit, Compliance
 * Tier 2 High Impact (weight 2) — Access, Incidents, Resilience, Vuln, Data, CERT-In
 * Tier 3 Operational (weight 1) — Docs, Monitoring, Awareness, Assets, Suppliers, Change
 */

export type AnswerValue = 'yes' | 'partial' | 'no';
export type Tier = 1 | 2 | 3;

export interface ChatbotQuestion {
  id: number;
  domain: string;
  tier: Tier;
  weight: 1 | 2 | 3;
  question: string;
  hint: string; // Helper text shown beneath the question
  gap: string;  // Gap text shown in final report for no/partial answers
  recommendation: string; // Short recommendation text
}

export const QUESTIONS: ChatbotQuestion[] = [
  {
    id: 1,
    domain: 'Governance',
    tier: 1,
    weight: 3,
    question: 'Do you have a formally defined and maintained ISMS covering scope, policies, roles, and periodic reviews?',
    hint: 'This includes documented policy approvals, defined scope boundaries, and scheduled management reviews.',
    gap: 'Missing governance structure, unclear scope, or lack of periodic review.',
    recommendation: 'Establish a formal ISMS with defined scope, assigned roles, and a scheduled review calendar aligned to ISO 27001 Clause 4–6.',
  },
  {
    id: 2,
    domain: 'Risk Management',
    tier: 1,
    weight: 3,
    question: 'Do you manage risk end to end by identifying, assessing, treating, and regularly reviewing risks?',
    hint: 'Think about whether your team has a documented risk register and a defined treatment plan that gets revisited.',
    gap: 'Unstructured risk lifecycle or unmanaged residual risks.',
    recommendation: 'Implement a formal risk management process covering identification, assessment, treatment, and periodic review per ISO 27001 Clause 6.1.',
  },
  {
    id: 3,
    domain: 'Access Control',
    tier: 2,
    weight: 2,
    question: 'Are access rights controlled through provisioning, least privilege, MFA, and periodic lifecycle review?',
    hint: 'Consider joiner/mover/leaver processes, quarterly access reviews, and whether MFA is enforced on critical systems.',
    gap: 'Excessive access rights, weak authentication, or absence of lifecycle controls.',
    recommendation: 'Deploy a formal Identity & Access Management (IAM) process with role-based access, MFA enforcement, and quarterly recertification.',
  },
  {
    id: 4,
    domain: 'Documentation',
    tier: 3,
    weight: 1,
    question: 'Are your security policies and procedures documented, approved, communicated, and regularly reviewed?',
    hint: 'Check if policies have version histories, approval signatures, and are accessible to the people who need them.',
    gap: 'Missing, outdated, or inconsistently implemented documentation.',
    recommendation: 'Establish a document control process with defined review cycles, version control, and staff acknowledgement records.',
  },
  {
    id: 5,
    domain: 'Incident Management',
    tier: 2,
    weight: 2,
    question: 'Do you have an incident management process covering detection, response, reporting, escalation, and lessons learned?',
    hint: 'This includes an incident response plan, defined severity tiers, and post-incident review meetings.',
    gap: 'No structured incident handling or continuous improvement process.',
    recommendation: 'Develop and test an Incident Response Plan (IRP) that covers detection through post-incident review with documented lessons learned.',
  },
  {
    id: 6,
    domain: 'Monitoring',
    tier: 3,
    weight: 1,
    question: 'Are system activities logged, alerts escalated, and logs reviewed regularly?',
    hint: 'Think about SIEM tools, log retention periods, and who reviews alerts and when.',
    gap: 'Lack of security visibility or delayed threat detection.',
    recommendation: 'Implement centralised logging and monitoring (SIEM), define alert escalation paths, and schedule regular log reviews.',
  },
  {
    id: 7,
    domain: 'Awareness Training',
    tier: 3,
    weight: 1,
    question: 'Do employees receive regular security awareness training, phishing simulations, and completion tracking?',
    hint: 'Consider phishing simulations, e-learning completion rates, and yearly refreshers.',
    gap: 'Elevated human risk due to unmeasured awareness programmes.',
    recommendation: 'Deploy a structured security awareness programme with at least annual training, phishing simulations, and completion tracking.',
  },
  {
    id: 8,
    domain: 'Resilience',
    tier: 2,
    weight: 2,
    question: 'Do you maintain tested backups and disaster recovery or business continuity processes with defined RTO/RPO targets?',
    hint: 'Have backups been restored in a test environment recently? Is there a documented DRP/BCP?',
    gap: 'Risk of unrecoverable data loss or untested recovery processes.',
    recommendation: 'Define and regularly test a Disaster Recovery Plan (DRP) with documented RTO/RPO targets and verified backup restoration.',
  },
  {
    id: 9,
    domain: 'Internal Audit',
    tier: 1,
    weight: 3,
    question: 'Do you conduct ISMS internal audits, management reviews, and corrective action tracking to closure?',
    hint: 'Look for scheduled audit calendars, audit reports, and nonconformity trackers.',
    gap: 'No independent validation cycle or structured improvement process.',
    recommendation: 'Establish an annual internal audit programme per ISO 27001 Clause 9.2, with management reviews and a tracked corrective action register.',
  },
  {
    id: 10,
    domain: 'Compliance Validation',
    tier: 1,
    weight: 3,
    question: 'Are security controls tested, evidenced, and mapped to applicable legal, regulatory, and contractual requirements?',
    hint: 'This covers ISO 27001 control testing, evidence collection, and mapping to regulations like GDPR or IT Act.',
    gap: 'Weak control implementation or misalignment with compliance obligations.',
    recommendation: 'Maintain a compliance register mapping controls to obligations, with regular control effectiveness testing and evidence collection.',
  },
  {
    id: 11,
    domain: 'Asset Management',
    tier: 3,
    weight: 1,
    question: 'Do you maintain an asset inventory with data classification and assigned owners?',
    hint: 'Think about asset inventories, data classification labels, and ownership assignments.',
    gap: 'Poor asset visibility and absence of data classification schemes.',
    recommendation: 'Implement an Asset Management programme with a maintained inventory, classification policy, and assigned asset owners.',
  },
  {
    id: 12,
    domain: 'Vulnerability Management',
    tier: 2,
    weight: 2,
    question: 'Are vulnerabilities identified through regular scanning, prioritised by severity, and remediated within defined SLAs?',
    hint: 'Consider automated scanning tools, patch management cycles, and CVSS-based prioritisation.',
    gap: 'Sustained exposure due to unresolved or untracked vulnerabilities.',
    recommendation: 'Deploy automated vulnerability scanning, define SLA-based remediation windows by severity, and track remediation status centrally.',
  },
  {
    id: 13,
    domain: 'Supplier Security',
    tier: 3,
    weight: 1,
    question: 'Do third-party suppliers have documented security requirements, questionnaires, and contractual security clauses?',
    hint: 'Check for vendor security questionnaires, contractual security clauses, and periodic supplier reviews.',
    gap: 'Unmanaged third-party and supply chain risks.',
    recommendation: 'Establish a Supplier Security Policy with due diligence questionnaires, contractual security obligations, and periodic reassessment.',
  },
  {
    id: 14,
    domain: 'Change Management',
    tier: 3,
    weight: 1,
    question: 'Are system and infrastructure changes controlled through formal review gates, advisory oversight, and rollback plans?',
    hint: 'Look for change advisory boards (CAB), change request tickets, and rollback procedures.',
    gap: 'Uncontrolled changes introducing avoidable security risks.',
    recommendation: 'Enforce a Change Management Process with mandatory security review for significant changes, CAB approvals, and rollback plans.',
  },
  {
    id: 15,
    domain: 'Data Protection',
    tier: 2,
    weight: 2,
    question: 'Do you protect data with encryption at rest and in transit, access controls, and secure handling or disposal procedures?',
    hint: 'Consider TLS enforcement, disk encryption, DLP tools, and secure media disposal policies.',
    gap: 'Elevated risk of data breach or unauthorised data exposure.',
    recommendation: 'Implement data protection controls including encryption (at rest & in transit), DLP, secure disposal procedures, and a data handling policy.',
  },
  {
    id: 16,
    domain: 'CERT-In Compliance',
    tier: 2,
    weight: 2,
    question: 'Do you have an incident reporting process that meets CERT-In requirements, including the 6-hour mandatory reporting window?',
    hint: 'India\'s CERT-In mandates mandatory incident reporting within 6 hours for specific incident types. Does your IRP reflect this?',
    gap: 'Non-compliance with CERT-In directives and inability to meet mandatory reporting timelines.',
    recommendation: 'Update your Incident Response Plan to explicitly address CERT-In reporting obligations, designate a CISO/POC, and run a tabletop drill.',
  },
];

// Pre-computed lookup maps
export const QUESTION_MAP = new Map<number, ChatbotQuestion>(
  QUESTIONS.map(q => [q.id, q])
);

export const MAX_WEIGHTED_SCORE = QUESTIONS.reduce((sum, q) => sum + q.weight, 0);
// 4×3 + 6×2 + 6×1 = 12 + 12 + 6 = 30

export type MaturityLevel = 'High' | 'Medium' | 'Low';

export const MATURITY_THRESHOLDS = {
  HIGH: 85,   // ≥ 85%
  MEDIUM: 50, // 50–84%
  // LOW: < 50%
} as const;

export function getMaturityLevel(percentage: number): MaturityLevel {
  if (percentage >= MATURITY_THRESHOLDS.HIGH) return 'High';
  if (percentage >= MATURITY_THRESHOLDS.MEDIUM) return 'Medium';
  return 'Low';
}

export const MATURITY_CONFIG = {
  High: {
    label: 'High Maturity',
    badge: '🛡️',
    colour: '#16a34a',
    bgColour: 'rgba(22, 163, 74, 0.12)',
    description: 'Most controls are in place. Your organisation is approaching audit readiness with only minor improvements needed.',
    cta: 'Let Cyberfyx conduct a final pre-audit gap assessment to certify your readiness.',
  },
  Medium: {
    label: 'Medium Maturity',
    badge: '⚠️',
    colour: '#E78731',
    bgColour: 'rgba(231, 135, 49, 0.12)',
    description: 'Partial controls exist but lack consistency and formal documentation. A detailed gap assessment and targeted control strengthening is required.',
    cta: 'Cyberfyx can deliver a structured gap assessment and a prioritised remediation roadmap.',
  },
  Low: {
    label: 'Low Maturity',
    badge: '🚨',
    colour: '#dc2626',
    bgColour: 'rgba(220, 38, 38, 0.12)',
    description: 'Multiple significant gaps identified. Your organisation lacks a structured ISMS. A full ISO 27001 implementation programme is strongly recommended.',
    cta: 'Cyberfyx specialises in end-to-end ISO 27001 implementation — let\'s build your ISMS from the ground up.',
  },
} as const;
