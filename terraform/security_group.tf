resource "aws_security_group" "eb-security-group" {
  name        = "eb-security-group"
  description = "security group for eb instances"
}

resource "aws_security_group" "db-security-group" {
  name        = "db"
  description = "security group for database"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "aws_security_group_id" {
  value = aws_security_group.eb-security-group.id
}

resource "aws_security_group_rule" "eb-db-access" {
  security_group_id        = aws_security_group.db-security-group.id
  type                     = "ingress"
  description              = "Access given to the security group applied to all EB instances"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.eb-security-group.id
}

resource "aws_security_group_rule" "aspen-batch-db-access" {
  security_group_id        = aws_security_group.db-security-group.id
  type                     = "ingress"
  description              = "Access given to instances in the aspen batch pipeline."
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.aspen-batch-security-group.id
}

resource "aws_security_group_rule" "remote-db-access-ttung" {
  count             = var.DEPLOYMENT_ENVIRONMENT == "prod" ? 0 : 1
  security_group_id = aws_security_group.db-security-group.id
  type              = "ingress"
  description       = "ttung"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  cidr_blocks       = ["24.4.203.80/32"]
}

resource "aws_security_group_rule" "remote-db-access-phoenix" {
  count             = var.DEPLOYMENT_ENVIRONMENT == "prod" ? 0 : 1
  security_group_id = aws_security_group.db-security-group.id
  type              = "ingress"
  description       = "phoenix"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  cidr_blocks       = ["24.6.0.151/32"]
}

resource "aws_security_group_rule" "remote-db-access-shannon" {
  count             = var.DEPLOYMENT_ENVIRONMENT == "prod" ? 0 : 1
  security_group_id = aws_security_group.db-security-group.id
  type              = "ingress"
  description       = "shannon"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  cidr_blocks       = ["73.162.199.26/32"]
}
