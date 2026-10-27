# Description

> Four steps towards a good Description
>
> 1. User Voice
>
> - what a real person Actually say (i wanna see wait times before going ...)
> - Notice tone, emotion, and context not said out loud
> - Use empathy to connect and define the real user need (whats been unsaid)
> - User voice is raw and not yet buildable
>
> 2. Product Requirement
>
> - Take a Raw user need and scope into measurable requirements (Patients can view estimated wait times, mobile friendly)
> - Make decisions based on judgement and what you learn in your empathy work
> - Ensure clear concrete criteria to guide AI
>
> 3. Technical Spec
>
> - Clear instructions on what and how to build (web app that pulls clinic api for wait data ...)
> - The more specific the Better
> - Assumptions like which stack to use and how to handle errors need to be called out for AI
>
> 4. AI instruction
>
> - Specific, contextualized instructions
> - clearly define edge cases
> - define all assumptions as which stack to use
> - tests and success checkpoints that must be passed

> Builder who carefully describe all aspects of the problem, get better results

## Identify Failure

One main rule will be to understand why description failed.
A big role would be todo this forensic

> Description Failure
>
> - User Voice, never really heard or had enough empathy to really understand what they need
> - Product requirement, where you heard them but scoped it wrong
> - Technical spec, requiremnt was right but technical spec lost something
> - Ai instruction, Prompt failure, everything upstream was solid but we instruct ai poorly

_`Tests` are the most precise form of description. A passing test with an unhappy user means you described the wrong intent._
