---
title: nexus-self-interaction-model
created_at: '2026-04-07T11:07:53.733757'
updated_at: '2026-04-07T11:07:53.733757'
---
Nexus self runs once daily in the morning — reports progress, gives motivation, scolds/warns if needed. Throughout the day, the user reports activities ('I exercised', 'I read chapter X'). The agent logs these appropriately. For reading specifically: the agent must NOT just ask vague questions. It should research the book/chapter, provide a recap with quotes/excerpts/context, then engage a QA loop to 1) crystallize knowledge, 2) test comprehension, 3) glean what the user took from the reading. Format: 'Ok let's recap, in chapter X the following happens... what did you think about Y?' — then a short back-and-forth on mainstream interpretation vs the user's own take. Only after this exchange does it log the reading session. The system must handle backdated entries — e.g. 'Yesterday I did XYZ' should log with yesterday's date, not today's.