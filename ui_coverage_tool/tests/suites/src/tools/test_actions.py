from ui_coverage_tool.src.tools.actions import ActionType


# -------------------------------
# TEST: ActionType.to_list()
# -------------------------------


def test_action_type_to_list_contains_all_members() -> None:
    members = ActionType.to_list()

    assert isinstance(members, list)
    assert all(isinstance(m, ActionType) for m in members)
    assert set(members) == set(ActionType)
    assert len(members) == len(ActionType)
