# Why I Built Knowledge Compiler

I built Knowledge Compiler around a problem that I kept noticing: understanding an unfamiliar codebase can take a ridiculous amount of time before you can even start making meaningful changes.

I know people who already work in the software industry, and I've helped some of them along the way. Seeing the challenges they face has shown me how much effort can go into understanding an existing system. You enter a repository with its own architecture, dependencies, configuration, tests, undocumented assumptions, and years of implementation decisions. Before you can confidently change anything, you need to figure out how the pieces fit together.

The documentation might be outdated. The README might describe behavior that no longer exists. Tests might reveal things nobody documented. Important assumptions might be buried inside functions or scattered across multiple services.

You end up searching, reading, comparing, and building a mental model of the system from fragments.

And even after finding an answer, you still need to know why that answer is correct and where the evidence came from.

That got me thinking:

**What if a tool could show you not just what it thinks a codebase does, but also the evidence behind that conclusion?**

That question became the starting point for Knowledge Compiler.

## The Problem Is Bigger Than Reading Code

Reading code is only one part of understanding software.

The harder part is figuring out what the code actually establishes.

- What does this system do?
- Which behaviors are explicitly implemented?
- What do the tests tell us?
- Which dependencies and configuration files matter?
- Does the documentation agree with the implementation?
- What can we confidently conclude from the available evidence?
- What are we still guessing about?
- Where should we look to verify a conclusion?

A summary can describe a repository without answering these questions. An AI model can produce an explanation that sounds convincing without establishing that the explanation is correct.

For engineering work, plausibility is not enough.

I wanted to explore a different approach: a system that represents conclusions alongside the evidence that supports or contradicts them.

## Show Me What This Codebase Knows About Itself

That became the central idea behind Knowledge Compiler:

**Show me what this codebase knows about itself.**

The compiler inspects a repository, extracts evidence, generates structured claims, and connects those claims to the available source material.

Instead of treating every conclusion as equally certain, it distinguishes between findings established by deterministic checks, observations supported by evidence, claims contradicted by evidence, and questions that remain unresolved.

The objective isn't to pretend that a tool can understand every line of every codebase perfectly.

It's to make its conclusions inspectable.

If the compiler claims that a repository contains automated tests, I want the user to be able to inspect the evidence behind that statement. If an AI-generated observation cannot be established from the available sources, the system should preserve that uncertainty rather than turn a guess into a fact.

I want engineers to be able to ask not only *What did you find?* but also *Why should I believe you?*

## Why Not Build Another Codebase Summarizer?

There are already tools that summarize files, explain functions, generate documentation, and answer questions about source code.

Those capabilities are useful. But a generated explanation and an evidence-backed engineering claim are not the same thing.

Knowledge Compiler focuses on a different set of principles:

- Claims should be traceable to source evidence.
- Different kinds of evidence should remain distinguishable.
- Contradictory evidence should not be silently ignored.
- Uncertainty should be visible.
- AI-generated observations should not automatically become facts.
- The core analysis should remain useful without a language model.

I don't see summaries or conversational interfaces as useless. They can be valuable ways to explore what a system discovers.

But I believe they become more useful when the underlying conclusions can be inspected, challenged, and traced back to their sources.

## Why a Deterministic Core?

I didn't want Knowledge Compiler to become useless whenever a language model was unavailable, too slow, or too expensive to run.

That's why deterministic analysis comes first.

The compiler can discover files, extract repository content, identify supported structures, and generate baseline claims without requiring an AI model.

Optional AI investigation can examine selected parts of a codebase and propose additional observations. Those observations are then evaluated against independently extracted evidence.

This separation matters.

Someone using a CPU-only machine should still be able to use the core analysis workflow. Someone with a capable GPU may be able to run local AI investigation with lower inference latency, depending on the hardware and model.

The deterministic pipeline shouldn't depend on how powerful someone's machine is.

AI is an additional investigation capability, not a prerequisite for the project to be useful.

## Why Local AI?

I wanted to explore meaningful language-model integration without making a paid hosted API a requirement.

Ollama provides a practical way to run a model locally. Knowledge Compiler can supply selected repository material to the model, collect its observations, and evaluate those observations against extracted evidence.

Of course, local models have limitations. They can misunderstand code, miss relevant context, and generate incorrect observations even when their answers sound confident. They can also be slow on CPU-only hardware.

