# Supervisor Restart Semantics — Quick Quiz

Use this after the reading and before or after the practical. Write short answers; no need for essay responses.

1. What are the two separate decisions OTP makes when a supervised child exits?

2. A child has `restart: :transient` and exits with `:normal`. Should it restart? Why?

3. A child has `restart: :transient` and exits with `:boom`. Should it restart? Why?

4. You have children in this order:

   ```elixir
   [:database, :cache, :web]
   ```

   Under `:rest_for_one`, which children restart if `:cache` crashes?

5. Same child order. Under `:rest_for_one`, which children restart if `:database` crashes?

6. When would `:one_for_all` be a better fit than `:one_for_one`?

7. Why can `:rest_for_one` be a good match for dependency chains?

8. What is the purpose of `max_restarts` / `max_seconds`?

9. In a child spec, why does `id` need to be unique among siblings?

10. Pick the best strategy:

    - independent cache workers
    - parser → validator → writer pipeline
    - three workers sharing one in-memory state snapshot that must reset together
