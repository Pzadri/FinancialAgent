/**
 * Mock data for demo mode.
 * All values are fictional and do not represent real financial information.
 */

// ── Créditos ──────────────────────────────────────────────────────────────────
export const mockCreditos = {
  cards: [
    {
      name: 'Visa Platinum',
      color: '#1da1f2',
      debt: 8450.00,
      creditLimit: 30000,
      usagePercent: 28,
      available: 21550,
      cutoffDate: '2026-06-05',
      paymentDate: '2026-06-20',
      minimumPayment: 420.00,
      fullPayment: 8450.00,
      daysUntilPayment: 27
    },
    {
      name: 'Mastercard Gold',
      color: '#f59e0b',
      debt: 3200.00,
      creditLimit: 15000,
      usagePercent: 21,
      available: 11800,
      cutoffDate: '2026-06-10',
      paymentDate: '2026-06-25',
      minimumPayment: 160.00,
      fullPayment: 3200.00,
      daysUntilPayment: 32
    },
    {
      name: 'Amex Blue',
      color: '#10b981',
      debt: 1750.00,
      creditLimit: 20000,
      usagePercent: 9,
      available: 18250,
      cutoffDate: '2026-06-15',
      paymentDate: '2026-06-30',
      minimumPayment: 87.50,
      fullPayment: 1750.00,
      daysUntilPayment: 37
    }
  ],
  summary: {
    totalCredit: 65000,
    totalDebt: 13400,
    totalAvailable: 51600,
    totalPayment: 13400,
    usagePercent: 21
  }
}

// ── Deudas ────────────────────────────────────────────────────────────────────
export const mockDeudas = {
  deudas: [
    {
      id: 1,
      name: 'Préstamo Auto',
      totalDebt: 85000,
      paymentAmount: 4250,
      frequency: 'mensual',
      frequencyLabel: 'Mensual',
      paymentsRemaining: 20,
      nextPaymentDate: '2026-06-01',
      daysUntilPayment: 8
    },
    {
      id: 2,
      name: 'Crédito Personal',
      totalDebt: 24000,
      paymentAmount: 1600,
      frequency: 'quincenal',
      frequencyLabel: 'Quincenal',
      paymentsRemaining: 15,
      nextPaymentDate: '2026-06-15',
      daysUntilPayment: 22
    }
  ],
  totalDebt: 109000
}

// ── Gastos / Ingresos ─────────────────────────────────────────────────────────
export const mockGIRecords = {
  records: [
    { id: 1,  date: '2026-05-24', description: 'Salario quincenal',       category: 'Sueldo',    amount:  22500 },
    { id: 2,  date: '2026-05-22', description: 'Renta departamento',      category: 'Vivienda',  amount: -9500  },
    { id: 3,  date: '2026-05-20', description: 'Proyecto freelance web',  category: 'Freelance', amount:  8000  },
    { id: 4,  date: '2026-05-18', description: 'Supermercado semanal',    category: 'Alimentos', amount: -1850  },
    { id: 5,  date: '2026-05-15', description: 'Salario quincenal',       category: 'Sueldo',    amount:  22500 },
    { id: 6,  date: '2026-05-14', description: 'Gasolina',                category: 'Transporte',amount: -950   },
    { id: 7,  date: '2026-05-12', description: 'Delivery comida',         category: 'Delivery',  amount:  3200  },
    { id: 8,  date: '2026-05-10', description: 'Restaurante',             category: 'Alimentos', amount: -680   },
    { id: 9,  date: '2026-05-08', description: 'Netflix + Spotify',       category: 'Otros',     amount: -320   },
    { id: 10, date: '2026-05-05', description: 'Pago tarjeta Visa',       category: 'Creditos',  amount: -8450  },
    { id: 11, date: '2026-04-30', description: 'Salario quincenal',       category: 'Sueldo',    amount:  22500 },
    { id: 12, date: '2026-04-28', description: 'Renta departamento',      category: 'Vivienda',  amount: -9500  },
    { id: 13, date: '2026-04-25', description: 'Proyecto freelance app',  category: 'Freelance', amount:  12000 },
    { id: 14, date: '2026-04-20', description: 'Supermercado',            category: 'Alimentos', amount: -2100  },
    { id: 15, date: '2026-04-15', description: 'Salario quincenal',       category: 'Sueldo',    amount:  22500 },
    { id: 16, date: '2026-04-12', description: 'Gasolina',                category: 'Transporte',amount: -900   },
    { id: 17, date: '2026-04-10', description: 'Delivery comida',         category: 'Delivery',  amount:  2800  },
    { id: 18, date: '2026-04-05', description: 'Pago tarjeta MC',         category: 'Creditos',  amount: -3200  },
    { id: 19, date: '2026-03-31', description: 'Salario quincenal',       category: 'Sueldo',    amount:  22500 },
    { id: 20, date: '2026-03-28', description: 'Renta departamento',      category: 'Vivienda',  amount: -9500  },
    { id: 21, date: '2026-03-25', description: 'Proyecto freelance',      category: 'Freelance', amount:  6500  },
    { id: 22, date: '2026-03-20', description: 'Supermercado',            category: 'Alimentos', amount: -1950  },
    { id: 23, date: '2026-03-15', description: 'Salario quincenal',       category: 'Sueldo',    amount:  22500 },
    { id: 24, date: '2026-03-10', description: 'Gasolina',                category: 'Transporte',amount: -870   },
    { id: 25, date: '2026-02-28', description: 'Salario quincenal',       category: 'Sueldo',    amount:  22500 },
    { id: 26, date: '2026-02-25', description: 'Renta departamento',      category: 'Vivienda',  amount: -9500  },
    { id: 27, date: '2026-02-20', description: 'Proyecto freelance',      category: 'Freelance', amount:  9000  },
    { id: 28, date: '2026-02-15', description: 'Salario quincenal',       category: 'Sueldo',    amount:  22500 },
    { id: 29, date: '2026-01-31', description: 'Salario quincenal',       category: 'Sueldo',    amount:  22500 },
    { id: 30, date: '2026-01-15', description: 'Salario quincenal',       category: 'Sueldo',    amount:  22500 }
  ]
}

