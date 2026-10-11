export interface MatrixPayload {
  period: { start_date: string; end_date: string | null }
  sessions: { id: string; date: string; total_money: number }[]
  participants_by_session: Record<string, {
    user_telegram_id: string
    user_name: string | null
    additional_participants: number
  }[]>
  shuttlecock_total: number
  shuttlecock_tubes: number
  additional_costs: {
    id: string
    name: string
    total_amount: number
    total_weight: number
  }[]
  additional_cost_participants_by_cost: Record<string, {
    user_telegram_id: string
    user_name: string | null
    full_name: string | null
    weight: number
  }[]>
  total_period_money: number
  personal_report: {
    person_id: string
    telegram_user_name: string
    full_name: string | null
    period_money: number
  }[]
  users: {
    telegram_id: string
    telegram_user_name: string | null
    full_name: string | null
  }[]
}

