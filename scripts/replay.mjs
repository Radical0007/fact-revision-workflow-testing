import { readFileSync } from 'node:fs'
import { factFields, frameChecks } from './frame-checks.mjs'

// The fixture supplies both observations independently of the expected-state calculation.
const source = process.argv[2] ?? new URL('../examples/one-field.json', import.meta.url)
const { before, patch, patchResponse, getResponse } = JSON.parse(readFileSync(source, 'utf8'))
for (const field of factFields) {
  if (!Object.hasOwn(before, field)) throw new Error(`Missing pre-state field: ${field}`)
}
const checks = frameChecks({
  initialInput: before, initialState: before, patch,
  updated: patchResponse, persisted: getResponse, executedRequests: 3,
})

const submitted = factFields.filter(field => Object.hasOwn(patch, field))
console.log('Offline replay; submitted fact keys:', submitted.join(', '))
console.log('field | pre-state | expected | PATCH observed | GET observed')
const format = value => value === undefined ? '<absent>' : JSON.stringify(value)
for (const field of factFields) {
  const response = checks.find(check => check.id === `fact_value:${field}`)
  const readback = checks.find(check => check.id === `persisted_fact:${field}`)
  const values = [before[field], response.expected, response.observed, readback.observed].map(format)
  console.log([field, ...values].join(' | '))
}
for (const [label, prefix] of [['PATCH', 'fact_value:'], ['GET', 'persisted_fact:']]) {
  const fields = checks.filter(check => check.id.startsWith(prefix))
  console.log(`${label} field checks: ${fields.filter(check => check.pass).length}/${fields.length} passed`)
}
const failed = checks.filter(check => !check.pass)
for (const check of failed) {
  console.error(`FAIL ${check.id}: expected ${format(check.expected)}, observed ${format(check.observed)}`)
}
console.log(`Offline contract checks: ${checks.length - failed.length}/${checks.length} passed`)
if (failed.length) process.exitCode = 1
