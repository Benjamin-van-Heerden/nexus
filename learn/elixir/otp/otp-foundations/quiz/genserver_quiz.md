# GenServer and OTP Behaviours Quiz

## Instructions

Answer these questions without looking at the reading material. Write your answers in a separate file or on paper, then check your understanding.

---

## Questions

### 1. Core Concepts

**Q1.1:** What is the fundamental difference between a `call` and a `cast` in GenServer?

**Q1.2:** Why does the GenServer documentation recommend using `cast` "sparingly"? Name at least two reasons.

**Q1.3:** What does the `@impl true` attribute do? What benefit does it provide?

---

### 2. Return Values

**Q2.1:** Your `handle_call/3` callback needs to return a value to the caller and update state. What tuple do you return?

**Q2.2:** Your `handle_cast/2` callback updates state but has nothing to return to the caller. What tuple do you return?

**Q2.3:** You want to reply to a `call` later, not immediately. What tuple do you return from `handle_call/3` initially, and what function do you use later to send the reply?

---

### 3. When to Use What

**Q3.1:** You're building a simple counter that multiple processes increment. Would you use `Agent` or `GenServer`? Why?

**Q3.2:** You need to validate a user's input against a database and return true/false. `call` or `cast`?

**Q3.3:** You're sending metrics to an analytics service. You don't care if it succeeds, and you don't want to block the caller. `call` or `cast`?

**Q3.4:** You have a one-off async task: downloading a file. Should you use `GenServer` or `Task`?

---

### 4. Understanding the Flow

**Q4.1:** A message arrives at your GenServer process. It wasn't sent via `GenServer.call` or `GenServer.cast` — it was sent with raw `send(pid, :ping)`. Which callback handles it?

**Q4.2:** In `handle_call(request, from, state)`, what does the `from` argument contain? When would you use it?

**Q4.3:** What happens if your GenServer's mailbox fills up faster than it can process messages?

---

### 5. Code Reading

**Q5.1:** Look at this code. Is there a problem? If so, what?

```elixir
def handle_cast(:increment, state) do
  new_count = state.count + 1
  {:reply, new_count, %{state | count: new_count}}
end
```

**Q5.2:** This code compiles but has a bug. What's wrong?

```elixir
def handle_call(:get_user, _from, state) do
  user = fetch_user_from_db(state.user_id)
  {:noreply, state}
end
```

**Q5.3:** Fix this callback to properly use `@impl`:

```elixir
def init(initial_state) do
  {:ok, initial_state}
end
```

---

## Answer Key (Don't peek until you've answered!)

<details>
<summary>Click to reveal answers</summary>

### 1. Core Concepts

**A1.1:** `call` is synchronous — caller blocks waiting for a reply. `cast` is asynchronous — caller sends and continues immediately without waiting.

**A1.2:** (1) Casts are lost if the GenServer crashes — no delivery guarantee. (2) No backpressure — you can overwhelm the GenServer's mailbox. (3) Harder to debug because failures are silent.

**A1.3:** It marks the following function as implementing a behaviour callback. Benefits: compile-time warnings if signature is wrong, documents intent clearly.

### 2. Return Values

**A2.1:** `{:reply, value, new_state}`

**A2.2:** `{:noreply, new_state}` — casts cannot reply!

**A2.3:** Return `{:noreply, state}` initially, then use `GenServer.reply(from, response)` later.

### 3. When to Use What

**A3.1:** `Agent` — it's specifically designed for simple get/update state operations. Less boilerplate than GenServer.

**A3.2:** `call` — you need the result synchronously.

**A3.3:** `cast` — you don't need confirmation and want to avoid blocking.

**A3.4:** `Task` — one-off async work doesn't need a persistent process. Tasks are simpler and self-terminate.

### 4. Understanding the Flow

**A4.1:** `handle_info/2` — this handles all non-GenServer messages.

**A4.2:** `{pid, ref}` — the caller's PID and a unique reference. Use it when you want to reply later with `GenServer.reply/2`.

**A4.3:** The mailbox grows unbounded, consuming memory. Eventually the VM may kill the process or crash. This is why backpressure (using `call`) matters.

### 5. Code Reading

**A5.1:** `handle_cast` cannot return `{:reply, ...}`. Casts are asynchronous — there's no caller to reply to. Should be `{:noreply, new_state}`.

**A5.2:** The function fetches the user but never returns it! Should be `{:reply, user, state}` not `{:noreply, state}`.

**A5.3:**
```elixir
@impl true
def init(initial_state) do
  {:ok, initial_state}
end
```

</details>
