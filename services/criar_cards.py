def card_html(titulo, valor, cor):
    return f"""
    <div style="padding:20px; border-radius:10px; background-color:{cor}; color:white; text-align:center; font-weight:bold;">
        <div style="font-size:18px;">{titulo}</div>
        <div style="font-size:24px;">R$ {valor:,.2f}</div>
    </div>
    """