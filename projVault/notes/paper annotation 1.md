interesting points:

would we want to test entire minesweeper fields, or isolated specific problems?
- ultimately, the statistic would measure general minesweeper fields, so there's no sense in evaluating isolated problems.
- there's also no simple way to merge sub-problems in minesweeper without altering the difficulty, so that might need to become a chunk of the project
^ actually.. there's no need to split levels into sub-problems, because our telemetry would tell us what part of the board the user is stuck on.
to take advantage of that.. our experiment platform SHOULDNT show the user the whole field.. but only a **reduced view**. potentially with a **minimap** view for the whole field as a supplement.
- on that note.. we dont however want the **sub-view+minimap** to be *unnecessary*, so we should make the **field big enough** to *necessitate it*. HOWEVER, **not too big** to take 10+ minutes to solve the average field.
	  - also need to consider **mine count**. we could only consider a single count, but *anecdotal evidence suggests mine count heavily influences **difficulty*** and is important.

when we run our own experiment.. we should ask
- difficulty scale: easy ...challenging... hard
- fun scale: boring...engaging

![[paper annotation 1 2025-09-25 12.21.57.excalidraw|9999]]