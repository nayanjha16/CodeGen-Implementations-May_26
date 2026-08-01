graph TD;
**start**([<p>__start__</p>]):::first
router(router)
supervisor(supervisor)
translation(translation)
generation(generation)
compiler(compiler)
repair(repair)
explanation(explanation)
**end**([<p>__end__</p>]):::last
**start** --> router;
compiler -. &nbsp;success&nbsp; .-> explanation;
compiler -.-> repair;
generation --> compiler;
repair --> compiler;
router --> supervisor;
supervisor -. &nbsp;end&nbsp; .-> **end**;
supervisor -.-> explanation;
supervisor -.-> generation;
supervisor -.-> translation;
translation --> compiler;
explanation --> **end**;
classDef default fill:#f2f0ff,line-height:1.2
classDef first fill-opacity:0
classDef last fill:#bfb6fc
