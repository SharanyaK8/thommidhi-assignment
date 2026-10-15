# Part 2: An Open Question

### What I understood and assumed

I read “ee title better aa, leka second one?” as “Is this title better, or the second one?” The question has no titles in it, so I assume the creator also provides both titles, perhaps through two input boxes. “Better” is also unclear. I assume it means which title is more likely to attract clicks, unless the creator says otherwise. I checked the meaning of the Telugu words online and read the sentence this way. I am fairly sure about it, but I would still ask a native Telugu speaker to confirm, because online meanings can miss how people actually talk. I am less sure about what “better” means here, so the system should ask for clarification when necessary.

### Design

I would keep the first version simple, with one model call. The backend checks that both titles are provided, sends the original Telugu-English question and titles to a model that understands code-mixed language, and requests a short answer with the preferred title and one or two reasons. The backend then checks the response format before returning the answer in a similar language style to the creator.

I would not add translation or multiple model calls at the beginning because they can increase latency and cost. I would add another step only if testing showed that it improved answer quality enough to justify the extra cost.

### Time and cost

For the three-second target, I would initially budget around 0.5 seconds for the network and backend, up to about two seconds for the model, and keep the remaining time as a buffer. These are starting estimates, not guarantees, so I would measure actual end-to-end response times, including the 95th-percentile latency.

I would keep prompts and answers short and use a simple fallback if the response is taking too long. Streaming could make the answer appear sooner, but I would still measure how long the complete response takes.

For the ₹0.10 cost limit, I would calculate the input-token and output-token costs using the chosen model's current prices. I would also include validation, retries, and any additional processing. I would test the actual cost per question and aim comfortably below the limit.

### Trade-offs

A smaller model may be faster and cheaper but may misunderstand informal Telugu or spelling variations. A larger model may understand them better but cost more and take longer. I would test a few models using the same questions and choose the least expensive one that meets the quality, latency, and cost requirements.

Short answers are faster and cheaper but provide less detail, so I would give additional explanations only when requested.

### What I would test first

I would create around 30–50 sample questions written in the way real creators type, including different spellings, Telugu written in English letters, missing titles, unclear references such as “the second one,” and questions where the answer depends on the audience.

I would check whether the system understands the question, asks for clarification when necessary, compares only the provided titles, avoids unsupported claims, and meets the response-time and cost targets. I would review the results manually before deciding which model to use.

### When the system is not sure

It should not guess just to respond quickly. If the titles are missing, it should ask for them. If the question is unclear, it should ask a short question, such as “Do you mean which title may get more clicks, or which one is clearer?”

If the question is understood but there is not enough information to confidently choose a title, the system should explain the uncertainty and give a cautious, reasoned opinion rather than inventing a click percentage. I would not trust the model's own confidence statement by itself. I would compare its answers with labelled test examples to understand where it performs well and where it needs to ask for clarification.

The goal is not just to answer quickly. It is to provide a useful answer while staying within the time and cost limits and being honest about uncertainty.