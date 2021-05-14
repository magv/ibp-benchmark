Off[FrontEndObject::notavail];
FIREPATH = Environment["FIREPATH"];
THISDIR = Directory[];
SetDirectory[FIREPATH <> "/extra/LiteRed/Setup"];
Get["LiteRed.m"];
SetDirectory[FIREPATH];
Get["FIRE6.m"];
Internal = {l};
External = {p1, p2, p3};
Propagators = {
    (l)^2 - m2,
    (l + p2)^2 - m2,
    (l - p1 - p3)^2 - m2,
    (l - p1)^2 - m2
};
Replacements = {
    p1^2 -> 0,
    p2^2 -> 0,
    p3^2 -> 0,
    p1*p2 -> s12/2,
    p1*p3 -> (-s12 - s23)/2,
    p2*p3 -> s23/2
};
RESTRICTIONS = {};
CreateNewBasis[basisx, Directory->(THISDIR <> "/basisx.litered")];
GenerateIBP[basisx];
Print["* AnalyzeSectors[]"];
AnalyzeSectors[basisx, {_, _, _, _}];
Print["* FindSymmetries[]"];
FindSymmetries[basisx];
Print["* DiskSave[]"];
DiskSave[basisx];
Print["* Done"];
