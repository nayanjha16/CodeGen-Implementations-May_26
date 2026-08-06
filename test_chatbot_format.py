from agent.repo_migrate_chat import _append_user, _append_bot
history = []
_append_user(history, "hello")
_append_bot(history, "world")
print(history)
