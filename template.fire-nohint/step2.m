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
CreateNewBasis[basisx, Directory->(THISDIR <> "/basisx.litered")];
GenerateIBP[basisx];
Print["* AnalyzeSectors[]"];
AnalyzeSectors[basisx, {{ {", ".join("_" if s else "0" for s in p.top_sector)} }}];
Print["* FindSymmetries[]"];
FindSymmetries[basisx];
Print["* DiskSave[]"];
DiskSave[basisx];
Print["* Done"];
