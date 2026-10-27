## Project

**Scenario:** A community health clinic needs a way for patients to check wait times before coming in. That's all you've been told.

### Deliverable 1: A Problem Brief (one page max)

#### Who are the users?

We can cluster the users in three categories:

1. **Patients** — need to know how long the wait will be.
2. **Staff** — update the wait time according to the number of patients in the queue.
3. **Admin** — has more fine-grained control over the system.

#### What do they actually need?

A way to plan their doctor's visit at a less crowded time, so that patient numbers are more evenly distributed and the waiting room is less crowded.

#### What does a great solution feel like to use?

Really fast, easily accessible, live and reliable.

#### What are the real constraints?

- **Budget:** low — it's a community clinic; it should be little work to build and maintain.
- **Technical skill:** low among staff → simple UI.
- **Patient access to devices:** old and young people; we expect everyone to have internet access.

### Deliverable 2: A Delegation Plan

> Map the build to the six toolkit capabilities. For each one, decide which AI collaboration mode fits best: **Automation** (AI does it, you check), **Augmentation** (you and AI work it together), or **Agency** (AI operates with latitude inside boundaries you set). Make a simple table — six rows, one per capability.

AI is strongest in the middle, weakest at the edges.

| Capability         | AI share  | Mode         | AI does                                                                             | We do                                                                               |
| ------------------ | --------- | ------------ | ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **Empathy**        | Low       | Augmentation | Sorts interview notes                                                               | Talk to patients and staff                                                          |
| **Design**         | Medium    | Augmentation | Generates product options                                                           | Decide what to build                                                                |
| **Architecture**   | High      | Augmentation | Proposes patterns                                                                   | Add our constraints, decide                                                         |
| **Implementation** | Very high | Agency       | Builds within spec and tests                                                        | Write spec and tests, review                                                        |
| **Judgment**       | Low       | Augmentation | Checks the code runs, clusters our experience reports, walks through it as personas | Test with real users, write experience reports, judge if it's good                  |
| **Shipping**       | Low       | Augmentation | Drafts release notes, analyses production feedback and metrics                      | Talk to users in production, understand their experience, decide the next iteration |

### Deliverable 3: Acceptance Tests

Write five to seven statements that define “done.” Each must be concrete enough that a stranger could tell you whether the finished product passes or fails.

- “A patient with a basic smartphone can find the current wait time in under 30 seconds without creating an account.”
- "A patient should rely on the times they should be accurate with a range +-15 min"
- "They should be accessible easily readable"
- "The Stuff should not spent more then 1 minute an hour to maintain the system"

### Lesson Reflection:

> If implementation became effectively free tomorrow, where would your value as a builder come from?
>
> - The Value as a builder comes primarly from the Edges of the Toolset, Empathy, Design and Judgment and Shipping. So Speak to people identify requirements, collect requirements, make decisions based on AI options, Collect feedback, Rank feedback Feel the experience.