In my own CPU-only testing, one AI investigation unit has taken approximately 2–3 minutes. At that rate, 100 units processed sequentially would take roughly 3 hours 20 minutes to 5 hours. That's an observed estimate on one setup, not a universal benchmark. A capable GPU may reduce inference time substantially, but no particular speedup is guaranteed.

These trade-offs are part of the engineering problem.

The interesting question isn't simply whether an AI model can explain a repository. It's how to incorporate model-generated observations into a system that distinguishes evidence-backed findings from unresolved hypotheses.

That's the problem I wanted to work on.

## Why Call It a Compiler?

A traditional compiler transforms one representation into another through a sequence of defined stages.

Knowledge Compiler applies a similar idea to repository-derived knowledge.

It takes a software repository as input and moves through discovery, evidence extraction, optional investigation, validation, and claim generation.

The output is a structured representation of what the analysis can establish about the repository.

The name doesn't mean that the system has solved software understanding. It describes the approach: transforming raw repository material into structured knowledge through explicit, testable stages.

I want the pipeline to remain understandable and extensible rather than hiding the entire process inside one enormous AI prompt.

## Why Build the Entire Application?

I could have stopped at a Python script that scans a repository and prints some results.

Instead, I wanted to build the surrounding engineering system too.

Knowledge Compiler includes a FastAPI backend, background processing, Redis, BullMQ, MySQL, a Next.js frontend, Docker Compose, and GitHub Actions.

That introduces problems beyond the compiler itself:

- How do you run long analyses without blocking an API request?
- How do you track job state and report progress?
- How do you persist claims and evidence?
- How do you represent relationships between them?
- How do you handle failures across multiple services?
- How do you test that the complete system works, not just individual functions?

Building the infrastructure forces me to deal with these questions instead of creating something that works only as a standalone script.

I'm also learning through the process. I didn't build this because I already knew every technology involved. I built it because I wanted to understand the problem deeply enough to design, implement, test, and connect the pieces myself.

The infrastructure matters, but it isn't the point. Every component should ultimately support the central objective: helping engineers investigate unfamiliar software more effectively.

## What Building It Has Taught Me

One of the biggest lessons has been that adding AI doesn't automatically make a system intelligent.

A model can generate an impressive explanation. The harder work is supplying relevant context, checking the result, representing uncertainty, and making the outcome useful to another engineer.

I've also learned that structured output doesn't automatically mean structured knowledge. A JSON object can contain claims and evidence IDs without guaranteeing that the evidence actually supports the claim.

The relationships between those objects matter. So do the rules that assign claim statuses, the limitations of the extraction process, and the ability to inspect the underlying source.

Building the complete application has also exposed me to the realities of backend development, background jobs, databases, frontend state, API contracts, containerization, and integration testing.

Those challenges are part of building the product, not distractions from it.

They have also taught me to be careful about what I claim the system can do. A feature that works in one tested scenario isn't automatically a general solution to the entire problem.

## What Knowledge Compiler Doesn't Claim to Be

Knowledge Compiler is an evolving engineering project.

Its structural analysis is primarily implemented for Python, even though file discovery recognizes additional languages. Its deterministic claims cover a limited set of repository properties. AI investigation examines selected units rather than exhaustively understanding every possible execution path.

Evidence-based validation is not formal verification, and in the current implementation the check is performed by the same local model that proposed the observations, so it can be wrong too. Confidence scores are heuristic values, not calibrated probabilities. A claim marked as verified reflects the compiler's implemented checks, not a mathematical proof of every possible interpretation.

I would rather be clear about these limitations than pretend that a system understands arbitrary codebases simply because it can produce convincing output.

The goal is to keep improving the system while making the boundaries of its current behavior visible.

## Where I Want to Take It

The long-term goal is to make the initial investigation of an unfamiliar production codebase substantially faster.

I want an engineer to be able to point Knowledge Compiler at a repository and get a useful, inspectable starting point:

- What the repository contains.
- Which behaviors have evidence behind them.
- Which tests and configuration files matter.
- Which conclusions are supported or contradicted.
- Which questions remain unanswered.
- Where to investigate next.

The aim is to reduce the time spent manually assembling an initial mental model of a system, so engineers can spend more time investigating meaningful problems and less time searching blindly.

It won't eliminate the need to read code, run tests, debug behavior, or exercise engineering judgment. It should help people approach those tasks with a better starting point.

I'm building Knowledge Compiler to explore that idea seriously: not as another tool that confidently generates explanations, but as an engineering system that makes its reasoning and evidence easier to inspect.

**Don't tell me what you think. Show me why you think it.**