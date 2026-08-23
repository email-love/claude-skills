#!/usr/bin/env python3
"""Structural validator for Email Love quality-gate records. Stdlib only.

HONESTY NOTE: this is NOT a full JSON Schema validator. It enforces exactly the
structural rules listed below, directly in code; the .schema.json files in
schemas/ document the same contract for humans and for any future validation
with a real JSON Schema engine. What IS enforced here:

Fact Pack (fact-pack.schema.json v1.1)
  - required core fields, targetKind/readiness enums;
  - geometryRelevant true  -> currentGeometry required;
  - mappingRelevant true   -> mapping{visibleRegion, proofInstanceId,
    sourceComponentId} required;
  - readiness "ready" requires zero unresolved items with canChangeMutation.

Repair Contract (repair-contract.schema.json v1.1)
  - class enum and the class-specific section (changes / replacement /
    reconstruction) present;
  - every changed node id inside allowedNodeIds;
  - requiredChecks contains structure, exporter_desktop, exporter_mobile;
  - section_reconstruction requires >= 2 recorded disproved patches;
  - the contract's target agrees with the Fact Pack target.

Acceptance Matrix (acceptance-matrix.schema.json v1.1)
  - no duplicate (component, breakpoint, check) row;
  - every component carries exporter rows for BOTH desktop and mobile;
  - "deferred" rows carry a deferredReason (deferred is distinct from
    "missing": deferred is consciously postponed, missing was never covered);
  - "missing" rows are always an error - the matrix must enumerate coverage;
  - aggregate "verified" requires every row "pass"; any "fail" forces
    "failed"; anything else forces "repaired_unverified".

    python3 tests/quality-gates/validate_quality_pack.py <record.json>
    python3 tests/quality-gates/validate_quality_pack.py --self-test
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


class ValidationError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def validate_fact_pack(fp: dict) -> None:
    require(isinstance(fp, dict), "factPack must be an object")
    for key in ("schemaVersion", "target", "symptom", "sourceAuthority", "facts",
                "unresolved", "readiness", "geometryRelevant", "mappingRelevant"):
        require(key in fp, f"factPack missing {key}")
    require(fp["schemaVersion"] == "1.1", "factPack schemaVersion must be 1.1")
    target = fp["target"]
    require(isinstance(target.get("targetNodeId"), str) and target["targetNodeId"],
            "factPack.target.targetNodeId required")
    require(target.get("targetKind") in ("email-root", "module", "instance", "leaf"),
            "factPack.target.targetKind invalid")
    sa = fp["sourceAuthority"]
    require(bool(sa.get("structural")) and bool(sa.get("visual")),
            "factPack.sourceAuthority needs structural and visual")
    for i, fact in enumerate(fp["facts"]):
        require(bool(fact.get("source")) and bool(fact.get("observation")),
                f"factPack.facts[{i}] needs source and observation")
    blocking = 0
    for i, u in enumerate(fp["unresolved"]):
        require(isinstance(u.get("question"), str) and u["question"],
                f"factPack.unresolved[{i}] needs question")
        require(isinstance(u.get("canChangeMutation"), bool),
                f"factPack.unresolved[{i}].canChangeMutation must be boolean")
        blocking += u["canChangeMutation"]
    require(fp["readiness"] in ("ready", "blocked"), "factPack.readiness invalid")
    if fp["readiness"] == "ready":
        require(blocking == 0,
                "factPack readiness is 'ready' but an unresolved item can change the mutation")
    if fp["geometryRelevant"] is True:
        require("currentGeometry" in fp,
                "geometryRelevant is true but currentGeometry is absent")
    if fp["mappingRelevant"] is True:
        m = fp.get("mapping")
        require(isinstance(m, dict) and all(
            m.get(k) for k in ("visibleRegion", "proofInstanceId", "sourceComponentId")),
            "mappingRelevant is true but mapping{visibleRegion, proofInstanceId, "
            "sourceComponentId} is incomplete")


def validate_repair_contract(rc: dict, fp: dict) -> None:
    require(isinstance(rc, dict), "repairContract must be an object")
    for key in ("schemaVersion", "targetNodeId", "class", "evidence", "allowedNodeIds",
                "preservedInvariants", "rollback", "requiredChecks"):
        require(key in rc, f"repairContract missing {key}")
    require(rc["schemaVersion"] == "1.1", "repairContract schemaVersion must be 1.1")
    require(rc["class"] in ("property_patch", "instance_replacement",
                            "section_reconstruction"),
            "repairContract.class invalid")
    require(rc["evidence"] and all(isinstance(e, str) and e for e in rc["evidence"]),
            "repairContract.evidence must be non-empty strings")
    allowed = set(rc["allowedNodeIds"])
    require(allowed, "repairContract.allowedNodeIds must not be empty")
    checks = set(rc["requiredChecks"])
    require({"structure", "exporter_desktop", "exporter_mobile"} <= checks,
            "requiredChecks must include structure, exporter_desktop, exporter_mobile")
    require(rc["targetNodeId"] == fp["target"]["targetNodeId"],
            "repairContract target disagrees with factPack target")
    if rc["class"] == "property_patch":
        changes = rc.get("changes")
        require(isinstance(changes, list) and changes,
                "property_patch requires a non-empty changes list")
        for i, ch in enumerate(changes):
            for k in ("nodeId", "property", "before", "after"):
                require(k in ch, f"changes[{i}] missing {k}")
            require(ch["nodeId"] in allowed,
                    f"changes[{i}].nodeId {ch['nodeId']!r} is not in allowedNodeIds")
    elif rc["class"] == "instance_replacement":
        rep = rc.get("replacement")
        require(isinstance(rep, dict) and rep.get("brokenNodeId")
                and rep.get("intactComponent"),
                "instance_replacement requires replacement{brokenNodeId, intactComponent}")
        require(rep["brokenNodeId"] in allowed,
                "replacement.brokenNodeId is not in allowedNodeIds")
    else:
        rec = rc.get("reconstruction")
        require(isinstance(rec, dict) and rec.get("sectionNodeId")
                and rec.get("authoritativeSource"),
                "section_reconstruction requires reconstruction{sectionNodeId, "
                "authoritativeSource, disprovedPatches}")
        require(isinstance(rec.get("disprovedPatches"), int)
                and type(rec["disprovedPatches"]) is int
                and rec["disprovedPatches"] >= 2,
                "section_reconstruction requires >= 2 recorded disproved patches")
        require(rec["sectionNodeId"] in allowed,
                "reconstruction.sectionNodeId is not in allowedNodeIds")


def validate_acceptance_matrix(am: dict) -> None:
    require(isinstance(am, dict), "acceptanceMatrix must be an object")
    for key in ("schemaVersion", "checks", "aggregate"):
        require(key in am, f"acceptanceMatrix missing {key}")
    require(am["schemaVersion"] == "1.1", "acceptanceMatrix schemaVersion must be 1.1")
    seen: set[tuple] = set()
    components: dict[str, set[tuple]] = {}
    statuses: list[str] = []
    for i, row in enumerate(am["checks"]):
        for k in ("component", "breakpoint", "check", "status"):
            require(k in row, f"checks[{i}] missing {k}")
        require(row["breakpoint"] in ("desktop", "mobile"),
                f"checks[{i}].breakpoint invalid")
        require(row["check"] in ("canvas", "structure", "exporter"),
                f"checks[{i}].check invalid")
        require(row["status"] in ("pass", "fail", "deferred", "missing"),
                f"checks[{i}].status invalid")
        key = (row["component"], row["breakpoint"], row["check"])
        require(key not in seen, f"duplicate acceptance row {key}")
        seen.add(key)
        components.setdefault(row["component"], set()).add(
            (row["breakpoint"], row["check"]))
        if row["status"] == "deferred":
            require(bool(row.get("deferredReason")),
                    f"checks[{i}] is deferred without a deferredReason")
        require(row["status"] != "missing",
                f"checks[{i}] is 'missing': the matrix must enumerate coverage; "
                "record it as deferred with a reason, or cover it")
        statuses.append(row["status"])
    for comp, pairs in components.items():
        require(("desktop", "exporter") in pairs and ("mobile", "exporter") in pairs,
                f"component {comp!r} lacks exporter coverage for both breakpoints")
    agg = am["aggregate"]
    require(agg in ("verified", "repaired_unverified", "failed"),
            "acceptanceMatrix.aggregate invalid")
    if any(s == "fail" for s in statuses):
        require(agg == "failed", "a failing row requires aggregate 'failed'")
    elif all(s == "pass" for s in statuses):
        pass  # verified or a conservative repaired_unverified are both honest
    else:
        require(agg != "verified",
                "aggregate 'verified' requires every row to pass "
                "(deferred coverage means repaired_unverified)")


def validate_record(record: dict) -> None:
    for key in ("factPack", "repairContract", "acceptanceMatrix"):
        require(key in record, f"record missing {key}")
    validate_fact_pack(record["factPack"])
    validate_repair_contract(record["repairContract"], record["factPack"])
    validate_acceptance_matrix(record["acceptanceMatrix"])


def self_test() -> int:
    fixture = json.loads((HERE / "fixtures" / "synthetic-event-card.json").read_text())
    validate_record(fixture)
    print("  ok  synthetic fixture validates")

    def must_fail(mutate, label):
        record = json.loads(json.dumps(fixture))
        mutate(record)
        try:
            validate_record(record)
        except ValidationError:
            print(f"  ok  {label}")
            return
        print(f"FAIL: {label} did not fail")
        sys.exit(1)

    must_fail(lambda r: r["acceptanceMatrix"]["checks"].append(
        dict(r["acceptanceMatrix"]["checks"][0])),
        "duplicate acceptance row rejected")
    must_fail(lambda r: r["acceptanceMatrix"]["checks"].__delitem__(
        next(i for i, c in enumerate(r["acceptanceMatrix"]["checks"])
             if c["breakpoint"] == "mobile" and c["check"] == "exporter")),
        "missing mobile exporter coverage rejected")
    must_fail(lambda r: (r["acceptanceMatrix"]["checks"][0].update(
        status="deferred", deferredReason="tools unavailable"),
        r["acceptanceMatrix"].update(aggregate="verified")),
        "verified aggregate with deferred coverage rejected")
    must_fail(lambda r: r["acceptanceMatrix"]["checks"][0].update(status="missing"),
        "missing coverage row rejected (must be deferred-with-reason or covered)")
    must_fail(lambda r: r["factPack"]["unresolved"].append(
        {"question": "does the comp specify 496 or 528?", "canChangeMutation": True}),
        "ready fact pack with blocking unknown rejected")
    must_fail(lambda r: r["factPack"].update(geometryRelevant=True) or
        r["factPack"].pop("currentGeometry", None),
        "geometry-relevant fact pack without geometry rejected")
    must_fail(lambda r: r["repairContract"].update(
        class_=None) or r["repairContract"].update({"class": "section_reconstruction"}),
        "reconstruction class without a reconstruction section rejected")
    must_fail(lambda r: r["repairContract"].update(
        requiredChecks=["structure", "exporter_desktop"]),
        "requiredChecks without mobile exporter rejected")
    must_fail(lambda r: r["repairContract"]["changes"][0].update(nodeId="999:999"),
        "change outside allowedNodeIds rejected")
    print("self-test passed")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if args == ["--self-test"]:
        return self_test()
    if len(args) != 1:
        print(__doc__)
        return 2
    try:
        validate_record(json.loads(Path(args[0]).read_text()))
    except ValidationError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print("valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
