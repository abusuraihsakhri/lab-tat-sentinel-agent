import test from 'node:test';
import assert from 'node:assert/strict';
import { evaluateTask } from '../web/app.mjs';

const base = {
  task_id: 'DEMO-1', target_identifier: 'SYNTH-1',
  primary_metric: 10, secondary_metric: 3,
  status_descriptor: 'NOMINAL', is_critical_flag: false
};

test('routine task has no alerts', () => {
  const output = evaluateTask(base);
  assert.equal(output.overall_urgency, 'ROUTINE');
  assert.equal(output.total_alerts, 0);
});

test('primary and secondary threshold alerts are elevated', () => {
  const output = evaluateTask({...base, primary_metric: 30, secondary_metric: 15});
  assert.equal(output.overall_urgency, 'ELEVATED_RISK');
  assert.equal(output.total_alerts, 2);
});

test('critical flag takes precedence', () => {
  const output = evaluateTask({...base, is_critical_flag: true});
  assert.equal(output.overall_urgency, 'CRITICAL_STAT_PANIC');
  assert.equal(output.critical_alerts_count, 1);
});

test('anomaly descriptor flags conformance', () => {
  assert.equal(evaluateTask({...base, status_descriptor: 'DISCORDANT'}).total_alerts, 1);
});

test('reject invalid numbers and empty identifiers', () => {
  assert.throws(() => evaluateTask({...base, primary_metric: NaN}), /finite/);
  assert.throws(() => evaluateTask({...base, task_id: ' '}), /required/);
});

test('browser-only result cannot be confused with an HMAC audit', () => {
  const output = evaluateTask(base);
  assert.equal(output.audit_hash, undefined);
  assert.match(output.cryptographic_audit, /Not available/);
});
