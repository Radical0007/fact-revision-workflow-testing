"""Enumerate the finite model used in Table 5 and check its historical totals."""

import csv
import hashlib
import json
from collections import Counter
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def observation(sequence, complete):
    values = {'x': 0, 'y': 0}
    stamps = {'x': 0, 'y': 0}
    artifact = 'A'
    artifact_stamp = 0
    global_version = 1
    for action in sequence:
        if action == 'admin++':
            global_version += 1
        elif action.startswith('artifact='):
            value = action[-1]
            if value != artifact:
                artifact_stamp += 1
                artifact = value
        else:
            key = action[0]
            value = int(action[-1])
            if values[key] != value:
                values[key] = value
                stamps[key] += 1
                global_version += 1

    keys = ['x', 'y'] if complete else ['x']
    return {
        'approved': True,
        'approved_global_version': 1,
        'current_global_version': global_version,
        'dependency_complete': complete,
        'approved_projection': {key: 0 for key in keys},
        'current_projection': {key: values[key] for key in keys},
        'approved_dependency_stamps': {key: 0 for key in keys},
        'current_dependency_stamps': {key: stamps[key] for key in keys},
        'approved_artifact_sha256': hashlib.sha256(b'A').hexdigest(),
        'current_artifact_sha256': hashlib.sha256(artifact.encode()).hexdigest(),
        'approved_artifact_revision': 0,
        'current_artifact_revision': artifact_stamp,
    }


def history_oracle(sequence):
    prior = {'x': 0, 'y': 0, 'artifact': 'A'}
    valid = True
    for action in sequence:
        if action == 'admin++':
            continue
        name, value = action.split('=')
        if name in ('x', 'y'):
            value = int(value)
        if prior[name] != value:
            valid = False
        prior[name] = value
    return 'accept' if valid else 'reject'


def never_invalidate(state):
    return 'accept' if state['approved'] else 'reject'


def global_version_equality(state):
    if state['approved'] and state['approved_global_version'] == state['current_global_version']:
        return 'accept'
    return 'reject'


def content_projection(state):
    if not state['dependency_complete']:
        return 'unknown'
    if not state['approved']:
        return 'reject'
    if state['current_artifact_sha256'] != state['approved_artifact_sha256']:
        return 'reject'
    return 'accept' if state['approved_projection'] == state['current_projection'] else 'reject'


def dependency_revision_stamps(state):
    if not state['dependency_complete']:
        return 'unknown'
    if not state['approved']:
        return 'reject'
    if state['current_artifact_sha256'] != state['approved_artifact_sha256']:
        return 'reject'
    return 'accept' if state['approved_dependency_stamps'] == state['current_dependency_stamps'] else 'reject'


def fact_and_artifact_revision_stamps(state):
    if not state['dependency_complete']:
        return 'unknown'
    if not state['approved']:
        return 'reject'
    if state['current_artifact_revision'] != state['approved_artifact_revision']:
        return 'reject'
    if state['current_artifact_sha256'] != state['approved_artifact_sha256']:
        return 'reject'
    return 'accept' if state['approved_dependency_stamps'] == state['current_dependency_stamps'] else 'reject'


MONITORS = (
    never_invalidate,
    global_version_equality,
    content_projection,
    dependency_revision_stamps,
    fact_and_artifact_revision_stamps,
)


def main():
    protocol = json.loads((ROOT / 'protocols/table5.json').read_text(encoding='utf-8'))
    complete_counts = {monitor.__name__: Counter() for monitor in MONITORS}
    incomplete_unknown = Counter()
    sequences = 0
    for length in protocol['lengths']:
        for sequence in product(protocol['operations'], repeat=length):
            sequences += 1
            truth = history_oracle(sequence)
            for complete in protocol['completeness_strata']:
                state = observation(sequence, complete)
                for monitor in MONITORS:
                    name = monitor.__name__
                    prediction = monitor(state)
                    if complete:
                        counts = complete_counts[name]
                        counts['sequences'] += 1
                        counts['valid' if truth == 'accept' else 'invalid'] += 1
                        counts['false_accepts'] += (truth == 'reject' and prediction == 'accept')
                        counts['false_rejects'] += (truth == 'accept' and prediction == 'reject')
                        counts['unknown'] += (prediction == 'unknown')
                    elif prediction == 'unknown':
                        incomplete_unknown[name] += 1

    if sequences != protocol['expected_operation_sequences']:
        raise ValueError(f"Enumeration produced {sequences} sequences")
    with (ROOT / 'results/table5.csv').open(encoding='utf-8', newline='') as source:
        historical = list(csv.DictReader(source))
    if [row['checker'] for row in historical] != list(complete_counts):
        raise ValueError('Recorded and computed checker lists differ')
    print('Table 5, complete dependencies, history-sensitive contract')
    print('checker sequences valid invalid false_accepts false_rejects unknown')
    for row in historical:
        name = row.pop('checker')
        computed = dict(complete_counts[name])
        if computed != {key: int(value) for key, value in row.items()}:
            raise ValueError(f"Counts differ from the historical record for {name}: {computed}")
        print(name, *(computed[key] for key in row))
    aware = ('content_projection', 'dependency_revision_stamps', 'fact_and_artifact_revision_stamps')
    if incomplete_unknown != {name: sequences for name in aware}:
        raise ValueError(f"Unexpected incomplete-dependency results: {incomplete_unknown}")
    print(f'Incomplete dependencies: each of the three dependency-aware checkers returned unknown {sequences} times.')


if __name__ == '__main__':
    main()
