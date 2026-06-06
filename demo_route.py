
# ─── DEMO ROUTE ───────────────────────────────────────────────────────────────
# Paste this block into app.py just ABOVE the line: if __name__ == '__main__':

@app.route('/demo')
def demo_login():
    """Auto-login with a demo account — no registration needed."""
    DEMO_EMAIL = 'demo@wealthlens.mx'
    DEMO_PASSWORD = 'WealthLens2026!'
    DEMO_NAME = 'Demo User'

    db = get_db()

    # Create demo user if they don't exist
    existing = db.execute("SELECT * FROM users WHERE email=?", (DEMO_EMAIL,)).fetchone()
    if not existing:
        db.execute(
            "INSERT INTO users (email, password_hash, name, lang, currency) VALUES (?, ?, ?, ?, ?)",
            (DEMO_EMAIL, generate_password_hash(DEMO_PASSWORD), DEMO_NAME, 'en', 'MXN')
        )
        db.commit()
        # Re-fetch after insert
        existing = db.execute("SELECT * FROM users WHERE email=?", (DEMO_EMAIL,)).fetchone()

    # Seed demo data if no assets yet
    asset_count = db.execute("SELECT COUNT(*) as c FROM assets WHERE user_id=?", (existing['id'],)).fetchone()['c']
    if asset_count == 0:
        demo_assets = [
            (existing['id'], 'CEDE Banregio 28d', 'cede', 150000, 'MXN', '12.10% GAT'),
            (existing['id'], 'AMXL.MX — América Móvil', 'stock', 85000, 'MXN', '340 acciones'),
            (existing['id'], 'Bitcoin (BTC)', 'crypto', 62000, 'MXN', '0.035 BTC'),
            (existing['id'], 'Ethereum (ETH)', 'crypto', 28000, 'MXN', '0.5 ETH'),
            (existing['id'], 'FIBRA UNO (FUNO11)', 'fibra', 45000, 'MXN', '1,500 certificados'),
            (existing['id'], 'Fondo de Emergencia', 'cash', 30000, 'MXN', '3 meses gastos'),
        ]
        db.executemany(
            "INSERT INTO assets (user_id, name, type, value_mxn, currency, note) VALUES (?,?,?,?,?,?)",
            demo_assets
        )

        demo_goals = [
            (existing['id'], 'Fondo de Retiro', 'Retirement Fund', 2000000, 420000, '2045-12-31', 1, '#1D9E75'),
            (existing['id'], 'Viaje a Japón', 'Trip to Japan', 80000, 35000, '2026-12-31', 2, '#378ADD'),
            (existing['id'], 'Enganche Casa', 'House Down Payment', 500000, 150000, '2028-06-30', 1, '#EF9F27'),
        ]
        db.executemany(
            "INSERT INTO goals (user_id, name, name_es, target_mxn, saved_mxn, deadline, priority, color) VALUES (?,?,?,?,?,?,?,?)",
            demo_goals
        )

        import random
        categories = ['groceries', 'dining', 'transport', 'utilities', 'entertainment', 'health', 'shopping']
        amounts_expense = [-3200, -1800, -950, -2100, -650, -480, -1200, -890, -2400, -760]
        amounts_income = [28000, 28000, 5000, 28000, 28000, 3500]
        demo_transactions = []
        for i in range(6):
            demo_transactions.append((
                existing['id'],
                f'2026-0{i+1}-05',
                'Nómina mensual',
                amounts_income[i],
                'income', 'manual', 'BBVA'
            ))
        for i in range(20):
            month = (i % 6) + 1
            demo_transactions.append((
                existing['id'],
                f'2026-0{month}-{10 + (i % 15)}',
                f'Gasto {categories[i % len(categories)]}',
                amounts_expense[i % len(amounts_expense)],
                categories[i % len(categories)], 'manual', 'BBVA'
            ))
        db.executemany(
            "INSERT INTO transactions (user_id, date, description, amount, category, source, account) VALUES (?,?,?,?,?,?,?)",
            demo_transactions
        )
        db.commit()

    # Log in as demo user
    session['user_id'] = existing['id']
    session['lang'] = 'en'
    return redirect(url_for('dashboard'))
