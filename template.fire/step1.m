Off[FrontEndObject::notavail];
FIREPATH = Environment["FIREPATH"];
THISDIR = Directory[];
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
Print["* PrepareIBP[]"];
PrepareIBP[];
Print["* Prepare[]"];
Prepare[AutoDetectRestrictions->False];
Print["* SaveStart[]"];
SaveStart[THISDIR <> "/basisx"];
Print["* Done"];
