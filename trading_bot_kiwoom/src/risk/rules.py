class RiskRules:
    def __init__(self, max_positions=6, daily_loss_limit=0.015, cooldown_after_losses=3):
        self.max_positions=max_positions
        self.daily_loss_limit=daily_loss_limit
        self.cooldown_after_losses=cooldown_after_losses