// ── Inversiones ───────────────────────────────────────────────────────────────
export const mockInversiones = {
  ahorro: [
    {
      name: 'Revolut',
      description: 'Cuenta de ahorro digital',
      color: '#1da1f2',
      balance: 45000,
      annualRate: 9.5,
      dailyGain: 11.71
    },
    {
      name: 'Cajita Nu',
      description: 'Cuenta Nu rendimientos diarios',
      color: '#8b5cf6',
      balance: 32000,
      annualRate: 11.0,
      dailyGain: 9.64
    },
    {
      name: 'Didi',
      description: 'Ahorro compartido',
      color: '#f59e0b',
      balance: 18500,
      annualRate: 8.0,
      dailyGain: 4.05
    }
  ],
  prestamos: [
    {
      id: 1,
      principal: 20000,
      rate: 15,
      term: '12 meses',
      expectedInterest: 3000,
      totalReturn: 23000,
      status: 'active',
      statusLabel: 'Activo'
    },
    {
      id: 2,
      principal: 10000,
      rate: 12,
      term: '6 meses',
      expectedInterest: 600,
      totalReturn: 10600,
      status: 'active',
      statusLabel: 'Activo'
    }
  ],
  afore: {
    balance: 128000,
    annualReturn: 7.5,
    bimonthlyContribution: 3200,
    voluntaryContribution: 500
  },
  summary: {
    totalSavings: 95500,
    totalLoans: 30000,
    totalLoanInterest: 3600,
    avgLoanRate: 13.5
  }
}

// ── GBM Portfolio ─────────────────────────────────────────────────────────────
export const mockGBM = {
  nacional: [
    { ticker: 'VWCE',  shares: 12,   avgCost: 1850.00, marketPrice: 2120.50, marketValue: 25446,  gainLoss: 3246,  returnPct: 14.57 },
    { ticker: 'FUNO11',shares: 200,  avgCost: 28.50,   marketPrice: 31.20,   marketValue: 6240,   gainLoss: 540,   returnPct: 9.47  },
    { ticker: 'BSMXB', shares: 500,  avgCost: 42.10,   marketPrice: 45.80,   marketValue: 22900,  gainLoss: 1850,  returnPct: 8.79  },
    { ticker: 'CEMEX', shares: 300,  avgCost: 11.20,   marketPrice: 10.50,   marketValue: 3150,   gainLoss: -210,  returnPct: -6.25 }
  ],
  usa: [
    { ticker: 'VOO',   shares: 0.85, avgCost: 420.00,  marketPrice: 498.30,  marketValue: 423.55, gainLoss: 66.55, returnPct: 18.65 },
    { ticker: 'QQQ',   shares: 0.50, avgCost: 380.00,  marketPrice: 445.20,  marketValue: 222.60, gainLoss: 32.60, returnPct: 17.16 },
    { ticker: 'NVDA',  shares: 0.30, avgCost: 550.00,  marketPrice: 875.40,  marketValue: 262.62, gainLoss: 97.62, returnPct: 59.16 }
  ],
  summary: {
    nacionalValueMXN: 57736,
    usaValueUSD: 908.77,
    usaValueMXN: 16357.86,
    totalValueMXN: 74093.86,
    totalGainMXN: 5672.86,
    totalReturnPct: 8.29,
    usdMxnRate: 18.00
  }
}

// ── Telegram ──────────────────────────────────────────────────────────────────
export const mockTelegramStatus = {
  connected: true,
  chat_id: '123456789',
  bot_username: 'financial_demo_bot'
}

// ── Update status ─────────────────────────────────────────────────────────────
export const mockUpdateStatus = {
  needsUpdate: false,
  lastUpdate: '24 may 2026',
  isMonday: false,
  daysSinceUpdate: 0
}
