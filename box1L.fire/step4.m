LoadFireTables[filename_, coeff_: Identity, JoinTerms_: True] := Module[{temp, GGG, data},
    data = Get[filename];
    temp = {GGG[##[[1]]], {GGG[##[[1]]], ##[[2]]} & /@ ##[[2]]} & /@ data[[1]];
    Set[GGG[##[[1]]], G[##[[2, 1]], ##[[2, 2]]]] & /@ data[[2]];
    temp = temp;
    Clear[GGG];
    temp = DeleteCases[temp, {a_, {{a_, "1"}}}];
    temp = {##[[1]], {##[[1]], ToExpression[##[[2]]]} & /@ ##[[2]]} & /@ temp;
    temp = {##[[1]], {##[[1]], coeff[##[[2]]]} & /@ ##[[2]]} & /@ temp;
    If[JoinTerms,
        temp = {##[[1]], Times @@@ ##[[2]]} & /@ temp;
        temp = {##[[1]], Plus @@ ##[[2]]} & /@ temp;
    ];
    Rule @@@ temp // ReplaceAll[G[bid_, idx_List] :> B[bid, Sequence @@ idx]]
 ]

Put[LoadFireTables["basisx.tables"], "basisx.ibp-tables.m"];
