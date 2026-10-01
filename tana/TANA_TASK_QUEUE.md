# Build: Fix Tana's tasks, then add a Task Queue

For Claude Code on the Tana PC. Project: `C:\Users\Owner\Documents\Tana Companion`
(Electron + TypeScript; main process in `src/main`, renderer in `src/renderer`, Tana Brain
served locally at http://127.0.0.1:5192, node at `.tools/node22/node.exe`).
Make a git backup bundle before changing anything. Do Part 1 completely before Part 2.

---

## Part 1: Find out why Tana isn't doing the tasks I post in chat

Problem: when I post a task in the Tana Brain chat, Tana doesn't carry it out. Find the
root cause before changing any code. Check each step below in order and note what you find.

1. **Reproduce it.** Start Tana (`app-shell\Tana\Tana.exe` or the dev command) the way I
   normally run it, and open the chat at http://127.0.0.1:5192.
   Post a simple test task in the chat, for example "Create a file called task-test.txt
   that says hello". Watch the server logs, the worker logs and the browser console while
   you do it.
2. **Is the message saved?** Confirm the chat message reaches the backend and gets stored
   (database row, file, queue entry, whatever the app uses). If it never arrives, the bug
   is in the chat UI or API route.
3. **Is it recognised as a task?** Find the code that decides whether a chat message is a
   task or just conversation (keywords, a classifier, a `/task` prefix, a tool call, a
   flag). Check whether my test message passes that check. Look for wording it expects that
   I don't use.
4. **Is anything picking it up?** Find the process that executes tasks (worker, cron job,
   polling loop, webhook, background job, scheduled Claude session). Check that:
   - it is actually running, and starts when the PC or Tana restarts;
   - it reads from the same place the chat writes to (same database, table, folder, queue
     name, user ID);
   - its status filter matches, e.g. it looks for `pending` but chat saves `new`;
   - it doesn't crash or skip silently. Look for swallowed errors and empty `catch` blocks.
5. **Can it actually run the task?** Check API keys, environment variables, model name,
   permissions, rate limits, expired tokens and file paths. Run one task by hand through
   the same code path and read the full error.
6. **Does the result come back?** Confirm the result and a status update (done or failed)
   are posted back into the chat so I can see them.

**Fix:** fix the root cause you found, not just the symptom. Make failures visible: if a
task fails, Tana must post the error in the chat instead of saying nothing. Then post 3
different test tasks in chat and confirm all 3 run and report back. Write a short summary
of what was wrong and what you changed into `TASK_FIX_NOTES.md`, then commit.

---

## Part 2: Task Queue (only after Part 1 works)

Give Tana and Tana Brain one ordered task queue. Tana works through it top to bottom, and I
can re-order it whenever I want.

### 2.1 Data
- Store the queue in the app's existing database, or `tasks/queue.json` in Tana's user data
  folder (`%APPDATA%\tana-companion`) if there is none. Each task has: `id`, `title`, `details`, `position` (order number), `status`
  (`queued`, `in_progress`, `done`, `failed`, `paused`), `created_at`, `updated_at`,
  `result` and `error`.
- Every task posted in chat (from Part 1) is added to the **bottom** of the queue
  automatically.
- Add IPC handlers / local API routes (match how chat already talks to the main process) to
  list, add, edit, delete, re-order (send the full list of IDs in the new order),
  pause/resume and retry tasks. Keep them local-only / behind the existing login.

### 2.2 How Tana uses the queue
- Tana always takes the `queued` task with the lowest `position`, sets it to
  `in_progress`, does it, then sets it to `done` (with the result) or `failed` (with the
  error), and moves on to the next one. One task at a time unless I say otherwise.
- Before starting each task, Tana re-reads the queue so any re-ordering I did is respected.
- Paused tasks are skipped until I resume them.
- Add the queue rules to Tana's system prompt / instructions file (and to `CLAUDE.md` if
  Tana runs through Claude Code), including the queue's location and API, so Tana always
  knows how to read it. Also add a tool or command Tana can call to read the queue, so
  when I ask "what's next?" or "what's in your queue?" it answers from the live list.
- Post a short chat message whenever a task starts, finishes or fails.

### 2.3 Task Queue button and pop-up (desktop chat)
- In the Tana chat on desktop, add a **Task Queue** button in the chat header/toolbar,
  next to the other chat buttons, with a badge showing how many tasks are queued.
- Clicking it opens a pop-up window (modal) over the chat that shows the list in order:
  number, title, status badge, and the current task highlighted at the top.
- In the pop-up I can:
  - **drag and drop** tasks to re-order them, plus up/down arrow buttons as a backup;
  - add a task, edit a task's title/details, delete a task;
  - pause/resume a task, and retry a failed one;
  - show or hide finished tasks.
- Changes save right away and update live (poll every few seconds or use the existing
  websocket), so the order I set is the order Tana uses on its next pick.
- Add the same pop-up as a **Task Queue** page in Tana Brain's navigation, so I can also
  open it outside the chat (and on phone).

### 2.4 Check it
- Add 3 tasks in chat. Open the Task Queue pop-up and confirm all 3 are there in order.
- Drag the 3rd task to the top. Confirm Tana does that one next.
- Pause one task and confirm Tana skips it; resume it and confirm it runs.
- Ask Tana in chat "what's in your queue?" and confirm it reads the live list correctly.
- Restart Tana and confirm the queue and its order are still there.
- Commit when everything works.
