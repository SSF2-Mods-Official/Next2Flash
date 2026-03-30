package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class NSpecBombThrown_156 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var projectile:*;
        public var level:*;
        public var character:*;

        public function NSpecBombThrown_156()
        {
            super();
            addFrameScript(0, this.frame1, 7, this.frame8, 8, this.frame9, 15, this.frame16, 16, this.frame17, 23, this.frame24, 24, this.frame25, 32, this.frame33);
        }

        public function toContinue(_arg_1:*):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toContinue);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toContinue);
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
            this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.toContinue);
            this.self.stancePlayFrame("continue");
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.projectile = this.self;
            this.level = 1;
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
                this.self.faceRight();
                this.self.updateAttackBoxStats(1, {"priority":2});
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toContinue);
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.toContinue);
            };
        }

        internal function frame8():*
        {
            this.self.stancePlayFrame("level1");
        }

        internal function frame9():*
        {
            this.self.updateAttackBoxStats(1, {"priority":4});
            this.level = 2;
        }

        internal function frame16():*
        {
            this.self.stancePlayFrame("level2");
        }

        internal function frame17():*
        {
            this.level = 3;
            this.self.updateAttackBoxStats(1, {"priority":5});
        }

        internal function frame24():*
        {
            this.self.stancePlayFrame("level3");
        }

        internal function frame25():*
        {
            if (this.level == 1)
            {
                this.self.attachEffect("effect_explosion");
                SSF2API.getCamera().shake(3);
            }
            else if (this.level == 2)
            {
                this.self.attachEffect("effect_explosion", {
                    "scaleX":1.37,
                    "scaleY":1.37
                });
                SSF2API.getCamera().shake(6);
            }
            else if (this.level == 3)
            {
                this.self.attachEffect("effect_explosion", {
                    "scaleX":1.81,
                    "scaleY":1.81
                });
                SSF2API.getCamera().shake(10);
            };
            SSF2API.playSound("bomberman_explode");
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
        }

        internal function frame33():*
        {
            this.self.stancePlayFrame("end");
        }


    }
}

