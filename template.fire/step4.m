Off[FrontEndObject::notavail];
FIREPATH = Environment["FIREPATH"];
THISDIR = Directory[];
SetDirectory[FIREPATH <> "/extra/LiteRed/Setup"];
Get["LiteRed.m"];
SetDirectory[FIREPATH];
Get["FIRE6.m"];
Internal = {{ {", ".join(str(m) for m in p.loop_momenta)} }};
External = {{ {", ".join(str(m) for m in p.external_momenta)} }};
Propagators = {{
#% for mom, m2 in p.denominators:
    ({mom})^2 - {m2},
#% pass
    Nothing
}} /. {p.replace_by_one} -> 1;
Replacements = {{
#% for p1, p2, v in p.scalar_product_rules:
    {p1}*{p2} -> {v},
#% pass
    Nothing
}} /. {p.replace_by_one} -> 1;
RESTRICTIONS = {{}};
LoadFireTables[filename_, coeff_: Identity, JoinTerms_: True] := Module[{{temp, GGG, data}},
    data = Get[filename];
    temp = {{GGG[##[[1]]], {{GGG[##[[1]]], ##[[2]]}} & /@ ##[[2]]}} & /@ data[[1]];
    Set[GGG[##[[1]]], G[##[[2, 1]], ##[[2, 2]]]] & /@ data[[2]];
    temp = temp;
    Clear[GGG];
    temp = DeleteCases[temp, {{a_, {{{{a_, "1"}}}}}}];
    temp = {{##[[1]], {{##[[1]], ToExpression[##[[2]]]}} & /@ ##[[2]]}} & /@ temp;
    temp = {{##[[1]], {{##[[1]], coeff[##[[2]]]}} & /@ ##[[2]]}} & /@ temp;
    If[JoinTerms,
        temp = {{##[[1]], Times @@@ ##[[2]]}} & /@ temp;
        temp = {{##[[1]], Plus @@ ##[[2]]}} & /@ temp;
    ];
    Rule @@@ temp // ReplaceAll[G[bid_, idx_List] :> B[bid, Sequence @@ idx]]
 ]
tables = LoadFireTables[THISDIR <> "/basisx.hint.tables"];
masters = tables[[;;,2]] // Cases[#, _B, -1]& // Union // ReplaceAll[B[bid_, idx__] :> {{bid, {{idx}}}}];
WriteRules[masters, THISDIR <> "/basisx"];
