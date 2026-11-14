"""The observation contract encodes the project's scientific-integrity rules."""

from __future__ import annotations

from open_lab_builder.contracts import validate_document, validate_event_stream


def by_type(events, event_type):
    return next(e for e in events if e["type"] == event_type)


def test_example_log_is_a_valid_stream(events):
    assert validate_event_stream(events) == []


def test_the_agent_can_never_be_the_recorder(events):
    event = events[2]
    event["recorder"] = "agent"
    assert validate_document(event)


def test_agent_statements_are_claims_not_observations(events):
    statement = by_type(events, "agent.statement")
    statement["epistemic_status"] = "observed"
    assert validate_document(statement)


def test_observed_actions_cannot_be_labelled_as_claims(events):
    call = by_type(events, "tool.call")
    call["epistemic_status"] = "agent_claim"
    assert validate_document(call)


def test_derived_events_must_cite_their_sources(events):
    output = by_type(events, "agent.output")
    output["epistemic_status"] = "derived"
    assert validate_document(output)
    output["derived_from"] = [1]
    assert validate_document(output) == []


def test_tool_call_and_result_are_linked(events):
    call, result = by_type(events, "tool.call"), by_type(events, "tool.result")
    assert call["correlation_id"] == result["correlation_id"]
    del call["correlation_id"]
    assert validate_document(call)


def test_tool_call_requires_capability_and_arguments(events):
    call = by_type(events, "tool.call")
    del call["payload"]["arguments"]
    assert validate_document(call)


def test_only_the_supervisor_records_supervisor_actions(events):
    action = by_type(events, "supervisor.action")
    action["recorder"] = "agent_runtime"
    assert validate_document(action)


def test_unknown_run_state_is_rejected(events):
    events[0]["payload"]["to"] = "immortal"
    assert validate_document(events[0])


def test_sequence_gap_is_detected(events):
    del events[4]
    assert any("expected seq" in str(issue) for issue in validate_event_stream(events))


def test_reordering_is_detected(events):
    events[1], events[2] = events[2], events[1]
    assert validate_event_stream(events)


def test_events_from_another_run_are_detected(events):
    events[3]["run_id"] = "run-other"
    assert any("differs from the first event" in str(i) for i in validate_event_stream(events))


def test_messages_from_the_environment_are_recorded_by_the_runtime_as_observations(events):
    message = by_type(events, "environment.message")
    assert validate_document(message) == []
    for field, value in (("recorder", "supervisor"), ("epistemic_status", "agent_claim")):
        changed = dict(message, **{field: value})
        assert validate_document(changed), field
    for missing in ("kind", "text"):
        payload = {k: v for k, v in message["payload"].items() if k != missing}
        assert validate_document(dict(message, payload=payload)), missing
    assert validate_document(dict(message, payload={**message["payload"], "kind": "human"}))


def test_environment_messages_need_the_newer_minor_version(events):
    message = dict(by_type(events, "environment.message"), schema_version="1.0.0")
    # A 1.0.0 document is still valid under 1.1.0: the type was added, nothing removed.
    assert validate_document(message) == []
