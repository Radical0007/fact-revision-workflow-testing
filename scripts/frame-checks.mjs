// Independent contract projections. This module imports no application code.
export const factFields = Object.freeze(['title', 'location', 'occurredAt', 'studentName', 'studentNo', 'college', 'description', 'initialAction', 'peopleCount', 'injuredCount', 'ongoing'])
const equal = (a, b) => JSON.stringify(a) === JSON.stringify(b)
export const relationCheck = (id, expected, observed) => ({ id, expected, observed, pass: equal(expected, observed) })

export function frameChecks({ initialInput, initialState, patch, updated, persisted, executedRequests }) {
  const checks = [relationCheck('valid_patch_status', 200, updated.status), relationCheck('read_status', 200, persisted.status)]
  for (const field of factFields) {
    const expected = Object.hasOwn(patch, field) ? (typeof patch[field] === 'string' ? patch[field].trim() : patch[field]) : initialInput[field]
    checks.push(relationCheck(`fact_value:${field}`, expected, updated.body[field]))
    checks.push(relationCheck(`persisted_fact:${field}`, expected, persisted.body[field]))
  }
  checks.push(relationCheck('event_version_once', initialState.version + 1, updated.body.version))
  checks.push(relationCheck('fact_update_preserves_path', initialState.path, persisted.body.path))
  checks.push(relationCheck('exact_trial_budget', 3, executedRequests))
  return checks
}
