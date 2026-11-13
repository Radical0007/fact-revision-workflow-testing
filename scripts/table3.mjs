import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const data = readFileSync(new URL('../results/table3-counts.csv', import.meta.url), 'utf8')
const [header, ...lines] = data.trimEnd().split(/\r?\n/)
assert.equal(header, 'version,shape,seed,stratum,trials,violating_trials,requests')

const groups = new Map()
const number = value => {
  assert.match(value, /^(0|[1-9]\d*)$/)
  return Number(value)
}
for (const line of lines) {
  const columns = line.split(',')
  assert.equal(columns.length, 7)
  const [version, shape, seed, stratum] = columns
  const [trials, violations, requests] = columns.slice(4).map(number)
  const key = [version, shape, seed, stratum].join('/')
  assert.ok(!groups.has(key), `duplicate group: ${key}`)
  assert.ok(violations <= trials && requests === trials * 3, `count mismatch: ${key}`)
  groups.set(key, { trials, violations, requests })
}
assert.equal(groups.size, 240)

// Columns in the paper: legacy/base, fixed/base, legacy/extension, fixed/extension.
const paper = { single: [3360, 0, 240, 0], random: [2945, 0, 211, 0], full: [0, 0, 0, 0] }
const versions = ['legacy', 'fixed']
const seeds = Array.from({ length: 20 }, (_, index) => 101 + index)
console.log('Table 3 | legacy/base14 | fixed/base14 | legacy/extension | fixed/extension | requests/version')
for (const [shape, published] of Object.entries(paper)) {
  const cells = []
  const violations = []
  const requests = { legacy: 0, fixed: 0 }
  let randomLegacyTotal = 0
  let randomLegacyFailures = 0
  for (const stratum of ['base14', 'extension']) {
    for (const version of versions) {
      let trials = 0
      let failures = 0
      for (const seed of seeds) {
        const key = [version, shape, seed, stratum].join('/')
        const group = groups.get(key)
        assert.ok(group, `missing group: ${key}`)
        assert.equal(group.trials, stratum === 'base14' ? 168 : 12, `trials: ${key}`)
        failures += group.violations
        trials += group.trials
        requests[version] += group.requests
      }
      cells.push(`${failures}/${trials}`)
      violations.push(failures)
      if (version === 'legacy' && shape === 'random') {
        randomLegacyTotal += trials
        randomLegacyFailures += failures
      }
    }
  }
  assert.deepEqual(violations, published, `violations differ from Table 3 for ${shape}`)
  assert.deepEqual(requests, { legacy: 10800, fixed: 10800 })
  console.log([shape, ...cells, requests.legacy].join(' | '))
  if (shape === 'random') {
    const percent = (100 * randomLegacyFailures / randomLegacyTotal).toFixed(2)
    console.log(`Random subset, before repair: ${randomLegacyFailures}/${randomLegacyTotal} = ${percent}%`)
  }
}
