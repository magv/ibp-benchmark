(* This script compares two IBP tables.
 *)

If[Not[MatchQ[$ScriptCommandLine, {_String, _String}]],
  Print["Usage: math -script compare-ibp-tables.m -- table1.m table2.m"];
  Exit[1];
];

{filename1, filename2} = $ScriptCommandLine;

Print["Table 1 is '", filename1, "'"];
table1 = Get[filename1] /. B[1,idx__] :> basis[idx] // Association;
masters1 = table1 // Values // Cases[#, _basis, {0, Infinity}]& // Union;
Print["Table 1 has ", masters1 // Length, " masters, ", table1 // Length, " rules"];

Print["Table 2: ", filename2];
table2 = Get[filename2] /. B[1,idx__] :> basis[idx];
masters2 = table2 // Values // Cases[#, _basis, {0, Infinity}]& // Union;
Print["Table 2 has ", masters2 // Length, " masters, ", table2 // Length, " rules"];

Print["Masters #1: ", masters1 // Length];
masters1 // MapIndexed[Print[#2//First, ") ", #1]&];

Print["Masters #2: ", masters2 // Length];
masters2 // MapIndexed[Print[#2//First, ") ", #1]&];

(* Return True if a rational expression is probably zero, and
 * False if it is definitely not zero.
 *)
ProbablyZeroQ[ex_] := Module[{vars, map},
  vars = Cases[ex, _Symbol, {0, Infinity}] // Union;
  Quiet[
    AllTrue[Range[10], (
      map = vars // Map[# -> RandomInteger[{10, 10000}]&] // Association;
      Check[Together[ex /. map] === 0, True, {Power::infy, Infinity::indet}]
    )&]
    ,
    {Power::infy, Infinity::indet}]
]

integrals = Join[table1 // Keys, table2 // Keys, masters1, masters2] // Union;
Do[
  integral = integrals[[idx]];
  Print[idx, ") ", integral];
  ex1 = integral /. table1;
  ex2 = integral /. table2 /. table1;
  If[Not[MemberQ[table1 // Keys, integral] || MemberQ[masters1, integral]],
    Print["Integral ", integral, " is missing from table 1"];
    Exit[1];
  ];
  If[Not[MemberQ[table2 // Keys, integral] || MemberQ[masters2, integral]],
    Print["Integral ", integral, " is missing from table 2"];
    Exit[1];
  ];
  diff = Collect[ex1 - ex2, _basis, If[ProbablyZeroQ[#],0,Coeff[#]]&];
  If[diff =!= 0,
    Print["Mismatch in ", integral];
    Print["Difference between table1 and table2:"];
    Print[diff];
    Exit[1];
  ];
  ,
  {idx, Length[integrals]}]
