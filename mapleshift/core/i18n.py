"""
Preset translations. Numbers, codes and names are NEVER translated:
they are dropped into the {placeholders} after translation.

French: official language. Punjabi and Mandarin: machine-assisted drafts.
Before a real launch, a native speaker should review every string.
"""

LANGS = {
    "en": "English",
    "fr": "Français",
    "pa": "ਪੰਜਾਬੀ",
    "zh": "中文",
}

T = {
    "en": {
        "report_title": "Claim pack for your broker",
        "invoice_total": "Invoice total",
        "confirmed_extra": "Extra cost from counter-tariffs",
        "possible_extra": "Possible extra cost (needs checking)",
        "items_affected": "Items affected",
        "of_invoice": "{pct}% of this invoice",
        "item": "Item", "code": "Tariff item", "made_in": "Made in", "rate": "Rate",
        "value": "Value (CAD)", "extra": "Extra cost", "confidence": "How sure",
        "Verified": "Verified", "Estimated": "Estimated", "Needs review": "Needs review",
        "affected": "Affected", "at_risk": "Check needed", "not_affected": "Not affected",
        "checklist": "What to do next",
        "proof_of_origin": "Ask {supplier} for proof of where {n} item(s) were made.",
        "compare_suppliers": "Get quotes from non-US suppliers for your most expensive items.",
        "confirm_origin": "Find out where these items were made. The surtax only applies to goods made in the US.",
        "broker_review": "Ask a customs broker to confirm the tariff code for these items.",
        "review_prices": "Review your prices: counter-tariffs add {amount} ({pct}% of this invoice).",
        "remission": "If you cannot switch suppliers, ask a broker about Canada's tariff remission framework.",
        "support_programs": "Check government support, such as the Regional Tariff Response Initiative and BDC programs.",
        "in_transit": "Goods already on their way to Canada on September 8, 2026 may not be subject to the surtax. Ask your broker.",
        "sources": "Sources",
        "disclaimer": "This is an estimate, not legal or customs advice. Always confirm with a licensed customs broker.",
        "mt_note": "",
        "rate_note": "Rates from {list}. USD converted at {fx} ({fx_note}). Excludes regular duty, GST, freight and brokerage.",
        "print": "Print or save as PDF",
    },
    "fr": {
        "report_title": "Dossier de réclamation pour votre courtier",
        "invoice_total": "Total de la facture",
        "confirmed_extra": "Coût supplémentaire des contre-tarifs",
        "possible_extra": "Coût supplémentaire possible (à vérifier)",
        "items_affected": "Articles touchés",
        "of_invoice": "{pct} % de cette facture",
        "item": "Article", "code": "Numéro tarifaire", "made_in": "Fabriqué en", "rate": "Taux",
        "value": "Valeur (CAD)", "extra": "Coût supplémentaire", "confidence": "Fiabilité",
        "Verified": "Vérifié", "Estimated": "Estimé", "Needs review": "À vérifier",
        "affected": "Touché", "at_risk": "À vérifier", "not_affected": "Non touché",
        "checklist": "Prochaines étapes",
        "proof_of_origin": "Demandez à {supplier} une preuve de l'origine de {n} article(s).",
        "compare_suppliers": "Demandez des soumissions à des fournisseurs hors des États-Unis pour vos articles les plus coûteux.",
        "confirm_origin": "Vérifiez où ces articles ont été fabriqués. La surtaxe ne s'applique qu'aux produits fabriqués aux États-Unis.",
        "broker_review": "Demandez à un courtier en douane de confirmer le numéro tarifaire de ces articles.",
        "review_prices": "Révisez vos prix : les contre-tarifs ajoutent {amount} ({pct} % de cette facture).",
        "remission": "Si vous ne pouvez pas changer de fournisseur, renseignez-vous auprès d'un courtier sur le cadre de remise des droits du Canada.",
        "support_programs": "Consultez les mesures de soutien, comme l'Initiative régionale de réponse aux tarifs et les programmes de BDC.",
        "in_transit": "Les marchandises déjà en route vers le Canada le 8 septembre 2026 pourraient ne pas être visées par la surtaxe. Consultez votre courtier.",
        "sources": "Sources",
        "disclaimer": "Ceci est une estimation et non un avis juridique ou douanier. Confirmez toujours auprès d'un courtier en douane agréé.",
        "mt_note": "Traduction automatique révisée. Les termes officiels restent en anglais ou en français.",
        "rate_note": "Taux tirés de : {list}. USD converti à {fx} ({fx_note}). N'inclut pas les droits ordinaires, la TPS, le transport ni le courtage.",
        "print": "Imprimer ou enregistrer en PDF",
    },
    "pa": {
        "report_title": "ਟੈਰਿਫ਼ ਪ੍ਰਭਾਵ ਰਿਪੋਰਟ",
        "invoice_total": "ਇਨਵੌਇਸ ਦਾ ਕੁੱਲ",
        "confirmed_extra": "ਜਵਾਬੀ ਟੈਰਿਫ਼ਾਂ ਕਾਰਨ ਵਾਧੂ ਖ਼ਰਚਾ",
        "possible_extra": "ਸੰਭਾਵੀ ਵਾਧੂ ਖ਼ਰਚਾ (ਜਾਂਚ ਲੋੜੀਂਦੀ)",
        "items_affected": "ਪ੍ਰਭਾਵਿਤ ਚੀਜ਼ਾਂ",
        "of_invoice": "ਇਸ ਇਨਵੌਇਸ ਦਾ {pct}%",
        "item": "ਚੀਜ਼", "code": "ਟੈਰਿਫ਼ ਕੋਡ (tariff item)", "made_in": "ਕਿੱਥੇ ਬਣੀ", "rate": "ਦਰ",
        "value": "ਕੀਮਤ (CAD)", "extra": "ਵਾਧੂ ਖ਼ਰਚਾ", "confidence": "ਕਿੰਨਾ ਪੱਕਾ",
        "Verified": "ਪੁਸ਼ਟੀ ਹੋਈ", "Estimated": "ਅੰਦਾਜ਼ਾ", "Needs review": "ਜਾਂਚ ਲੋੜੀਂਦੀ",
        "affected": "ਪ੍ਰਭਾਵਿਤ", "at_risk": "ਜਾਂਚ ਲੋੜੀਂਦੀ", "not_affected": "ਪ੍ਰਭਾਵਿਤ ਨਹੀਂ",
        "checklist": "ਅੱਗੇ ਕੀ ਕਰਨਾ ਹੈ",
        "proof_of_origin": "{supplier} ਤੋਂ ਸਬੂਤ ਮੰਗੋ ਕਿ {n} ਚੀਜ਼(ਜ਼ਾਂ) ਕਿੱਥੇ ਬਣੀਆਂ ਸਨ।",
        "compare_suppliers": "ਆਪਣੀਆਂ ਸਭ ਤੋਂ ਮਹਿੰਗੀਆਂ ਚੀਜ਼ਾਂ ਲਈ ਅਮਰੀਕਾ ਤੋਂ ਬਾਹਰਲੇ ਸਪਲਾਇਰਾਂ ਤੋਂ ਰੇਟ ਲਓ।",
        "confirm_origin": "ਪਤਾ ਕਰੋ ਕਿ ਇਹ ਚੀਜ਼ਾਂ ਕਿੱਥੇ ਬਣੀਆਂ ਸਨ। ਸਰਟੈਕਸ (surtax) ਸਿਰਫ਼ ਅਮਰੀਕਾ ਵਿੱਚ ਬਣੀਆਂ ਚੀਜ਼ਾਂ ਉੱਤੇ ਲੱਗਦਾ ਹੈ।",
        "broker_review": "ਕਿਸੇ ਕਸਟਮ ਬ੍ਰੋਕਰ (customs broker) ਤੋਂ ਇਹਨਾਂ ਚੀਜ਼ਾਂ ਦੇ ਟੈਰਿਫ਼ ਕੋਡ ਦੀ ਪੁਸ਼ਟੀ ਕਰਵਾਓ।",
        "review_prices": "ਆਪਣੀਆਂ ਕੀਮਤਾਂ ਦੀ ਸਮੀਖਿਆ ਕਰੋ: ਜਵਾਬੀ ਟੈਰਿਫ਼ {amount} ਜੋੜਦੇ ਹਨ (ਇਸ ਇਨਵੌਇਸ ਦਾ {pct}%)।",
        "remission": "ਜੇ ਤੁਸੀਂ ਸਪਲਾਇਰ ਨਹੀਂ ਬਦਲ ਸਕਦੇ, ਤਾਂ ਬ੍ਰੋਕਰ ਤੋਂ ਕੈਨੇਡਾ ਦੇ ਟੈਰਿਫ਼ ਛੋਟ ਢਾਂਚੇ (remission framework) ਬਾਰੇ ਪੁੱਛੋ।",
        "support_programs": "ਸਰਕਾਰੀ ਮਦਦ ਦੇਖੋ, ਜਿਵੇਂ Regional Tariff Response Initiative ਅਤੇ BDC ਪ੍ਰੋਗਰਾਮ।",
        "in_transit": "ਜੋ ਮਾਲ 8 ਸਤੰਬਰ 2026 ਨੂੰ ਪਹਿਲਾਂ ਹੀ ਕੈਨੇਡਾ ਵੱਲ ਰਸਤੇ ਵਿੱਚ ਸੀ, ਉਸ ਉੱਤੇ ਸ਼ਾਇਦ ਸਰਟੈਕਸ ਨਾ ਲੱਗੇ। ਆਪਣੇ ਬ੍ਰੋਕਰ ਤੋਂ ਪੁੱਛੋ।",
        "sources": "ਸਰੋਤ",
        "disclaimer": "ਇਹ ਇੱਕ ਅੰਦਾਜ਼ਾ ਹੈ, ਕਾਨੂੰਨੀ ਜਾਂ ਕਸਟਮ ਸਲਾਹ ਨਹੀਂ। ਹਮੇਸ਼ਾਂ ਲਾਇਸੈਂਸਸ਼ੁਦਾ ਕਸਟਮ ਬ੍ਰੋਕਰ ਨਾਲ ਪੁਸ਼ਟੀ ਕਰੋ।",
        "mt_note": "ਮਸ਼ੀਨ ਅਨੁਵਾਦ। ਸਰਕਾਰੀ ਸ਼ਬਦ ਅੰਗਰੇਜ਼ੀ ਵਿੱਚ ਰੱਖੇ ਗਏ ਹਨ ਤਾਂ ਜੋ ਤੁਸੀਂ ਉਹਨਾਂ ਨੂੰ ਸਰਕਾਰੀ ਦਸਤਾਵੇਜ਼ਾਂ ਵਿੱਚ ਪਛਾਣ ਸਕੋ।",
        "rate_note": "ਦਰਾਂ ਦਾ ਸਰੋਤ: {list}। USD ਨੂੰ {fx} ਦੀ ਦਰ ਨਾਲ ਬਦਲਿਆ ({fx_note})। ਆਮ ਡਿਊਟੀ, GST, ਢੋਆ-ਢੁਆਈ ਅਤੇ ਬ੍ਰੋਕਰੇਜ ਸ਼ਾਮਲ ਨਹੀਂ।",
        "print": "ਪ੍ਰਿੰਟ ਕਰੋ ਜਾਂ PDF ਵਜੋਂ ਸੇਵ ਕਰੋ",
    },
    "zh": {
        "report_title": "关税影响报告",
        "invoice_total": "发票总额",
        "confirmed_extra": "反制关税带来的额外成本",
        "possible_extra": "可能的额外成本（需核实）",
        "items_affected": "受影响的商品",
        "of_invoice": "占本发票的 {pct}%",
        "item": "商品", "code": "税则号 (tariff item)", "made_in": "原产地", "rate": "税率",
        "value": "金额 (CAD)", "extra": "额外成本", "confidence": "可信度",
        "Verified": "已核实", "Estimated": "估算", "Needs review": "需核实",
        "affected": "受影响", "at_risk": "需核实", "not_affected": "不受影响",
        "checklist": "下一步行动",
        "proof_of_origin": "请向 {supplier} 索取 {n} 件商品的原产地证明。",
        "compare_suppliers": "为最贵的几种商品向美国以外的供应商询价。",
        "confirm_origin": "确认这些商品的生产地。附加税 (surtax) 只适用于在美国生产的商品。",
        "broker_review": "请报关行 (customs broker) 确认这些商品的税则号。",
        "review_prices": "检查您的售价：反制关税增加了 {amount}（占本发票的 {pct}%）。",
        "remission": "如果无法更换供应商，请向报关行咨询加拿大的关税减免框架 (remission framework)。",
        "support_programs": "了解政府支持措施，例如 Regional Tariff Response Initiative 和 BDC 计划。",
        "in_transit": "2026年9月8日已在运往加拿大途中的货物可能不需缴纳附加税。请咨询您的报关行。",
        "sources": "资料来源",
        "disclaimer": "此为估算，并非法律或海关建议。请务必向持牌报关行确认。",
        "mt_note": "机器翻译。官方术语保留英文，方便您在官方文件中识别。",
        "rate_note": "税率来源：{list}。美元按 {fx} 换算（{fx_note}）。不含常规关税、GST、运费和报关费。",
        "print": "打印或保存为 PDF",
    },
}


def t(lang, key, **vals):
    text = T.get(lang, T["en"]).get(key) or T["en"].get(key, key)
    try:
        return text.format(**vals)
    except (KeyError, IndexError):
        return text
