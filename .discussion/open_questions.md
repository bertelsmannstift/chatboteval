# Open Questions for Design Phase

## Stack 
- Argilla vs Cutoms (Fast API & HTMX)

## ANNOTATOR UI
- interface in English / German? lang is primarily Eng: HB to find out
- number of reviewers?
- do we want to deliver in-app guidance to reviewers or just an initial guidance doc? Depends how varied & expert the reviewers are
- do we have anyone on BF side who might be able to ajudicate over disagreement? 
- do we want quality control - e.g. gld-standard questions mixed into batches to monitor annotator accuracy?
-simple annotator ID, or proper auth (SSO, OAuth, etc)?
 
## INPUT DATA RICHNESS
[Once we have the credentials setup I can start querying the bot automatically as we have the repo access]
- What format will query-response pairs arrive in?
- do we know if we will get meta-data / ground truths (chunks or fiull docs?) etc? 
-  what domain inputs are available? topic index, publication corpus ToC, use case list
-  reasoning traces?
 
## SYNTHETIC DATA GEN
- can synthetic data generation pipeline be a sparate tool? or part of the same pipeline? it's a big piece of work, and if we are focused on open sourcing it in future, it might be neater to provide this as a parallel tool (in same repo) for data-scarce/sensitive cases, rather than as part of same tool 
- will any organic data be available?
 
## DOWNSTREAM OUTPUTS / MODULARITY
- tradeoff: one pipeline vs modular components
- report generation model? metrics / dashboard?
- for the report/brief: will we want to the tool to generate elements of this  (i.e . chatboteval produces summary tables, plots, diagnostics automatically) or just produced raw data and we write a separat narrative report?
- presumably we want to uncouple (but be able to link) the eval from the downstream training as two separate processes/pipelines
- overall pipeline(?): synthetic data gen [creates dataset] > eval [raw data] > (i) an analysis module [produces analysis plots etc] / training [of downstream module] 
- presumably we would want to use all instances as both evaluating model and training the downstream models? More data efficient. Or 2 separate modes (2 diff pipelines: eval vs training)?