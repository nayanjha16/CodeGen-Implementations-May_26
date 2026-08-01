from src.demo_showcases import showcase_examples


def test_showcases_cover_all_tasks_and_have_unique_ids():
    examples = showcase_examples()
    assert {row["task_id"] for row in examples} == {
        "T1",
        "T2",
        "T3",
        "T4",
        "T5",
        "T6",
    }
    ids = [row["showcase_id"] for row in examples]
    assert len(ids) == len(set(ids))
    assert all(row["input_text"].strip() for row in examples)


def test_showcase_copy_is_defensive():
    first = showcase_examples()
    first[0]["title"] = "changed"
    assert showcase_examples()[0]["title"] != "changed"
